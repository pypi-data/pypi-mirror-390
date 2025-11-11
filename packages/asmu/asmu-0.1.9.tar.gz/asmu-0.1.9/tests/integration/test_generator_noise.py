import logging

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLOT = False


def test_generator_noise(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the Noise Generator."""
    # create objects
    interface = asmu.Interface(samplerate=10000,
                               blocksize=5000)
    # reference sine
    white = asmu.generator.Noise(interface, weight="white")
    # pink noise is slow due to fft/ifft filtering
    pink = asmu.generator.Noise(interface, weight="pink")

    # establish connections
    white.output().connect(interface.ioutput(ch=1))
    pink.output().connect(interface.ioutput(ch=2))

    # setup vector for callback to write to
    outdata = np.zeros((interface.blocksize, 2), dtype=np.float32)

    # call callback once (_inc() is not called)
    for i in range(10):
        interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]

    logger.info(f"mean_white = {np.mean(outdata[:, 0])}, mean_pink = {np.mean(outdata[:, 1])}")

    assert np.max(outdata[:, 0]) <= 1
    assert np.min(outdata[:, 0]) >= -1
    assert np.mean(outdata[:, 0]) == pytest.approx(0, abs=0.1)

    assert np.max(outdata[:, 1]) <= 1
    assert np.min(outdata[:, 1]) >= -1
    assert np.mean(outdata[:, 1]) == pytest.approx(0, abs=0.1)

    if PLOT:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(outdata[:, 0], label="white")
        ax.plot(outdata[:, 1], label="pink")
        ax.legend()
        plt.show()

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, outdata, None, None, None)


if __name__ == "__main__":
    # test_generator_noise(benchmark=None)
    pass
