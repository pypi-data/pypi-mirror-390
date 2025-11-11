"""The signals are handled by the ACore objects,
which are optimized Python classes called in the callback of the audio interface.
They handle the audio buffers and call the other connected ACore objects.
The execution time and memory usage of these functions is critical,
always use [profiling](../development.md#profiling) when working on these base classes,
or inherit from them for new processors.
Higher memory usage of ACore functions can increase the thread switching time drastically; please akeep that in mind.

!!! quote "General philosophy"
    ACore objects are fast audio manipulation classes,
    that should never dynamically allocate memory or hold more objects than they really need.
    They are local classes to the corresponding Processor class, that does all the non-audio stuff.

!!! warning
    Keep in mind, that all the ACore classes run in a different thread, called by the sounddevice callback function.
    Therfore reading or writing to variables, except for initialization, has to be thread safe!
"""
# classes and functions in here should never reference big classes like Interface, Processors, IO, ...
# Ensure that those are never imported!!!
import queue
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, Optional, Tuple

import numpy as np
import sounddevice as sd

if TYPE_CHECKING:
    from .typing import ABlock, ABuffer, CData, FFTInput, InAs


class AGenerator(ABC):
    def __init__(self,
                 out_buffer: bool,
                 blocksize: int,
                 start_frame: int) -> None:
        """This is the base class for audio generators.

        Args:
            out_buffer: Flag that decides if outputs are buffered.
            blocksize: Blocksize of the audio arrays.
            start_frame: The number of the first frame (to start counting from).
        """
        self._out_buffer = out_buffer
        self._blocksize = blocksize
        self._last_frame = start_frame
        self._start_frame = start_frame

        # set output channels and update _out_buf
        self._out_buf: "ABuffer"
        self.out_chs = 1
        self._reload = True

    @property
    def out_chs(self) -> int:
        return self._out_chs

    @out_chs.setter
    def out_chs(self, value: int) -> None:
        self._out_chs = value
        # update _out_buf size
        if self._out_buffer and value is not None:
            self._out_buf = np.zeros((self._blocksize, value), dtype=np.float32)

    def upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
        """This method is called by other AProcessors, connected to the outputs,
        to obtain the outputs data of the given channel.
        It is called in the opposite of audio flow and is therefore called upstream.
        The connected (other) AProcessors pass their outdata reference (to write to)
        and the channel ch they want to obtain the data from.
        Inside upstream, buffering and the appropriate calls for _mod and _inc are handled.

        Args:
            outdata: Reference of the 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).
            frame: Current frame number to be processed, this always increases by +1 and is incremented by the callback.
        """
        # if the next frame is called, increment and set buffer reload flag
        if frame != self._last_frame:
            self._last_frame = frame
            self._inc()
            self._reload = True
        # if out_buffer is enabled and reload flag is set fill _out_buf
        if self._out_buffer and self._reload:
            if self._out_buffer:
                for out_ch in range(self._out_chs):
                    self._mod(self._out_buf[:, out_ch], out_ch)
        self._reload = False

        # if buffer is enabled return buffer
        if self._out_buffer:
            outdata[:] = self._out_buf[:, ch]
        # otherwise process given array
        else:
            self._mod(outdata, ch)

    def upreset(self) -> None:
        self._last_frame = self._start_frame
        self._reset()

    @abstractmethod
    def _mod(self, outdata: "ABlock", ch: int) -> None:
        """This function is envoked by `upstream()`.
        It should write something in outdata for the given output channel ch.
        Make sure to copy your data or write directly into outdata and not just set outdata to a new reference.
        See sounddevice callback manual for more details.

        Args:
            outdata: The 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).
        """
        return None

    @abstractmethod
    def _inc(self) -> None:
        """This function is envoked by `upstream()`.
        If the class changes over time, this function can be used to perform these changes.
        It is called exactly once after all channels of the class have been processed.
        """
        return None

    @abstractmethod
    def _reset(self) -> None:
        """This function should reset the generator into initial state."""
        return None


