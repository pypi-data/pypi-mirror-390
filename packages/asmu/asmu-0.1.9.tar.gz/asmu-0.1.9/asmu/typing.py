"""This file stores abreviation of complex custom types."""
from typing import Callable, Literal, Optional, Protocol, Tuple, TypeAlias, TypedDict

import numpy as np
import numpy.typing as npt
import sounddevice as sd

from .acore import AAnalyzer, AEffect, AGenerator, AInterface

InA: TypeAlias = AGenerator | AEffect | AInterface
"""Type for ACore devices that can connect to inputs"""

InAs = Tuple[Tuple[Optional[InA], int], ...]
"""Tyoe for multiple InA devices and their corresponding channel number."""

ABlock = npt.NDArray[np.float32]
"""Type for single channel audio data block transferred by ACore devices.
ABlock.shape = (samples)"""

AWindowArg = npt.NDArray[np.float32 | np.float64]
"""Type for windowing time domain data prior to FFT.
Can be any float type, because it's converted to np.float32 anyways.
AWindow.shape = (windowsize)"""

AWindow = npt.NDArray[np.float32]
"""Type for windowing time domain data prior to FFT.
AWindow.shape = (windowsize)"""

FFTInput = npt.NDArray[np.float32]
"""Type for multi channel FFT data block.
Size depends on the input data window size.
FFTInput.shape = (windowsize, channels)"""

FFTOutput = npt.NDArray[np.complex64]
"""Type for multi channel FFT data block.
Size depends on the input data window size.
FFTOutput.shape = (windowsize/2+1, channels)"""

FFTFreqs = npt.NDArray[np.float32]
"""Type for FFT frequency vector.
Size depends on the input data window size.
FFTFreqs.shape = (windowsize/2+1)"""

FFTAbs = npt.NDArray[np.float32]
"""Type for multi channel abs(FFT) data block.
Size depends on the input data window size.
AvgTemp.shape = (windowsize/2+1, channels)"""

Avg = npt.NDArray[np.float32]
"""Type for multi channel average data.
RMSAvg.shape = (channels)"""

ABuffer = npt.NDArray[np.float32]
"""Type for multi channel audio data block stored in buffers of ACore devices.
ABuffer.shape = (samples, channels)"""

ACore = AGenerator | AAnalyzer | AEffect | AInterface
"""Type collecting all ACore devices."""

Device = Tuple[int | str | None, int | str | None] | int | str | None
"""Type for specifying audio device(s) to the Interface class on initialization."""


class CData(Protocol):
    """Type used to reflect sounddevice's CData object used in the callback function."""
    inputBufferAdcTime: float
    outputBufferDacTime: float
    currentTime: float


Callback = Callable[["npt.NDArray[np.float32]",
                     "npt.NDArray[np.float32]",
                     int,
                     CData,
                     sd.CallbackFlags],
                    None]
"""Type used to reflect sounddevice's calback function."""


class InterfaceIOTD(TypedDict, total=False):
    """Typed properties for InterfaceIO classes.

    Attributes:
        name: Trivial name.
        reference: Flag if the channel is used as reference for computation/calibration.
        gain: The gain setting of the input.
        latency: Individual IO latency (relative to Interface's system latency).
        color: A color used for plotting.
        cPa: Pressure calibration factor in Pascal.
        fPa: Frequency used for pressure calibration.
        datePa: Date of last pressure calibration (ISO 8601).
        cV: Voltage calibration factor in Volts.
        fV: Frequency used for voltage calibration.
        dateV: Date of last voltage calibration (ISO 8601).
        cA: Acceleration calibration factor in m/s^2.
        fA: Frequency used for acceleration calibration.
        dateA: Date of last acceleration calibration (ISO 8601).
        cFR: Frequency response calibration vector.
        fFR: Corresponding frequency vector.
        pos: Position vector.
    """
    # when PEP728 releases, we can also allow optional kwargs
    # https://peps.python.org/pep-0728/
    reference: Literal[True] | None
    name: str | None
    gain: float | None
    latency: int | None
    color: str | None
    cPa: float | None
    fPa: float | None
    datePa: str | None
    cV: float | None
    fV: float | None
    dateV: str | None
    cA: float | None
    fA: float | None
    dateA: str | None
    cFR: npt.NDArray[np.complex64] | None
    fFR: npt.NDArray[np.float32] | None
    pos: Tuple[float, float, float] | None
