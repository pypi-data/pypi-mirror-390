import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Unpack

import sounddevice as sd

from .acore import AInterface
from .io import IInput, IOutput
from .processor import Processor

if TYPE_CHECKING:
    from pathlib import Path

    from .asetup import ASetup
    from .exceptions import DeviceError
    from .processor import Analyzer
    from .typing import Callback, Device, InAs, InterfaceIOTD

logger = logging.getLogger(__name__)


class IDevice:
    def __init__(self, device: Optional[int | str] = None):
        """Class used internally to manage an audio device.

        Args:
            device: Numeric device ID or device name substring(s).
        """
        # can be initialized via index or str
        if device is None or (isinstance(device, int) and device < 0):
            self._index = -1
            self._name = "NoDevice"
            self._hostapi = "NoHostApi"
            return
        data = sd.query_devices(device)
        assert isinstance(data, dict)
        self.deserialize(data)

    def __str__(self) -> str:
        return f"[{self._index}] {self._name} | {self._hostapi}"

    def __bool__(self) -> bool:
        return self._index >= 0

    @property
    def sd(self) -> Optional[int]:
        """Parse IDevice as sounddevice device."""
        if self._index >= 0:
            return self._index
        return None

    @property
    def index(self) -> int:
        return self._index

    @property
    def hostapi(self) -> str:
        return self._hostapi

    def deserialize(self, data: Dict[str, Any]) -> None:
        try:
            self._index = int(data["index"])
            self._name = data["name"]
            if isinstance(data["hostapi"], int):
                # for int, extract name (because it could differ by system)
                hostapi = sd.query_hostapis(data["hostapi"])
                assert isinstance(hostapi, dict)
                self._hostapi = str(hostapi["name"])
            elif isinstance(data["hostapi"], str):
                # for str just store str
                self._hostapi = data["hostapi"]
            else:
                logger.warning("Format of hostapi not recognized.")
        except KeyError:
            logger.warning("Not all data given in IDevice deserialize.")

    def serialize(self) -> Dict[str, Any]:
        return {"index": self._index,
                "name": self._name,
                "hostapi": self._hostapi}