class AEffect(ABC):
    def __init__(self,
                 in_buffer: bool,
                 out_buffer: bool,
                 blocksize: int,
                 start_frame: int) -> None:
        """This is the base class for audio effects

        Args:
            in_buffer: Flag that decides if inputs are buffered, usually used for long input chains and fast effects.
            out_buffer: Flag that decides if outputs are buffered, usually used for slow effects.
            blocksize: Blocksize of the audio arrays.
            start_frame: The number of the first frame (to start counting from).
        """
        self._in_buffer = in_buffer
        self._out_buffer = out_buffer
        self._blocksize = blocksize
        self._last_frame = start_frame
        self._start_frame = start_frame

        # set in-/output channels and update buffers
        self._in_buf: "ABuffer"
        self._out_buf: "ABuffer"
        self.out_chs = 1
        self._reload = True

    @property
    def in_as(self) -> "InAs":
        """A tupel defining what objects output and channel, the inputchannels are connected to.
        Evaluating in_as[in_ch] for an input channel in_ch of self,
        yields a tuple of (Connected Object, Connected Channel)."""
        return self._in_as

    @in_as.setter
    def in_as(self, value: "InAs") -> None:
        """Setting in_as automatically updates the buffer size, if in_buffer is enabled."""
        self._in_as = value
        # update _in_buf size
        if self._in_buffer and value is not None:
            self._in_buf = np.zeros((self._blocksize, len(value)), dtype=np.float32)

    @property
    def out_chs(self) -> int:
        return self._out_chs

    @out_chs.setter
    def out_chs(self, value: int) -> None:
        self._out_chs = value
        # update _out_buf size
        if self._out_buffer and value is not None:
            self._out_buf = np.zeros((self._blocksize, value), dtype=np.float32)

    def upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
        """This method is called by other AProcessors, connected to the outputs,
        to obtain the outputs data of the given channel.
        It is called in the opposite of audio flow and is therefore called upstream.
        The connected (other) AProcessors pass their outdata reference (to write to)
        and the channel ch they want to obtain the data from.
        Inside upstream, buffering and the appropriate calls for _mod and _inc are handled.

        Args:
            outdata: Reference of the 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).
            frame: Current frame number to be processed, this always increases by +1 and is incremented by the callback.
        """
        # if the next frame is called, increment and set buffer reload flag
        if frame != self._last_frame:
            self._last_frame = frame
            self._inc()
            self._reload = True
        # if in_buffer is enabled and reload flag is set fill _in_buf
        if self._in_buffer and self._reload:
            self._fill_in_buf(frame)
        # if out_buffer is enabled and reload flag is set fill _out_buf
        if self._out_buffer and self._reload:
            self._fill_out_buf(frame)
        self._reload = False

        # if out_buffer is enabled copy _out_buf
        if self._out_buffer:
            outdata[:] = self._out_buf[:, ch]
        # otherwise process given array
        else:
            # _mod HAS TO HANDLE INPUT BUFFER + SETTING!!!
            self._mod(outdata, ch, frame)

    def upreset(self) -> None:
        # reset self
        self._last_frame = self._start_frame
        self._reset()
        # call reset upstream
        for in_a in self._in_as:
            if in_a[0] is not None:
                in_a[0].upreset()

    def _fill_in_buf(self, frame: int) -> None:
        self._in_buf.fill(0)
        for in_ch, in_a in enumerate(self._in_as):
            if in_a[0] is not None:
                # send _in_buf upstream
                in_a[0].upstream(self._in_buf[:, in_ch], in_a[1], frame)

    def _fill_out_buf(self, frame: int) -> None:
        for out_ch in range(self._out_chs):
            self._mod(self._out_buf[:, out_ch], out_ch, frame)

    def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
        """This function is envoked by `upstream()`.
        It should write something in outdata for the given output channel ch.
        Make sure to copy your data or write directly into outdata and not just set outdata to a new reference.
        See sounddevice callback manual for more details.

        Args:
            outdata: The 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).

        Notes:
            The implementation of this function process the input buffer `self._in_buf`,
            that is periodically filled by `start_upstream()`.
        """
        raise NotImplementedError("For enabled self._in_buffer, you must override this function!")

    def _mod_upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
        """This function is envoked by `upstream()`.
        It should write something in outdata for the given output channel ch.
        Make sure to copy your data or write directly into outdata and not just set outdata to a new reference.
        See sounddevice callback manual for more details.

        Args:
            outdata: The 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).
            frame: Current frame number to be processed, this always increases by +1 and is incremented by the callback.

        Notes:
            The implementation of this function sends data upstream to process for each input channel.

        Example: Input buffer example
            ```python
                in_a = self._in_as[ch][0]
                if in_a is not None:
                    # get outdata from upstream
                    in_a.upstream(outdata, self._in_as[ch][1], frame)
                    # process outdata here
                    ...
            ```
        """
        raise NotImplementedError("For disabled self._in_buffer, you must override this function!")

    def _mod(self, outdata: "ABlock", ch: int, frame: int) -> None:
        if self._in_buffer:
            self._mod_in_buf(outdata, ch)
        else:
            self._mod_upstream(outdata, ch, frame)

    @abstractmethod
    def _inc(self) -> None:
        """This function is envoked by `upstream()`.
        If the class changes over time, this function can be used to perform these changes.
        It is called exactly once per audio frame, but not for the first one.
        """
        return None

    @abstractmethod
    def _reset(self) -> None:
        """This function should reset the effect into initial state."""
        return None


