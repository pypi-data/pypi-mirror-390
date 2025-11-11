"""In this submodule you can find all analyzers, so "audio processors" with one or multiple inputs."""
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, Tuple

import numpy as np
import pyfftw

from .acore import AAnalyzer, AAnalyzerBuf
from .exceptions import UnitError
from .io import IInput, Input
from .processor import Analyzer

if TYPE_CHECKING:
    from soundfile import SoundFile

    from .afile import AFile
    from .interface import Interface
    from .io import IOutput
    from .typing import Avg, AWindow, AWindowArg, FFTAbs, FFTFreqs, FFTInput, FFTOutput


class Recorder(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 afile: "AFile|SoundFile") -> None:
        """The Recorder class analyzer is used to record audio to a given file.
        It is a multi input analyzer, with the input count extracted from the given AFile.
        Input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            afile: Reference to an AFile instance.

        Raises:
            ValueError: The given AFile was not opened.
        """
        # check afile is open and reset
        self._afile = afile
        if afile.closed:
            raise ValueError("The given AFile was not opened.")
        afile.flush()
        afile.seek(0)

        self._arecorder = self._ARecorder(afile, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._arecorder,
                         interface=interface,
                         inputs=tuple(Input(self) for i in range(afile.channels)),
                         in_update=False)

    class _ARecorder(AAnalyzer):
        def __init__(self,
                     afile: "AFile|SoundFile",
                     blocksize: int,
                     start_frame: int) -> None:
            self._afile = afile
            super().__init__(in_buffer=True,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _process_in_buf(self) -> None:
            self._afile.write(self._in_buf)

        def _reset(self) -> None:
            self._afile.flush()
            self._afile.seek(0)


class Oscilloscope(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 xpos: int = 2000,
                 ythreshold: float = 0,
                 mode: Literal["rising_edge", "falling_edge", "both"] = "rising_edge",
                 buffersize: int = 4000) -> None:
        """The Oscilloscope class analyzer is used to store a signal buffer, positioned by a trigger.
        It is a multi input analyzer, with input(0) used for triggering.
        Input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            xpos: x-position of trigger (in the buffer).
            ythreshold: Trigger threshold.
            mode: The trigger mode.
            buffersize: The size of the oscilloscope buffer.

        Raises:
            ValueError: Given trigger unknown.
        """
        match mode:
            case "falling_edge":
                imode = 0
            case "rising_edge":
                imode = 1
            case "both":
                imode = 2
            case _:
                raise ValueError("Given trigger unknown.")
        self._aosciloscope = self._AOscilloscope(xpos, ythreshold, imode, buffersize,
                                                 interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._aosciloscope,
                         interface=interface,
                         inputs=(Input(self), ),
                         in_update=True)

    def get_buffer(self, block: bool = True, timeout: float = 2) -> "FFTInput | Literal[False]":
        """On trigger, get one full buffer from the queue filled by the audio backend.

        Args:
            block: Determines if the call should block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            Buffer array or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._aosciloscope.buf_queue.empty():
            return self._aosciloscope.buf_queue.get(timeout=timeout)
        return False

    class _AOscilloscope(AAnalyzerBuf):
        def __init__(self,
                     xpos: int,
                     ythreshold: float,
                     mode: int,
                     bufsize: int,
                     blocksize: int,
                     start_frame: int) -> None:
            # trigger = 0: falling edge
            #         = 1: rising edger
            #         = 2: both edge
            self._mode = mode
            self._xpos = xpos
            self._ythreshold = ythreshold
            self._triggered = False
            self._trigger_ch = 0
            super().__init__(bufsize=bufsize,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _process_in_buf(self) -> None:
            # if triggered, fill buffer and return when full
            # finally reset trigger
            if self._triggered:
                self._in_buf_idx += self._blocksize
                if self._in_buf_idx >= self._bufsize:
                    # put the buffer into queue
                    if not self.buf_queue.full():
                        self.buf_queue.put(self._in_buf[:self._bufsize].copy())
                    # handle the overflow (rest)
                    rest = self._in_buf_idx - self._bufsize
                    if rest > 0:
                        self._in_buf[:rest, :] = self._in_buf[self._bufsize:self._in_buf_idx]
                    self._in_buf_idx = rest
                    self._triggered = False
                return
            if self._in_buf_idx >= self._xpos:
                # search for trigger in the buffer
                tpos = self._search_trigger(self._ythreshold, self._xpos, self._in_buf_idx+self._blocksize)
                if tpos:
                    # roll buffer back to xpos
                    dx = tpos - self._xpos
                    self._in_buf[:-dx, :] = self._in_buf[dx:, :]
                    self._triggered = True
                    self._in_buf_idx += self._blocksize - dx
                else:
                    # roll buffer back by one block
                    self._in_buf[:-self._blocksize, :] = self._in_buf[self._blocksize:, :]
                return
            # if not triggered and not rolling fill buf
            self._in_buf_idx += self._blocksize

        def _search_trigger(self, t: float, lower: int, upper: int) -> int:
            # search _in_buf trigger in the range lower:upper on self._trigger_ch
            # returns absolute trigger position (always > lower)
            # or False if not trigger was found
            a = self._in_buf[lower:upper, self._trigger_ch]
            a0 = a[:-1]
            a1 = a[1:]
            match self._mode:
                case 0:  # falling edge
                    trigger = np.where((a0 > t) & (a1 <= t))[0]
                case 1:  # rising edge
                    trigger = np.where((a0 < t) & (a1 >= t))[0]
                case 2:  # both
                    trigger = np.where(((a0 < t) & (a1 >= t)) | (a0 > t) & (a1 <= t))[0]
                case _:
                    raise ValueError("Unknown trigger mode.")
            if trigger.size > 0:
                return int(lower + trigger[0] + 1)
            return False

        def _reset(self) -> None:
            self._triggered = False


class Vector(Analyzer):
    def __init__(self, interface: "Interface", samples: int) -> None:

        self._avector = AAnalyzerBuf(samples, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._avector,
                         interface=interface,
                         inputs=(Input(self), ),
                         in_update=True)

    def get_buffer(self, block: bool = True, timeout: float = 2) -> "FFTInput | Literal[False]":
        """Get one full buffer from the queue filled by the audio backend.

        Args:
            block: Determines if the call should block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            Buffer array or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._avector.buf_queue.empty():
            return self._avector.buf_queue.get(timeout=timeout)
        return False


class FFT(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 win: Optional["AWindowArg"] = None) -> None:
        """Compute FFT of input signals.
        Computations are phase-accurate, and can be done for windowsizes multiple of blocksize.
        It is a multi input analyzer and input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            win: Windowing function vector, also determines FFT size.
                Defaults to FFT.std_fft_window().

        Raises:
            ValueError: When windowsize is not a multiple of blocksize.
        """
        if win is None:
            win = self.std_fft_window(interface)
        if win.size < interface.blocksize:
            raise ValueError("Window size must be larger than blocksize.")
        self._win: "AWindow" = win.astype(np.float32)
        self._tiledwin: "FFTInput"
        self._winsize = int(win.size)
        assert self._winsize % 2 == 0, "Window length must be even to ensure correct scaling."
        self._rms_win = np.sqrt(np.mean(self._win**2))
        self._peak_win = np.mean(self._win)

        self._indata_fftw: "FFTInput"
        self._rfft: "FFTOutput"
        self._fftw: "pyfftw.FFTW"
        self._scale_c64 = np.complex64(1 / self._winsize)
        self._scale_f32 = np.float32(1 / self._winsize)

        self._fs = np.fft.rfftfreq(self._winsize, 1/interface.samplerate).astype(np.float32)
        self._fft: "FFTOutput"
        self._tmp: "FFTAbs"
        self._avg: "Avg"

        self._afft = AAnalyzerBuf(win.size, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._afft,
                         interface=interface,
                         inputs=(Input(self), ),
                         in_update=True)

    @property
    def frequencies(self) -> "FFTFreqs":
        """The corresponding frequency vector of the FFT."""
        return self._fs

    @property
    def rfft(self) -> "FFTOutput":
        """The rfft vector set by get_rfft()."""
        return self._rfft

    def update_acore(self) -> None:
        self._indata_fftw = pyfftw.empty_aligned((self._winsize, len(self._inputs)), dtype=np.float32)
        self._rfft = pyfftw.empty_aligned((int(self._winsize / 2 + 1), len(self._inputs)), dtype=np.complex64)
        # the FFTW_ESTIMATE flags skips the tests and relys on heuristics
        # much faster connections, benchmarking did not show a slower fft.
        self._fftw = pyfftw.FFTW(self._indata_fftw,
                                 self._rfft,
                                 axes=(0, ),
                                 flags=('FFTW_ESTIMATE', ))
        self._fft = np.zeros((int(self._winsize / 2 + 1), len(self._inputs)), dtype=np.complex64)
        self._tiledwin = np.tile(self._win[:, None], (1, len(self._inputs)))
        self._tmp = np.zeros((int(self._winsize / 2 + 1), len(self._inputs)), dtype=np.float32)
        self._avg = np.zeros(len(self._inputs), dtype=np.float32)
        return super().update_acore()

    def std_fft_window(self, interface: "Interface") -> "AWindow":
        """
        Returns:
            The standard window function: Hann window with length of interface's samplerate.
            This results in 1Hz frequency bins.
        """
        return np.hanning(interface.samplerate)

    def get_rfft(self, block: bool = True, timeout: float = 2) -> "FFTOutput | Literal[False]":
        """Get the computation result from the queue filled by the audio backend, appyl given window to indata,
        and compute raw (unscaled) rfft, store it in self.rfft and return its reference.

        Args:
            block: Determines if the call should block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            FFT array or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._afft.buf_queue.empty():
            self._indata_fftw[:] = self._afft.buf_queue.get(timeout=timeout)
            self._indata_fftw *= self._tiledwin
            self._fftw.execute()
            return self._rfft
        return False

    def rfft2fft(self, rfft: "FFTOutput") -> "FFTOutput":
        """Compute the correctly peak compensated fft from the rfft.

        Args:
            rfft: Reference to the raw (unscaled) rfft result.

        Returns:
            The fft.
        """
        self._fft[:] = rfft
        # scale for windowsize
        self._fft *= self._scale_c64
        # scale rfft because of symmetry, also see numpy docs
        self._fft[1:-1] *= 2
        # compensate window scaling, for correct peak values
        self._fft /= self._peak_win
        return self._fft

    def rfft2ps(self, rfft: "FFTOutput") -> "FFTAbs":
        """Compute the correctly power compensated power spectrum from the rfft.

        Args:
            rfft: Reference to the raw (unscaled) rfft result.

        Returns:
            The power spectrum.
        """
        np.abs(rfft, out=self._tmp)
        # scale for windowsize
        self._tmp *= self._scale_f32
        # square
        self._tmp = self._tmp**2
        # scale rfft because of symmetry, also see numpy docs
        self._tmp[1:-1] *= 2
        # compensate window scaling, for correct rms values
        self._tmp /= self._rms_win**2
        return self._tmp

    def rfft2psd(self, rfft: "FFTOutput") -> "FFTAbs":
        """Compute the correctly power compensated power spectrum density from the rfft.

        Args:
            rfft: Reference to the raw (unscaled) rfft result.

        Returns:
            The power spectrum density.
        """
        self.rfft2ps(rfft)
        self._tmp /= self._fs[1]
        return self._tmp

    def rfft2rms(self, rfft: "FFTOutput") -> "Avg":
        """Get the RMS average value from the rfft.

        Args:
            rfft: Reference to the raw (unscaled) rfft result.

        Returns:
            Array of RMS average value per channel.
        """
        self.rfft2ps(rfft)
        np.sum(self._tmp, axis=0, out=self._avg)
        np.sqrt(self._avg, out=self._avg)
        return self._avg

    def rfft2peak(self, rfft: "FFTOutput") -> Tuple["Avg", "Avg"]:
        """Get the peak frequency and value from the rfft.

        Args:
            rfft: Reference to the raw (unscaled) rfft result.

        Returns:
           Array of peak frequencies and values per channel.
        """
        self.rfft2fft(rfft)
        np.abs(self._fft, out=self._tmp)
        ipeak = np.argmax(self._tmp, axis=0)
        self._avg = self._tmp[ipeak, np.arange(self._fft.shape[1])]
        return self._fs[ipeak], self._avg


class RMS(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 samples: int) -> None:
        """Compute the RMS average of incomming audio data.
        It is a multi input analyzer and input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            samples: Number of samples used in the RMS average.
        """

        self._armsavg = AAnalyzerBuf(samples, interface.blocksize, interface.start_frame)
        super().__init__(self._armsavg,
                         interface,
                         inputs=(Input(self), ),
                         in_update=True)

    def get_rms(self, block: bool = True, timeout: float = 2) -> "Avg | Literal[False]":
        """Get the RMS average value from the queue filled by the audio backend.

        Args:
            block: Decides if the call oshould block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            Array of RMS average value per channel or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._armsavg.buf_queue.empty():
            return np.sqrt(np.mean(self._armsavg.buf_queue.get(timeout=timeout)**2,
                                   axis=0,
                                   dtype=np.float32), dtype=np.float32)
        return False


class CalIInput(FFT):
    def __init__(self,
                 interface: "Interface",
                 actual: float,
                 unit: Literal["VRms", "Vp", "PaRms", "Pap", "SPL", "ARms", "Ap"],
                 win: Optional["AWindowArg"] = None,
                 averages: int = 10,
                 mode: Literal["peak", "rms"] = "rms",
                 iinput: Optional["IInput"] = None,
                 gain: float = 0) -> None:
        """The CalcIInput class analyzer is used to calibrate the connected interface IInput.
        It is a single input analyzer, therefore input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            actual: The actual value of the signal used for calibration.
            unit: The unit of the value given

                - `"VRms"`   : RMS value of the sinusoidal signal in Volt.
                - `"Vp"`   : Amplitude value of the sinusoidal signal in Volt.
                - `"PaRms"`  : RMS value of the sinusoidal signal in Pascal.
                - `"Pap"`  : Amplitude value of the sinusoidal signal in Pascal.
                - `"ARms"`  : RMS value of the sinusoidal signal in m/s^2.
                - `"Aap"`  : Amplitude value of the sinusoidal signal in m/s^2.
                - `"SPL"` : Sound Pressure Level (RMS pressure in Dezibel).

            win: The windowing function used for the FFT.
                Defaults to FFT.std_fft_window().
            averages: Number of samples averages.
            mode: Depending on the mode the rms average of the fft or just the fft peak is used.
            iinput: The IInput to save the calibration to.
                If None, the connected IInput is used.
            gain: Gain setting of the interface. This is not used for the calculation, but stored in the IInput.
        """
        self._actual = actual
        self._unit = unit

        self._averages = averages
        self._n: int = 0  # counter used for averages
        self._c: float = 0
        self._f: float = 0

        self._mode = mode
        self._gain = gain
        self._iinput = iinput

        super().__init__(interface=interface,
                         win=win)
        # FFT usually supports in_update, but in our case we only want a single input!
        self.in_update = False

    @property
    def actual(self) -> float:
        return self._actual

    def evaluate(self,
                 block: bool = True,
                 timeout: float = 2,
                 save: bool = True) -> Tuple[float, float] | Literal[False]:
        """If the measurement is finished, this evaluates the result and returns True.
        If the measurement is still running and block is False, False is returned.

        Args:
            block: Decides if the call should block.
            timeout: The timeout after which False is returned.
            save: Decides if the results should be saved to the connected or given IInput.

        Returns:
            (Frequency, Calibration Factor), when everything was successful.
            `False`, when the measurement is not done yet.

        Raises:
            UnitError: Given unit is unknown.
            ValueError: Given mode is unknown.
        """
        # get iinput if not given
        if self._iinput is None:
            assert isinstance(self.inputs[0].connected_output, IInput)
            self._iinput = self.inputs[0].connected_output

        # get fft spectrum
        rfft = self.get_rfft(block, timeout)
        if rfft is False:
            return rfft

        # ectract value
        match self._mode:
            case "peak":
                freqs, measured_peaks = self.rfft2peak(rfft)
            case "rms":
                freqs, _ = self.rfft2peak(rfft)
                measured_peaks = self.rfft2rms(rfft) * np.sqrt(2)
            case _:
                raise ValueError("Given mode is unknown.")

        freq = float(freqs[0])
        measured_peak = float(np.abs(measured_peaks[0]))

        # calculate the rms of the cal signal
        match self._unit:
            case "VRms" | "PaRms" | "ARms":
                peak = self._actual * np.sqrt(2)
            case "Vp" | "Pap" | "Ap":
                peak = self._actual
            case "SPL":
                peak = 2e-5 * 10 ** (self._actual / 20) * np.sqrt(2)
            case _:
                raise ValueError("Given unit is unknown.")

        # calculate calibration factor and frquency
        self._c += peak / measured_peak
        self._f += freq
        self._n += 1

        # check averages
        if self._n < self._averages:
            return False

        # average and reset
        c = self._c / self._n
        f = self._f / self._n
        self._n = 0
        self._c = 0
        self._f = 0

        # write to IInput
        now = datetime.now()
        if save and self._iinput is not None:
            self._iinput.gain = self._gain
            match self._unit:
                case "VRms" | "Vp":
                    self._iinput.cV = c
                    self._iinput.fV = f
                    self._iinput.dateV = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case "PaRms" | "Pap" | "SPL":
                    self._iinput.cPa = c
                    self._iinput.fPa = f
                    self._iinput.datePa = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case "ARms" | "Ap":
                    self._iinput.cA = c
                    self._iinput.fA = f
                    self._iinput.dateA = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case _:
                    raise UnitError("Given unit is unknown.")
        return (f, c)


class CalIOutput(FFT):
    def __init__(self,
                 interface: "Interface",
                 value: float,
                 quantity: Literal["V", "Pa", "A"],
                 ioutput: "IOutput",
                 win: Optional["AWindowArg"] = None,
                 averages: int = 10,
                 mode: Literal["peak", "rms"] = "rms",
                 iinput: Optional["IInput"] = None,
                 gain: float = 0) -> None:
        """The CalcIOutput class analyzer is used to calibrate the given IOutput.
        For this calibration procedure a Sine generator with an amplitude of "actual"
        has to be connected to the given IOutput.
        This IOutput must be physically connected to the IInput, which needs to be pre-calibrated,
        and this IInput must be connected to this analyzer.
        It is a single input analyzer, therefore input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            value: The peak amplitude value of the signal used for calibration in arbitrary units.
            quantity: The physical quantity to calibrate for.

                - `"V"`   : Calibrate the ioutput in Volt.
                - `"Pa"`  : Calibrate the ioutput in Pascal.
                - `"Pa"`  : Calibrate the ioutput in m/s^2.

            ioutput: The IOutput to calibrate, used to generate the signal and connected to the IInput.
            win: The windowing function used for the FFT.
                Defaults to FFT.std_fft_window().
            averages: Number of samples averages.
            mode: Depending on the mode the rms average of the fft or just the fft peak is used.
            iinput: The IInput to save the calibration to.
                If None, the connected IInput is used.
            gain: Gain setting of the interface. This is not used for the calculation, but stored in the IInput.

        Raises:
            ValueError: Given mode is unknown.
            UnitError: Given quantity is unknown.
        """
        self._value = value
        self._quantity = quantity
        self._ioutput = ioutput

        self._averages = averages
        self._n: int = 0  # counter used for averages
        self._c: float = 0
        self._f: float = 0

        self._mode = mode
        self._gain = gain
        self._iinput = iinput

        super().__init__(interface=interface,
                         win=win)
        # FFT usually supports in_update, but in our case we only want a single input!
        self.in_update = False

    def evaluate(self,
                 block: bool = True,
                 timeout: float = 2,
                 save: bool = True) -> Tuple[float, float] | Literal[False]:
        """If the measurement is finished, this evaluates the result and returns True.
        If the measurement is still running and block is False, False is returned.

        Args:
            block: Decides if the call should block.
            timeout: The timeout after which False is returned.
            save: Decides if the results should be saved to the connected or given IInput.

        Returns:
            (Frequency, Calibration Factor), when everything was successful.
            `False`, when the measurement is not done yet.

        Raises:
            UnitError: Given unit is unknown.
            UnitError: Given quantity is unknown.
            ValueError: Given mode is unknown.
        """
        # get iinput if not given
        if self._iinput is None:
            assert isinstance(self.inputs[0].connected_output, IInput)
            self._iinput = self.inputs[0].connected_output

        # get fft spectrum
        rfft = self.get_rfft(block, timeout)
        if rfft is False:
            return rfft

        # ectract value
        match self._mode:
            case "peak":
                freqs, measured_peaks = self.rfft2peak(rfft)
            case "rms":
                freqs, _ = self.rfft2peak(rfft)
                measured_peaks = self.rfft2rms(rfft) * np.sqrt(2)
            case _:
                raise ValueError("Given mode is unknown.")

        freq = float(freqs[0])
        measured_peak = float(np.abs(measured_peaks[0]))

        # calculate the rms of the cal signal
        match self._quantity:
            case "V":
                assert self._iinput.cV is not None, "Given IInput must be calibrated for voltage first."
                actual = measured_peak * self._iinput.cV
            case "Pa":
                assert self._iinput.cPa is not None, "Given IInput must be calibrated for pressure first."
                actual = measured_peak * self._iinput.cPa
            case "A":
                assert self._iinput.cA is not None, "Given IInput must be calibrated for acceleration first."
                actual = measured_peak * self._iinput.cA
            case _:
                raise UnitError("Given unit is unknown.")

        # calculate calibration factor and frquency
        self._c += actual / self._value
        self._f += freq
        self._n += 1

        # check averages
        if self._n < self._averages:
            return False

        # average and reset
        c = self._c / self._n
        f = self._f / self._n
        self._n = 0
        self._c = 0
        self._f = 0

        # write to IOutput
        now = datetime.now()
        if save:
            self._ioutput.gain = self._gain
            match self._quantity:
                case "V":
                    self._ioutput.cV = c
                    self._ioutput.fV = f
                    self._ioutput.dateV = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case "Pa":
                    self._ioutput.cPa = c
                    self._ioutput.fPa = f
                    self._ioutput.datePa = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case "A":
                    self._ioutput.cA = c
                    self._ioutput.fA = f
                    self._ioutput.dateA = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
                case _:
                    raise UnitError("Given quantity is unknown.")
        return (f, c)
