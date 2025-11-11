"""In this submodule you can find the Input and Output classes used in the "audio processors".
You will rarely use them directly, but the special IInput and IOutput classes used by the interface,
store a lot of important information you may want to access or modify."""
import logging
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Literal,
    Optional,
    Tuple,
    Unpack,
    get_origin,
)

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from pathlib import Path

    from .interface import Interface
    from .processor import Analyzer, Effect, Generator
    from .typing import InA, InterfaceIOTD

logger = logging.getLogger(__name__)


class Input:
    def __init__(self, processor: "Effect|Interface|Analyzer"):
        """Input base class.

        Args:
            processor: Reference to the corresponding Processor object.
        """
        self._processor = processor
        self._output: Optional["Output"] = None

    @property
    def idx(self) -> int:
        return self._processor.inputs.index(self)

    @property
    def connected_output(self) -> Optional["Output|IInput"]:
        return self._output

    @connected_output.setter
    def connected_output(self, value: Optional["Output|IInput"]) -> None:
        self._output = value
        # if an output was set or unset, update acore module of processor
        self._processor.update_acore()

    def __bool__(self) -> bool:
        return isinstance(self._output, Output)


class Output:
    def __init__(self, processor: "Generator|Effect|Interface"):
        """Output base class.
        (Tuples are used to store the inputs because they are static typas and therefore more efficient than lists.)

        Args:
            processor: Reference to the corresponding Processor object.
        """
        self._processor = processor
        self._inputs: Tuple[Input, ...] = ()

    @property
    def inputs(self) -> Tuple[Input, ...]:
        return self._inputs

    @property
    def idx(self) -> int:
        return self._processor.outputs.index(self)

    @property
    def acore(self) -> "InA":
        return self._processor.acore

    def __bool__(self) -> bool:
        return bool(len(self._inputs))

    def connect(self, input: "Input") -> None:
        """Connect this output to the given Input.

        Args:
            input: The Input to connect this output to.

        Example: Connect devices
            ```python
            import asmu

            interface = asmu.Interface()
            sine = asmu.generator.Sine(interface, 1000)
            gain = asmu.effect.Gain(interface, 0.5)

            sine.output().connect(gain.input())
            gain.output().connect(interface.ioutput(ch = 2))
            ```
        """
        if input not in self._inputs:
            self._inputs += (input, )
            input.connected_output = self
            self._processor.update_acore()
        else:
            logger.debug("Input is already connected to output.")

    def disconnect(self, input: "Input") -> None:
        """Disconnect this output from the given Input.

        Args:
            input: The Input to disconnect this output from.
        """
        if input.connected_output is self and input in self._inputs:
            self._inputs = tuple(inp for inp in self._inputs if inp != input)
            input.connected_output = None
            self._processor.update_acore()
        else:
            logger.debug("Trying to disconnect an input that is not connected to this output")


class _InterfaceIO(ABC):
    # supported properties
    # these have to be stated here again to allow static type checking
    reference: Literal[True]
    name: str
    gain: float
    latency: int
    color: str
    cPa: float
    fPa: float
    datePa: str
    cV: float
    fV: float
    dateV: str
    cA: float
    fA: float
    dateA: str
    cFR: npt.NDArray[np.complex64]
    fFR: npt.NDArray[np.float32]
    pos: Tuple[float, float, float]

    def __init__(self,
                 channel: int,
                 **kwargs: Unpack["InterfaceIOTD"]):
        self._store_as_attr = True
        self.channel = channel
        # super() should be called here, so parent attributes dont land in _extra
        self._extras: Dict[str, Any] = {}  # used to store extra attributes
        self._store_as_attr = False
        # this would also store unnown kwargs in _extras
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    @property
    @abstractmethod
    def _type(self) -> str:
        """Either "in" or "out" type."""

    def __repr__(self) -> str:
        return f"{self._type}_ch{self.channel:02.0f}"

    def __setattr__(self, name: str, value: Any) -> None:
        if (name.startswith("_")
           or hasattr(self, name)
           or name in _InterfaceIO.__annotations__
           or getattr(self, "_store_as_attr", False)):
            super().__setattr__(name, value)
            return
        self._extras[name] = value

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name in self._extras:
            return self._extras[name]
        return super().__getattribute__(name)

    def serialize(self, setup_path: "Path") -> Dict[str, Any]:
        data: Dict[str, Any] = {"channel": self.channel}
        for key in _InterfaceIO.__annotations__.keys():
            if hasattr(self, key):
                value = getattr(self, key)
                # store numpy arrays as file
                if isinstance(value, np.ndarray):
                    _path = setup_path.with_name(f"{self._type}_ch{self.channel:02.0f}_{key}.npy")
                    np.save(_path, value)
                    value = _path.as_posix()
                data[key] = value
        data.update(self._extras)
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        # this does not delete properties that are set but not in data
        for key, value in data.items():
            if key in _InterfaceIO.__annotations__:
                # load numpy arrays from file
                _type: Any = _InterfaceIO.__annotations__[key]
                if (get_origin(_type) or _type) == np.ndarray:
                    value = np.load(data[key])
            self.__setattr__(key, value)


class IInput(Output, _InterfaceIO):
    def __init__(self,
                 interface: "Interface",
                 channel: int,
                 **kwargs: Unpack["InterfaceIOTD"]):
        """A special type of Output class used for the analog interface inputs.
        It stores various settings and options.

        Args:
            interface: Reference to an Interface instance.
            channel: Channel number on the interface.
            **kwargs (InterfaceIOTD): Optional attributes, additional paramters are possible.
        """
        Output.__init__(self, interface)
        _InterfaceIO.__init__(self, channel, **kwargs)

    @property
    def _type(self) -> str:
        return "in"


class IOutput(Input, _InterfaceIO):
    def __init__(self,
                 interface: "Interface",
                 channel: int,
                 **kwargs: Unpack["InterfaceIOTD"]):
        """A special type of Input class used for the analog interface outputs.
        It stores various settings and options.

        Args:
            interface: Reference to an Interface instance.
            channel: Channel number on the interface.
            **kwargs (InterfaceIOTD): Optional attributes, additional paramters are possible
        """
        Input.__init__(self, interface)
        _InterfaceIO.__init__(self, channel, **kwargs)

    @property
    def _type(self) -> str:
        return "out"