class AEffectEnvelope(AEffect):
    def __init__(self,
                 gains: Tuple[float, ...],
                 steps: Tuple[float, ...],
                 scale: Literal["lin", "log"],
                 in_buffer: bool,
                 out_buffer: bool,
                 blocksize: int,
                 start_frame: int) -> None:
        self.cue: queue.Queue[int] = queue.Queue(maxsize=1)

        self._gains = gains
        self._steps = steps
        self._ramps = []
        self._is_gain = self._gains[0]
        for step in steps:
            self._ramps.append(np.linspace(0, step, blocksize, dtype=np.float32))
        self._scale = scale

        self._idx = 0
        self._gainramp = np.zeros(blocksize, dtype=np.float32)
        super().__init__(in_buffer=in_buffer,
                         out_buffer=out_buffer,
                         blocksize=blocksize,
                         start_frame=start_frame)

    def update_ramp(self, start: int = 0) -> None:
        idx = self._idx
        if start > 0:
            self._gainramp[start:] = self._is_gain + self._ramps[idx][:-start]
            # print(self._gainramp[start-10:start+10])
        else:
            self._gainramp = self._is_gain + self._ramps[idx]
        if self._steps[idx] > 0:
            search = start + np.searchsorted(self._gainramp[start:], self._gains[idx], side="right")
        elif self._steps[idx] < 0:
            search = start + np.searchsorted(-self._gainramp[start:], -self._gains[idx], side="right")
        else:
            if not start and self._scale == "log":
                self._log(self._gainramp)
            return
        # print("idx: ", self._idx, ", start: ", start, ", is_gain: ", self._is_gain, ", search: ", search)
        if search < self._blocksize:
            self._is_gain = self._gains[idx]
            self._idx += 1
            self.update_ramp(int(search))
        self._is_gain = self._gainramp[-1]
        if not start and self._scale == "log":
            self._log(self._gainramp)

    def _inc(self) -> None:
        # test fo queues
        if not self.cue.empty():
            self._idx = self.cue.get()
        self.update_ramp()

    def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
        outdata[:] = self._in_buf[:, ch] * self._gainramp

    def _mod_upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
        in_a = self._in_as[ch][0]
        if in_a is not None:
            in_a.upstream(outdata, self._in_as[ch][1], frame)  # get outdata from upstream
            outdata *= self._gainramp  # modify outdata

    def _log(self, x: "ABlock") -> None:
        x += np.log10(1 / 9)
        np.power(10, x, out=x)
        x -= 1 / 9

    def _reset(self) -> None:
        self._idx = 0
        self._is_gain = self._gains[0]


