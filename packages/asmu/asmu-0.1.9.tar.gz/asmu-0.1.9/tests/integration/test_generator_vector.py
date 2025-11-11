import logging

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_generator_vector(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the Vector Generator."""
    # create objects
    interface = asmu.Interface(samplerate=10000,
                               blocksize=5000)
    # reference sine
    vec = np.zeros((20000, 1), dtype=np.float32)
    vec[:6000, :] = 1
    vector = asmu.generator.Vector(interface, vec)

    # establish connections
    vector.output().connect(interface.ioutput(ch=1))
    vector.output().connect(interface.ioutput(ch=2))

    # setup vector for callback to write to
    outdata = np.zeros((interface.blocksize, 2), dtype=np.float32)

    # call callback
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    assert outdata[:, 0] == pytest.approx(vec[:5000, 0])

    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    assert outdata[:, 0] == pytest.approx(vec[5000:10000, 0])

    # test reset
    interface.acore.reset()
    # obtain data for frame = 0
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    assert outdata[:, 0] == pytest.approx(vec[:5000, 0])

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, outdata, None, None, None)


if __name__ == "__main__":
    # test_generator_vector(benchmark=None)
    pass
