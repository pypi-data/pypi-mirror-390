"""In this submodule you can find all effects, so "audio processors" with one or multiple inputs and outputs."""
import logging
import queue
from typing import TYPE_CHECKING, Literal, Tuple

import numpy as np
import pyfftw

from .acore import AEffect, AEffectEnvelope
from .io import Input, Output
from .processor import Effect

if TYPE_CHECKING:
    from .interface import Interface
    from .typing import ABlock, FFTFreqs, FFTOutput

logger = logging.getLogger(__name__)


class Gain(Effect):
    def __init__(self,
                 interface: "Interface",
                 gain: float,
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        """The Gain class effect is used to multiply a signal with the given gain.
        It is a multi input multi output effect, that applies the same gain to all connections.
        Input-update and output-update are supported.

        Args:
            interface: Reference to an Interface instance.
            gain: The gain.
            in_buffer: Flag that decides if inputs are buffered.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._gain = gain
        self._again = self._AGain(gain, in_buffer, out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._again,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    class _AGain(AEffect):
        def __init__(self,
                     gain: float,
                     in_buffer: bool,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self._gain = gain
            super().__init__(in_buffer=in_buffer,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            outdata[:] = self._in_buf[:, ch] * self._gain

        def _mod_upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
            in_a = self._in_as[ch][0]
            if in_a is not None:
                in_a.upstream(outdata, self._in_as[ch][1], frame)  # get outdata from upstream
                outdata *= self._gain  # modify outdata

        def _inc(self) -> None:
            return None

        def _reset(self) -> None:
            return None


class GainRamp(Effect):
    def __init__(self,
                 interface: "Interface",
                 gain: float,
                 gradient: float,
                 scale: Literal["lin", "log"] = "lin",
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        """The GainRamp class effect is used to smoothly change between gains.
        The gain initially specified and the newly set values are linear setpoints.
        If scale is set to "log", this will be scaled accordingly.
        It is a multi input multi output effect, that applies the same gain to all connections.
        Input-update and output-update are supported.


        Args:
            interface: Reference to an Interface instance.
            gain: The initial gain.
            gradient: The desired linear gain change per second.
            scale: Scaling of the given gain.
            in_buffer: Flag that decides if inputs are buffered.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._gain = gain
        step = gradient/interface.samplerate*interface.blocksize
        self._againramp = self._AGainRamp(gain, step, scale, in_buffer, out_buffer,
                                          interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._againramp,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    def set_gain(self, gain: float) -> None:
        """This is updated at the next upcoming frame.
        This is updated at the next upcoming frame.
        The function call blocks when called faster than the frames.

        Args:
            gain: The linear gain setpoint. If scale is set to "log", this will be scaled accordingly.
        """
        self._gain = gain
        self._againramp.gain_queue.put(self._gain)

    class _AGainRamp(AEffect):
        def __init__(self,
                     gain: float,
                     step: float,
                     scale: Literal["lin", "log"],
                     in_buffer: bool,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            # step: The desired linear gain change per frame.
            self.gain_queue: queue.Queue[float] = queue.Queue(maxsize=1)

            self._is_gain = gain
            self._set_gain = gain
            self._start_gain = gain
            self._ramp = np.linspace(0, step, blocksize, endpoint=True, dtype=np.float32)
            self._scale = scale

            self._gainramp = np.ones_like(self._ramp, dtype=np.float32) * gain
            super().__init__(in_buffer=in_buffer,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            outdata[:] = self._in_buf[:, ch] * self._gainramp

        def _mod_upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
            in_a = self._in_as[ch][0]
            if in_a is not None:
                in_a.upstream(outdata, self._in_as[ch][1], frame)  # get outdata from upstream
                outdata *= self._gainramp  # modify outdata

        def _inc(self) -> None:
            # get new gain if available
            if not self.gain_queue.empty():
                self._set_gain = self.gain_queue.get()
            # check if we are still in ramp mode (with tolerance)
            if abs(self._set_gain - self._is_gain) > 1e-3:
                if self._set_gain > self._is_gain:
                    # ramping downwards
                    self._gainramp = self._is_gain + self._ramp
                    self._gainramp[self._gainramp > self._set_gain] = self._set_gain
                else:
                    # ramping upwards
                    self._gainramp = self._is_gain - self._ramp
                    self._gainramp[self._gainramp < self._set_gain] = self._set_gain
                # set new gain
                self._is_gain = self._gainramp[-1]

                # scale the ramp
                if self._scale == "log":
                    self._log(self._gainramp)
            else:
                self._gainramp[:] = self._set_gain

        def _log(self, x: "ABlock") -> None:
            x += np.log10(1 / 9)
            np.power(10, x, out=x)
            x -= 1 / 9

        def _reset(self) -> None:
            self._is_gain = self._start_gain
            self._set_gain = self._start_gain
            # clear queues
            while not self.gain_queue.empty():
                self.gain_queue.get(block=False)


class ADSR(Effect):
    def __init__(self,
                 interface: "Interface",
                 attack: float,
                 decay: float,
                 sustain: float,
                 release: float,
                 scale: Literal["lin", "log"] = "lin",
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        assert attack > 0, "Attack must be > 0s."
        # ((gain-setpoint, gradient), ...)
        # init, attack
        gains: Tuple[float, ...] = (0, 1)
        steps: Tuple[float, ...] = (0, 1/attack/interface.samplerate*interface.blocksize)
        # decay
        if decay > 0:
            gains += (sustain, )
            steps += ((sustain - 1)/decay/interface.samplerate*interface.blocksize, )
        else:
            assert sustain == 1, "For zero decay, sustain must be 1."
        # sustain
        gains += (sustain, )
        steps += (0, )
        self._sustain_cue = len(gains)
        # release
        if release > 0:
            gains += (0, 0)
            steps += (-sustain/release/interface.samplerate*interface.blocksize, 0)
        else:
            self._sustain_cue -= 1
            assert sustain == 0, "For zero release, sustain must be 0."
        logger.info("gains = ", gains)
        logger.info("steps = ", steps)
        logger.info("sustain_cue = ", self._sustain_cue)
        self._aadsr = AEffectEnvelope(gains, steps, scale, in_buffer, out_buffer,
                                      interface.blocksize, interface.start_frame)

        self._running = False
        super().__init__(aeffect=self._aadsr,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    def start(self) -> None:
        self._aadsr.cue.put(1)
        self._running = True

    def running(self) -> bool:
        return self._running

    def release(self) -> None:
        self._aadsr.cue.put(self._sustain_cue)
        self._running = False


class Sum(Effect):
    def __init__(self,
                 interface: "Interface",
                 out_buffer: bool = False) -> None:
        """The Sum class effect is used to sum multiple inputs to a single output.
        Arithmetic averaging is used for summing.
        It is a multi input single output effect, therefore output-update is not supported.
        Input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._asum = self._ASum(out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._asum,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=False)

    class _ASum(AEffect):
        def __init__(self,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            super().__init__(in_buffer=True,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            np.mean(self._in_buf, axis=1, out=outdata, dtype=np.float32)

        def _inc(self) -> None:
            return None

        def _reset(self) -> None:
            return None


class Weight(Effect):
    def __init__(self,
                 interface: "Interface",
                 weight: Literal["Z", "A", "C"],
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        """The Weight effect is used to apply A, C, or Z weighting to signaks,
        via the fft/ifft approach and the weighting functions according to IEC 61672.

        Args:
            interface: Reference to an Interface instance.
            weight: Weighting according to IEC 61672.
            in_buffer: Flag that decides if inputs are buffered.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._weight = weight
        self._aweight = self._AWeight(weight,
                                      in_buffer,
                                      out_buffer,
                                      interface.blocksize,
                                      interface.samplerate,
                                      interface.start_frame)
        super().__init__(aeffect=self._aweight,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    @property
    def frequencies(self) -> "FFTFreqs":
        """The corresponding frequency vector of the FFT."""
        return self._aweight._fs

    def get_weight(self, frequencies: "FFTFreqs") -> "FFTOutput":
        """Returns the weighting function according to IEC 61672.

        Args:
            frequencies: Frequency vector.

        Returns:
            Vector of weights.
        """
        match self._weight:
            case "A":
                return self._aweight._Aw(frequencies)
            case "C":
                self._w = self._aweight._Cw(frequencies)
        return np.ones_like(frequencies, dtype=np.complex64)

    class _AWeight(AEffect):
        def __init__(self,
                     weight: Literal["Z", "A", "C"],
                     in_buffer: bool,
                     out_buffer: bool,
                     blocksize: int,
                     samplerate: int,
                     start_frame: int) -> None:

            self._indata_fftw = pyfftw.empty_aligned(blocksize, dtype=np.float32)
            self._scale_c64 = np.complex64(1 / blocksize)
            self._rfft = pyfftw.empty_aligned(int(blocksize/2+1), dtype=np.complex64)
            self._fftw = pyfftw.FFTW(self._indata_fftw,
                                     self._rfft,
                                     axes=(0, ),
                                     flags=('FFTW_ESTIMATE', ))
            self._ifftw = pyfftw.FFTW(self._rfft,
                                      self._indata_fftw,
                                      axes=(0, ),
                                      direction="FFTW_BACKWARD",
                                      flags=('FFTW_ESTIMATE', ))

            self._fs = np.fft.rfftfreq(blocksize, 1/samplerate).astype(np.float32)

            match weight:
                case "Z":
                    self._weight = False
                case "A":
                    logger.warning("A-Weight implementation is resource intensive and "
                                   "can cause audio issues. Use with caution!")
                    self._weight = True
                    self._w = self._Aw(self._fs)
                case "C":
                    logger.warning("C-Weight implementation is resource intensive and "
                                   "can cause audio issues. Use with caution!")
                    self._weight = True
                    self._w = self._Cw(self._fs)

            super().__init__(in_buffer=in_buffer,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _Cw(self, f: "FFTFreqs") -> "FFTOutput":
            # values from IEC 61672
            f1 = 20.6
            f4 = 12194
            C1000 = -0.062

            c = 10**(C1000/20)
            w = ((f4**2 * f**4)/((f**2 + f1**2)*(f**2 + f4**2))/c)
            return np.asarray(w, dtype=np.complex64)

        def _Aw(self, f: "FFTFreqs") -> "FFTOutput":
            # values from IEC 61672
            f1 = 20.6
            f2 = 107.7
            f3 = 737.9
            f4 = 12194
            A1000 = -2.0

            a = 10**(A1000/20)
            w = ((f4**2 * f**4) /
                 ((f**2 + f1**2) *
                  (f**2 + f2**2)**0.5 *
                  (f**2 + f3**2)**0.5 *
                  (f**2 + f4**2))/a)
            return np.asarray(w, dtype=np.complex64)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            if self._weight:
                self._indata_fftw[:] = self._in_buf[:, ch]
                self._fftw.execute()
                self._rfft *= self._scale_c64  # normalize fft
                self._rfft *= self._w
                self._ifftw.execute()
                outdata[:] = self._indata_fftw
            else:
                outdata[:] = self._in_buf[:, ch]

        def _mod_upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
            in_a = self._in_as[ch][0]
            if in_a is not None:
                # get outdata from upstream
                in_a.upstream(outdata, self._in_as[ch][1], frame)
                if self._weight:
                    # process outdata here
                    self._indata_fftw[:] = outdata
                    self._fftw.execute()
                    self._rfft *= self._scale_c64  # normalize fft
                    self._rfft *= self._w
                    self._ifftw.execute()
                    outdata[:] = self._indata_fftw

        def _inc(self) -> None:
            return None

        def _reset(self) -> None:
            return None