class AAnalyzer(ABC):
    def __init__(self,
                 in_buffer: bool,
                 blocksize: int,
                 start_frame: int) -> None:
        """This is the base class for audio analyzers.

        Args:
            in_buffer: Flag that decides if inputs are buffered.
            blocksize: Blocksize of the audio arrays.
            start_frame: The number of the first frame (to start counting from).
        """
        self._in_buffer = in_buffer
        self._blocksize = blocksize
        self._start_frame = start_frame

        # set input channels and update _in_buf
        self._in_buf: "ABuffer"

    @property
    def buffersize(self) -> int:
        """This proerty gives the buffersize, usually self._blocksize, but can be overriden for exotic buffersizes.
        Make sure to also override self._fill_in_buf() to handle special bufersizes."""
        return self._blocksize

    @property
    def in_as(self) -> "InAs":
        """A tupel defining what objects output and channel, the inputchannels are connected to.
        Evaluating in_as[in_ch] for an input channel in_ch of self,
        yields a tuple of (Connected Object, Connected Channel)."""
        return self._in_as

    @in_as.setter
    def in_as(self, value: "InAs") -> None:
        """Setting in_as automatically updates the buffer size, if in_buffer is enabled."""
        self._in_as = value
        # update _in_buf size
        if self._in_buffer and value is not None:
            self._update_in_buf(len(value))

    def _update_in_buf(self, channels: int) -> None:
        self._in_buf = np.zeros((self.buffersize, channels), dtype=np.float32)

    def start_upstream(self, frame: int) -> None:
        # no additional frame processing necessary,
        # because this function is only called once per frame
        # if in_buffer is enabled fill _in_buf
        if self._in_buffer:
            self._fill_in_buf(frame)
            self._process_in_buf()
        else:
            self._process_upstream(frame)

    def start_reset(self) -> None:
        # call reset upstream
        for in_a in self._in_as:
            if in_a[0] is not None:
                in_a[0].upreset()

    def _fill_in_buf(self, frame: int) -> None:
        self._in_buf.fill(0)
        for in_ch, in_a in enumerate(self._in_as):
            if in_a[0] is not None:
                # send _in_buf upstream
                in_a[0].upstream(self._in_buf[:, in_ch], in_a[1], frame)

    def _process_in_buf(self) -> None:
        """This method is called once per audio frame to process the obtained self._in_buf

        Notes:
            The implementation of this function process the input buffer `self._in_buf`,
            that is periodically filled by `start_upstream()`.
        """
        raise NotImplementedError("For enabled self._in_buffer, you must override this function.")

    def _process_upstream(self, frame: int) -> None:
        """This method is called once per audio frame to start the upstream chain.

        Notes:
            The implementation of this function sends data upstream to process for each input channel.

        Example: Input buffer example
            ```python
            NUMPY_ARRAY_TO_WRITE_TO.fill(0)
            for in_ch, in_a in enumerate(self._in_as):
                if in_a[0] is not None:
                    in_a[0].upstream(NUMPY_ARRAY_TO_WRITE_TO[:, in_ch], in_a[1], frame)
            ```
        """
        raise NotImplementedError("For disabled self._in_buffer, you must override this function.")

    @abstractmethod
    def _reset(self) -> None:
        """This function should reset the generator into initial state."""
        return None


class AAnalyzerBuf(AAnalyzer):
    def __init__(self, bufsize: int, blocksize: int, start_frame: int) -> None:
        """This is an extended base class for audio analyzers, with input buffer larger than the audio buffer.

        Args:
            bufsize: Size of the analyzer buffer.
            blocksize: Blocksize of the audio arrays.
            start_frame: The number of the first frame (to start counting from).
        """
        self.buf_queue: queue.Queue[FFTInput] = queue.Queue(maxsize=1)

        self._bufsize = bufsize
        self._in_buf_idx = 0

        super().__init__(in_buffer=True,
                         blocksize=blocksize,
                         start_frame=start_frame)

    @property
    def buffersize(self) -> int:
        # make the buffer bigger than the window to fit the overflow
        return self._bufsize+self._blocksize

    def _fill_in_buf(self, frame: int) -> None:
        for in_ch, in_a in enumerate(self._in_as):
            if in_a[0] is not None:
                # send _in_buf upstream
                lower = self._in_buf_idx
                upper = self._in_buf_idx+self._blocksize
                in_a[0].upstream(self._in_buf[lower:upper, in_ch], in_a[1], frame)
            else:
                self._in_buf[:, in_ch].fill(0)

    def _process_in_buf(self) -> None:
        self._in_buf_idx += self._blocksize
        if self._in_buf_idx >= self._bufsize:
            # put the buffer into queue
            if not self.buf_queue.full():
                self.buf_queue.put(self._in_buf[:self._bufsize].copy())
            # handle the overflow (rest)
            # TODO: Fix this overfolw and then profile!
            rest = self._in_buf_idx - self._bufsize
            if rest > 0:
                self._in_buf[:rest, :] = self._in_buf[self._bufsize:self._in_buf_idx]
            self._in_buf_idx = rest

    def _reset(self) -> None:
        self._in_buf_idx = 0
        while not self.buf_queue.empty():
            self.buf_queue.get(block=False)


