import logging
import os

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)


def test_afile() -> None:
    """PyTest for the AFile."""
    interface = asmu.Interface()

    # generate test data
    rng = np.random.default_rng()
    data = rng.standard_normal((interface.blocksize, 2), dtype=np.float32)
    np.clip(data, -1, 1, out=data, dtype=np.float32)

    # test tmp file
    with asmu.AFile(interface, mode="w+", channels=2, temp=True) as afile:
        afile.write(data)
        # reduced tolerance due to 24bit conversion
        assert afile.data == pytest.approx(data, rel=1e-6, abs=1e-6)

    # test named file (32bit - float)
    with asmu.AFile(interface, mode="w", path="test.wav", channels=2, subtype="FLOAT") as afile:
        afile.write(data)
    with asmu.AFile(interface, mode="r", path="test.wav") as afile:
        assert afile.data == pytest.approx(data)

    # test named file (flac)
    with asmu.AFile(interface, mode="w", path="test.flac", channels=2, subtype="PCM_24") as afile:
        afile.write(data)
    with asmu.AFile(interface, mode="r", path="test.flac") as afile:
        # reduced tolerance due to 24bit conversion
        assert afile.data == pytest.approx(data, rel=1e-6, abs=1e-6)

    # test extra settings
    with asmu.AFile(interface, mode="w", path="test.ogg", channels=2) as afile:
        afile.settings = {"test": "Hello World!"}
    with asmu.AFile(interface, mode="r", path="test.ogg") as afile:
        assert afile.settings["test"] == "Hello World!"

    # remove files
    os.remove("./test.wav")
    os.remove("./test.flac")
    os.remove("./test.ogg")


if __name__ == "__main__":
    test_afile()