class Interface(Processor):
    def __init__(self,
                 asetup: Optional["ASetup"] = None,
                 device: "Device" = None,
                 samplerate: int = 44100,
                 blocksize: int = 1024) -> None:
        """The Interface class represents the audio interface or soundcard.
        It is holding the audio generator and manages settings.
        The settings can either be specified on intialization, by an ASetup class, or used as default.

        Args:
            asetup: Reference to an ASetup instance.
                If set, loads the settings from the given ASetup and the other arguments are ignored.
                If you dont want that, specify it after initialization, by setting `Interface.asetup = ASetup`.
            device: Tuple of device names for different input and output device.
                If None, the default devices are used.
            samplerate: The samplerate in samples per second.
            blocksize: The blocksize defines the samples per frame.

        Notes:
            The device names can be obtained by running
            ```python linenums="1" title="List audio devices"
            import asmu
            asmu.query_devices()
            ```
        """
        # this is used for the analyzers to add themselfes later
        self._analyzers: Tuple["Analyzer", ...] = ()

        self.asetup = asetup
        if asetup is not None:
            asetup.load()
        else:
            # init from given values
            self._samplerate = samplerate
            self._blocksize = blocksize
            self.latency = 0

            # init device if not test
            if device is None or device == (None, None):
                # if None use default
                default = tuple(sd.default.device)
                assert len(default) == 2
                device = default
                logger.info("No device specified, using default.")
            # if single device is given, convert to tuple
            if not isinstance(device, tuple):
                device = (device, device)
            # parse device dicts
            self._device = (IDevice(device[0]), IDevice(device[1]))

            # init in-/outputs
            self._iinputs: Tuple[IInput, ...] = ()
            self._ioutputs: Tuple[IOutput, ...] = ()

            self._ainterface = AInterface(blocksize=self._blocksize, start_frame=self.start_frame)
        super().__init__(self)

    @property
    def callback(self) -> "Callback":
        """Direct access to the callback function used for testing."""
        return self._ainterface.callback

    @property
    def samplerate(self) -> int:
        return self._samplerate

    @property
    def blocksize(self) -> int:
        return self._blocksize

    @property
    def start_frame(self) -> int:
        return 0

    @property
    def asetup(self) -> Optional["ASetup"]:
        return self._asetup

    @asetup.setter
    def asetup(self, value: Optional["ASetup"]) -> None:
        self._asetup = value
        # register in asetup
        if value is not None and self._asetup is not None:
            self._asetup.interface = self

    @property
    def analyzers(self) -> Tuple["Analyzer", ...]:
        return self._analyzers

    @analyzers.setter
    def analyzers(self, value: Tuple["Analyzer", ...]) -> None:
        self._analyzers = value
        self.update_acore()

    @property
    def acore(self) -> "AInterface":
        return self._ainterface

    @property
    def outputs(self) -> Tuple["IInput", ...]:
        return self._iinputs

    @property
    def inputs(self) -> Tuple["IOutput", ...]:
        return self._ioutputs

    @property
    def iinputs(self) -> Tuple["IInput", ...]:
        """Returns a list of all IInputs."""
        return self._iinputs

    @property
    def ioutputs(self) -> Tuple["IOutput", ...]:
        """Returns a list of all IOutputs."""
        return self._ioutputs

    def iinput(self,
               idx: int = 0,
               ch: Optional[int] = None,
               **kwargs: Unpack["InterfaceIOTD"]) -> "IInput":
        """If the given index points to the next element of iinputs list,
        or if the index exists, but the given channel does not:
        Create new IInput for given channel, with given kwargs, and return it.
        Otherwise, search for the IInput matching one of the given kwargs.
        Search is conducted in the given order.

        Args:
            idx: Index in zero indexed list of IInputs.
            ch: Interface analog input channel, stored in the IInput.
            **kwargs (InterfaceIOTD): Optional attributes, additional paramters are possible.

        Raises:
            ValueError: Given idx does not point to the next free slot:
                Cant create more than one channel at once.
            ValueError: New IInput must specify a physical channel. Use the ch argument.
            ValueError: No IInput with given kwargs registered.

        Returns:
            Reference to IInput object.
        """
        # handle idx
        if idx > len(self._iinputs):
            raise ValueError("Given idx does not point to the next free slot: "
                             "Cant create more than one channel at once.")
        # new iinput, parse other parameters
        if idx == len(self._iinputs):
            if ch is None:
                raise ValueError("New IInput must specify a physical channel. Use the ch argument.")
            logger.info("Index points to next elemnt in iinputs list: "
                        "Create new IInput.")
            iinput = IInput(self, ch, **kwargs)
            self._iinputs += (iinput, )
            return iinput
        # idx exists, continue and check channel
        if ch is not None:
            try:
                return next((outpu for outpu in self._iinputs if outpu.channel == ch))
            except StopIteration:
                logger.info("Channel not found, create new IInput.")
                iinput = IInput(self, ch, **kwargs)
                self._iinputs += (iinput, )
                return iinput
        # search for kwargs
        if kwargs:
            for key, name in kwargs.items():
                try:
                    return next((outpu for outpu in self._iinputs if getattr(outpu, key, None) == name))
                except StopIteration:
                    pass
            raise ValueError("No IInput with given kwargs registered.")
        return self._iinputs[idx]

    def ioutput(self,
                idx: int = 0,
                ch: Optional[int] = None,
                **kwargs: Unpack["InterfaceIOTD"]) -> "IOutput":
        """If the given index points to the next element of ioutputs list,
        or if the index exists, but the given channel does not:
        Create new IOutput for given channel, with given kwargs, and return it.
        Otherwise, search for the IInput matching one of the given kwargs.
        Search is conducted in the given order.

        Args:
            idx: Index in zero indexed list of IOutputs.
            ch: Interface analog output channel, stored in the IOutput.
            **kwargs (InterfaceIOTD): Optional attributes, additional paramters are possible.

        Raises:
            ValueError: Given idx does not point to the next free slot:
                Cant create more than one channel at once.
            ValueError: New IOutput must specify a physical channel. Use the ch argument.
            ValueError: No IInput with given kwargs registered.

        Returns:
            Reference to IOutput object.
        """
        # handle idx
        if idx > len(self._ioutputs):
            raise ValueError("Given idx does not point to the next free slot: "
                             "Cant create more than one channel at once.")
        # new ioutput, parse other parameters
        if idx == len(self._ioutputs):
            if ch is None:
                raise ValueError("New IOutput must specify a physical channel. Use the ch argument.")
            logger.info("Index points to next elemnt in ioutputs list: "
                        "Create new IOutput.")
            ioutput = IOutput(self, ch, **kwargs)
            self._ioutputs += (ioutput, )
            return ioutput
        # idx exists, continue and check channel
        if ch is not None:
            try:
                return next((inpu for inpu in self._ioutputs if inpu.channel == ch))
            except StopIteration:
                logger.info("Channel not found, create new IOutput.")
                ioutput = IOutput(self, ch, **kwargs)
                self._ioutputs += (ioutput, )
                return ioutput
        # search for kwargs
        if kwargs:
            for key, name in kwargs.items():
                try:
                    return next((inpu for inpu in self._ioutputs if getattr(inpu, key, None) == name))
                except StopIteration:
                    pass
            raise ValueError("No IInput with given kwargs registered.")
        return self._ioutputs[idx]

    def get_latency(self) -> int:
        """Calculate and return loopback latency calculated from buffer times.

        !!! warning
            Dont rely on this method, as it only calculates the ADC/DAC's internal latency.
            Use [calibrate_latency.py](../examples/calibration.md/#calibrate_latency.py)
            to compare this result with the real loopback calibration.

        Raises:
            ValueError: Latency can only be extracted after stream execution.
            ValueError: Latency computation yielded unplausible values (<1ms).
        """
        ctime = self._ainterface.ctime
        if ctime is None:
            raise ValueError("Latency can only be extracted after stream execution.")
        dt = ctime.outputBufferDacTime - ctime.inputBufferAdcTime
        if dt < 1e-3:
            raise ValueError("Latency computation yielded unplausible values (<1ms).")
        return round(dt * self.samplerate + 1.0)  # the +1 was measured experimentally (could be the cable?)

    def _is_driver(self, drivers: Tuple[str, ...] = ("ASIO", "CoreAudio")) -> bool:
        """Determine if ALL of the set io devices are one of the given drivers
        by searching the device name for both driver names.
        By default we search for ASIO and CoreAudio.

        Returns:
            `True`, when all given devices are compatible with one of the given drivers. `False` otherwise.
        """
        for driver in drivers:
            isdriver = True
            if not self._device[0] and not self._device[1]:
                return False
            if self._device[0]:
                if not (driver.lower() in self._device[0].hostapi.lower()):
                    isdriver = False
            if self._device[1]:
                if not (driver.lower() in self._device[1].hostapi.lower()):
                    isdriver = False
            if isdriver:
                return True
        return False

    def _init_sounddevice(self) -> None:
        """Initiializes sounddevice with the classes attributes for the given lists of inputs and outputs.
        Depending on the driver, different channel mappings are necessary.
        ASIO and CoreAudio have internal channel selectors that only use the selected channels in the stream.
        For other audio frameworks, the stream uses all channels up to the highest needed,
        and we have to use asmu's channel mapping.
        """
        # test i/o configuration
        if not any(self._device):
            raise DeviceError("Do device specified.")
        if not self._iinputs and not self._ioutputs:
            raise ValueError("You should at least specify one input or output channel.")
        if self._iinputs and not all(self._iinputs):
            logger.warning("There are unconnected IInputs.")
        if self._iinputs and not all(self._iinputs):
            logger.warning("There are unconnected IOutputs")

        stream = sd.default
        stream.dtype = ("float32", "float32")
        stream.samplerate = self.samplerate
        stream.blocksize = self.blocksize
        stream.device = (self._device[0].sd, self._device[1].sd)

        if self._is_driver(drivers=("ASIO", )):
            if self._iinputs:
                # convert to channel names starting with 0
                in_channels = [inpu.channel - 1 for inpu in self._iinputs]
                asio_in = sd.AsioSettings(channel_selectors=in_channels)

                if not self._ioutputs:
                    stream.extra_settings = asio_in
                    stream.channels = len(in_channels)
                    return

            if self._ioutputs:
                out_channels = [output.channel - 1 for output in self._ioutputs]
                asio_out = sd.AsioSettings(channel_selectors=out_channels)

                if not self._iinputs:
                    stream.extra_settings = asio_out
                    stream.channels = len(out_channels)
                    return

            if self._iinputs and self._ioutputs:
                stream.extra_settings = (asio_in, asio_out)
                stream.channels = (len(in_channels), len(out_channels))
                return

        if self._is_driver(drivers=("CoreAudio", )):
            logger.warning("CoreAudio channel selection is not tested!")
            if self._iinputs:
                # convert to channel names starting with 0
                in_channels = [inpu.channel - 1 for inpu in self._iinputs]
                ca_in = sd.CoreAudioSettings(channel_map=in_channels)

                if not self._ioutputs:
                    stream.extra_settings = ca_in
                    stream.channels = len(in_channels)
                    return

            if self._ioutputs:
                out_channels = [-1] * sd.query_devices(device=self._device[1].index,
                                                       kind="output")["max_output_channels"]
                for idx, c in enumerate(self._ioutputs):
                    out_channels[c.channel - 1] = idx
                ca_out = sd.CoreAudioSettings(channel_map=out_channels)

                if not self._iinputs:
                    stream.extra_settings = ca_out
                    stream.channels = len(out_channels)
                    return

            if self._iinputs and self._ioutputs:
                stream.extra_settings = (ca_in, ca_out)
                stream.channels = (len(in_channels), len(out_channels))
                return

        if self._iinputs and not self._ioutputs:
            stream.channels = (max([inpu.channel for inpu in self._iinputs]), 1)
        if self._ioutputs and not self._iinputs:
            stream.channels = (1, max([output.channel for output in self._ioutputs]))
        if self._iinputs and self._ioutputs:
            stream.channels = (max([inpu.channel for inpu in self._iinputs]),
                               max([output.channel for output in self._ioutputs]))

    def start(self, end_frame: Optional[int] = None, reset: bool = True, drop: int = 3) -> sd.Stream:
        """Start the audio stream.

        Args:
            end_frame: If set, the stream is stopped at the given end_frame.
            reset: If Truet, all audio processors are reset to initial frame.
                Otherwise, the Stream continues after the last stop.
            drop: Select how many frames to drop, when the audio stream restarts.

        Returns:
            Reference to the started sounddevice stream.
            The full documentation is linked
            [here](https://python-sounddevice.readthedocs.io/en/latest/api/streams.html#sounddevice.Stream).
                But the basic functions can be summerized as:

                - `Stream.active`  : `True`, when the stream is active. `False` otherwise.
                    This is useful when end_frame is used, to check if the stream is finished.
                - `Stream.stop()`  : Terminate audio processing.
                    This waits until all pending audio buffers have been played before it returns.
                - `Stream.close()` : Close the stream. This should be used after the stream has been stopped,
                    because the end_frame has been reached or Stream.stop has been called.

                If it is used for an active stream, the audio buffers are discarded.
        """
        self._init_sounddevice()
        self._ainterface.end_frame = end_frame
        if reset:
            self._ainterface.reset(drop=drop)
        stream = sd.Stream(callback=self._ainterface.callback)
        stream.start()
        return stream

    def update_acore(self) -> None:
        # create in_as tuple
        in_as: InAs = ()
        for inp in self._ioutputs:
            # add proper connection constraint
            if inp.connected_output is None:
                in_as = in_as + ((None, 0), )
            else:
                # find channel idx it is connected to
                in_as = in_as + ((inp.connected_output.acore, inp.connected_output.idx), )
        self._ainterface.in_as = in_as
        # update channel maps depending on driver
        # also see _init_sounddevice for explanation
        if self._is_driver():
            self._ainterface.out_ch_map = tuple(range(len(self._iinputs)))
            self._ainterface.in_ch_map = tuple(range(len(self._ioutputs)))
        else:
            self._ainterface.out_ch_map = tuple(inpu.channel - 1 for inpu in self._iinputs)
            self._ainterface.in_ch_map = tuple(output.channel - 1 for output in self._ioutputs)
        # update aanalyzers
        self._ainterface.alzs = tuple(alz.acore for alz in self.analyzers)

    def serialize(self, setup_path: "Path") -> dict[str, Any]:
        data: dict[str, Any] = {}
        data["samplerate"] = int(self._samplerate)
        data["blocksize"] = int(self._blocksize)
        data["latency"] = int(self.latency)

        if any(self._device):
            data["device"] = (self._device[0].serialize(),
                              self._device[1].serialize())

        iinputs = []
        for iinput in self._iinputs:
            iinputs.append(iinput.serialize(setup_path))
        data["iinputs"] = iinputs

        ioutputs = []
        for ioutput in self._ioutputs:
            ioutputs.append(ioutput.serialize(setup_path))
        data["ioutputs"] = ioutputs
        return data

    def deserialize(self, data: dict[str, Any]) -> None:
        self._samplerate = int(data["samplerate"])
        self._blocksize = int(data["blocksize"])
        self.latency = int(data["latency"])

        self._device = (IDevice(), IDevice())
        try:
            dev = tuple(data["device"])
            self._device[0].deserialize(dev[0])
            self._device[1].deserialize(dev[1])
        except KeyError:
            # if None use default
            default = tuple(sd.default.device)
            assert len(default) == 2
            self._device = (IDevice(default[0]), IDevice(default[1]))
            logger.info("No device specified, using default.")

        self._iinputs = ()
        for iinput_data in data["iinputs"]:
            iinput = IInput(self, iinput_data["channel"])
            iinput.deserialize(iinput_data)
            self._iinputs += (iinput, )

        self._ioutputs = ()
        for ioutput_data in data["ioutputs"]:
            ioutput = IOutput(self, ioutput_data["channel"])
            ioutput.deserialize(ioutput_data)
            self._ioutputs += (ioutput, )

        self._ainterface = AInterface(blocksize=self._blocksize, start_frame=self.start_frame)