class AInterface:
    def __init__(self, blocksize: int, start_frame: int):
        """This is the base class of the audio interface.
        It is used to assemble the callback function.

        Args:
            blocksize: Blocksize of the audio arrays.
            start_frame: The number of the first frame (to start counting from).
        """
        self._out_buf: "ABuffer"
        self.out_ch_map = ()
        self.in_ch_map = ()
        self._in_as: "InAs" = ()

        self._blocksize = blocksize
        self._frame = start_frame
        self._start_frame = start_frame
        self.ctime: Optional["CTime"] = None

        self._alzs: Tuple["AAnalyzer", ...] = ()

        self.end_frame: Optional[int] = None

    @property
    def in_as(self) -> "InAs":
        """A tupel defining what objects output and channel, the inputchannels are connected to.
        Evaluating in_as[in_ch] for an input channel in_ch of self,
        yields a tuple of (Connected Object, Connected Channel)."""
        return self._in_as

    @in_as.setter
    def in_as(self, value: "InAs") -> None:
        self._in_as = value

    @property
    def out_ch_map(self) -> Tuple[int, ...]:
        return self._out_ch_map

    @out_ch_map.setter
    def out_ch_map(self, value: Tuple[int, ...]) -> None:
        self._out_ch_map = value
        if value:
            # update _out_buf size
            self._out_buf = np.zeros((self._blocksize, len(value)), dtype=np.float32)

    @property
    def in_ch_map(self) -> Tuple[int, ...]:
        return self._in_ch_map

    @in_ch_map.setter
    def in_ch_map(self, value: Tuple[int, ...]) -> None:
        self._in_ch_map = value

    @property
    def alzs(self) -> Tuple["AAnalyzer", ...]:
        return self._alzs

    @alzs.setter
    def alzs(self, value: Tuple["AAnalyzer", ...]) -> None:
        self._alzs = value

    @property
    def frame(self) -> int:
        return self._frame

    @frame.setter
    def frame(self, value: int) -> None:
        self._frame = value

    def callback(self,
                 indata: "ABuffer",
                 outdata: "ABuffer",
                 frames: int,
                 ctime: "CData",
                 status: sd.CallbackFlags) -> None:
        # drop frames to allow callback to stabilize
        if self._frame >= self._start_frame:
            # ctime can be None for tests...
            if self.ctime is None and ctime is not None:
                self.ctime = CTime(ctime)
            # copy indata so it can be processed by upstream()
            if self.out_ch_map:
                self._out_buf[:] = indata[:, self.out_ch_map]
            # call upstream method of the outputs connected to the inputs
            if self.in_as != ():
                outdata.fill(0)
                for in_ch, in_a in enumerate(self._in_as):
                    if in_a[0] is not None:
                        in_a[0].upstream(outdata[:, self.in_ch_map[in_ch]], in_a[1], self._frame)
            # call AAnalyzers start_upstream method (because they wont get called otherwise)
            for alz in self._alzs:
                alz.start_upstream(self._frame)
        self._frame += 1  # Overflow?
        if self.end_frame is not None and self.end_frame <= self._frame:
            raise sd.CallbackStop

    def upstream(self, outdata: "ABlock", ch: int, frame: int) -> None:
        """This method is called by other AProcessors, connected to the outputs,
        to obtain the outputs data of the given channel.
        It just copies the bufferd indata of the respected channel to the given outdata reference

        Args:
            outdata: Reference of the 1D array to write to, with length blocksize.
            ch: The channel corresponding to the outdata at hand (zero indexed).
            frame: Current frame number to be processed, this always increases by +1 and is incremented by the callback.
        """
        outdata[:] = self._out_buf[:, ch]

    def reset(self, drop: int = 0) -> None:
        """Reset all connected processors.

        Args:
            drop: Select how many frames to drop, when the audio stream restarts.
        """
        # reset self
        self._frame = self._start_frame - drop
        # call reset upstream
        for in_a in self._in_as:
            if in_a[0] is not None:
                in_a[0].upreset()
        # call AAnalyzers reset to start upstream reset
        for alz in self._alzs:
            alz.start_reset()

    def upreset(self) -> None:
        return


class CTime():
    def __init__(self, cdata: "CData"):
        """Class used to parse and store sounddevice's CTime values."""
        self.inputBufferAdcTime = cdata.inputBufferAdcTime
        self.outputBufferDacTime = cdata.outputBufferDacTime
        self.currentTime = cdata.currentTime
