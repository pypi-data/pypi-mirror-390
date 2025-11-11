import logging
import pathlib

import numpy as np
import pytest
from pytest_mock import MockerFixture

import asmu
import asmu.io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_io_iinput_(mocker: MockerFixture, tmp_path: pathlib.Path) -> None:
    # create mocks
    interface = mocker.Mock(spec=asmu.Interface)

    # cut
    iinput = asmu.io.IInput(interface, 9, reference=True)

    # __repr__
    assert str(iinput) == "in_ch09"

    # test properties
    # test some known paramters
    iinput.name = "test"
    assert iinput._processor == interface
    assert iinput.channel == 9
    assert iinput.name == "test"
    with pytest.raises(AttributeError):
        iinput.cPa
    iinput.cPa = 4.21
    assert iinput.cPa == 4.21

    # test numpy arrays
    cFR = np.array([1.0, 3.1, 1.6, 2.1], dtype=np.complex64)
    iinput.cFR = cFR
    assert np.allclose(iinput.cFR, cFR)

    # test extra parameters
    iinput.blubs = 128
    assert iinput.blubs == 128
    assert iinput._extras["blubs"] == 128

    # test methods
    # serialize
    data = iinput.serialize(tmp_path)
    logger.info(data)
    assert data["channel"] == 9
    assert data["reference"]
    assert data["name"] == "test"
    assert data["cPa"] == 4.21
    assert data["cFR"] == tmp_path.with_name("in_ch09_cFR.npy").as_posix()
    assert data["blubs"] == 128

    # deserialize
    iinput2 = asmu.io.IInput(interface, channel=8, cV=10.2)
    iinput2.extrablubs = 1234
    iinput2.cPa = 25.432

    print(data)
    iinput2.deserialize(data)
    assert iinput2.channel == 9
    assert iinput2.reference
    assert iinput2.name == "test"
    assert iinput2.cPa == 4.21
    assert np.allclose(iinput2.cFR, cFR)
    assert iinput2.blubs == 128
    assert iinput2.cV == 10.2
    assert iinput2.extrablubs == 1234
    assert iinput2.cPa == 4.21
    logger.info(iinput2.serialize(tmp_path))
