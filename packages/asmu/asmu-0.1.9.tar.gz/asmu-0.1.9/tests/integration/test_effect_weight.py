import logging

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLOT = False


def test_effect_weight(in_buffer: bool, out_buffer: bool, benchmark) -> None:  # type: ignore[no-untyped-def]
    """PyTest for the Weight Effect for A-weighting inspired by IEC 61672."""
    # create objects
    interface = asmu.Interface(samplerate=44100,
                               blocksize=8192)
    noise = asmu.generator.Noise(interface)
    # a-weight is slow due to fft/ifft filtering
    Aweight = asmu.effect.Weight(interface,
                                 "A",
                                 in_buffer=in_buffer,
                                 out_buffer=out_buffer)
    fft = asmu.analyzer.FFT(interface)

    # establish connections
    noise.output().connect(Aweight.input())
    Aweight.output().connect(fft.input(0))
    noise.output().connect(fft.input(1))

    # repeatedly call callback
    n = 0
    tf = None
    while n < 100:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        rfft = fft.get_rfft(block=False)
        if rfft is not False:
            if tf is None:
                tf = rfft[:, 0] / rfft[:, 1]
            else:
                tf += rfft[:, 0] / rfft[:, 1]
            n += 1

    # compute transfer function
    assert tf is not None
    tf /= n

    def f2i(f: float) -> int:
        return int(np.argmin(np.abs(fft.frequencies - f)))

    # allowed deviation given in IEC 61672 5.5.9 (Hz, dB)
    # currently only high freqs, b.c. current implementation does not work for low freqs
    fs = [125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    reldBs = [1, 1, 1, 1, 1, 1, 1.5, 2.5]

    # curve used in Weight
    acurve = np.abs(Aweight.get_weight(fft.frequencies))

    # deviation diven in 5.5.9
    assert np.abs(tf[f2i(1000)]) == pytest.approx(1, rel=(10**(0.2/20)-1))
    assert acurve[f2i(1000)] == pytest.approx(1, rel=(10**(0.2/20)-1))

    for f, reldB in zip(fs, reldBs):
        fidx = f2i(f)
        value = np.abs(tf[fidx])
        logger.info(f"tf({f}Hz) = {value}")
        assert value == pytest.approx(acurve[fidx], rel=(10**(reldB/20)-1))

    if PLOT:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.loglog(fft.frequencies, np.abs(tf))
        ax.loglog(fft.frequencies, acurve)
        bfs = Aweight.frequencies
        ax.loglog(bfs, np.abs(Aweight.get_weight(bfs)))
        plt.show()

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    test_effect_weight(True, False, benchmark=None)
