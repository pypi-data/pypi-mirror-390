import logging
import os

import numpy as np

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_io_iinput() -> None:
    """PyTest for the IInput IO."""
    asetup = asmu.ASetup("test_io_iinput.asmu")
    interface = asmu.Interface()
    interface.asetup = asetup

    # first call creates input
    interface.iinput(ch=5).cFR = np.ones(1000, dtype=np.complex64)
    # second call returns standard value idx=0
    interface.iinput().fFR = np.linspace(0, 22050, 1000, endpoint=True, dtype=np.float32)
    asetup.save()

    asetup2 = asmu.ASetup("test_io_iinput.asmu")
    interface2 = asmu.Interface(asetup=asetup2)

    assert np.allclose(interface.iinput().cFR, interface2.iinput().cFR)
    assert np.allclose(interface.iinput().fFR, interface2.iinput().fFR)

    # remove files
    os.remove("test_io_iinput.asmu")
    os.remove("in_ch05_cFR.npy")
    os.remove("in_ch05_fFR.npy")


if __name__ == "__main__":
    test_io_iinput()
