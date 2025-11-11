import logging
import pathlib

import numpy as np
import pytest
from pytest_mock import MockerFixture

import asmu
import asmu.io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_io_ioutput_(mocker: MockerFixture, tmp_path: pathlib.Path) -> None:
    # create mocks
    interface = mocker.Mock(spec=asmu.Interface)

    # cut
    ioutput = asmu.io.IOutput(interface, 9, reference=True)

    # __repr__
    assert str(ioutput) == "out_ch09"

    # test properties
    # test some known paramters
    ioutput.name = "test"
    assert ioutput._processor == interface
    assert ioutput.channel == 9
    assert ioutput.name == "test"
    with pytest.raises(AttributeError):
        ioutput.cPa
    ioutput.cPa = 4.21
    assert ioutput.cPa == 4.21

    # test numpy arrays
    cFR = np.array([1.0, 3.1, 1.6, 2.1], dtype=np.complex64)
    ioutput.cFR = cFR
    assert np.allclose(ioutput.cFR, cFR)

    # test extra parameters
    ioutput.blubs = 128
    assert ioutput.blubs == 128
    assert ioutput._extras["blubs"] == 128

    # test methods
    # serialize
    data = ioutput.serialize(tmp_path)
    logger.info(data)
    assert data["channel"] == 9
    assert data["reference"]
    assert data["name"] == "test"
    assert data["cPa"] == 4.21
    assert data["cFR"] == tmp_path.with_name("out_ch09_cFR.npy").as_posix()
    assert data["blubs"] == 128

    # deserialize
    ioutput2 = asmu.io.IOutput(interface, channel=8, cV=10.2)
    ioutput2.extrablubs = 1234
    ioutput2.cPa = 25.432

    ioutput2.deserialize(data)
    assert ioutput2.channel == 9
    assert ioutput2.reference
    assert ioutput2.name == "test"
    assert ioutput2.cPa == 4.21
    assert np.allclose(ioutput2.cFR, cFR)
    assert ioutput2.blubs == 128
    assert ioutput2.cV == 10.2
    assert ioutput2.extrablubs == 1234
    assert ioutput2.cPa == 4.21
    logger.info(ioutput2.serialize(tmp_path))
