import logging

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_analyzer_fft_tf(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the FFT Analyzer.
    Test the fft by computing a transfer function between two scaled noise functions."""
    gain = 0.25
    # create objects
    interface = asmu.Interface(samplerate=44100,
                               blocksize=192)
    # reference noise
    noise = asmu.generator.Noise(interface)
    gain_b = asmu.effect.Gain(interface, gain, in_buffer=False, out_buffer=False)
    fft = asmu.analyzer.FFT(interface)

    # establish connections
    noise.output().connect(gain_b.input())

    noise.output().connect(fft.input(0))
    noise.output().connect(fft.input(1))
    gain_b.output().connect(fft.input(2))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        rfft = fft.get_rfft(block=False)
        if rfft is not False:
            break

    assert (isinstance(rfft, np.ndarray))

    # compute transfer function
    tf = rfft[:, 1:] / rfft[:, [0]]

    # check if transfer functions are correct
    assert np.mean(np.abs(tf[:, 0])) == pytest.approx(1)
    assert np.mean(np.abs(tf[:, 1])) == pytest.approx(gain)
    # reduced precision due to float32
    assert np.mean(np.angle(tf[:, 0])) == pytest.approx(0, abs=1e-6)
    assert np.mean(np.angle(tf[:, 1])) == pytest.approx(0, abs=1e-6)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


def test_analyzer_fft_sine(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the FFT Analyzer.
    Test the accuracy of the fft based rms average.
    This test only performs well, if the RMS samples are a multiple of the sine period length.
    We ensure this by setting samples=int(interface.samplerate/freq)
    """
    gain = 0.25
    freq = 1000
    # create objects
    interface = asmu.Interface(samplerate=10*freq,
                               blocksize=100)
    sine = asmu.generator.Sine(interface, freq, out_buffer=out_buffer)
    gain_b = asmu.effect.Gain(interface, gain, in_buffer=False, out_buffer=False)
    fft = asmu.analyzer.FFT(interface)

    # establish connections
    sine.output().connect(gain_b.input())

    sine.output().connect(fft.input(0))
    gain_b.output().connect(fft.input(1))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        rfft = fft.get_rfft(block=False)
        if rfft is not False:
            break

    rms = fft.rfft2rms(rfft)
    fs, peaks = fft.rfft2peak(rfft)

    # check if peaks are correct
    logger.info(f"rms = {rms}, peaks = {peaks}, fs = {fs}")
    assert rms[0] == pytest.approx(1/np.sqrt(2))
    assert rms[1] == pytest.approx(gain/np.sqrt(2))
    assert peaks[0] == pytest.approx(1)
    assert peaks[1] == pytest.approx(gain)
    assert fs[0] == pytest.approx(freq)
    assert fs[1] == pytest.approx(freq)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


def test_analyzer_fft_const(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the FFT Analyzer.
    Test the accuracy of the fft based rms average.
    This test only performs well, if the RMS samples are a multiple of the sine period length.
    We ensure this by setting samples=int(interface.samplerate/freq)
    """
    value = 0.25
    # create objects
    interface = asmu.Interface(samplerate=10000,
                               blocksize=192)
    const = asmu.generator.Constant(interface, value)

    # with other window functions this test is not stable
    win = np.ones(interface.samplerate)
    fft = asmu.analyzer.FFT(interface, win=win)

    # establish connections
    const.output().connect(fft.input(0))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        rfft = fft.get_rfft(block=False)
        if rfft is not False:
            break

    rms = fft.rfft2rms(rfft)
    fs, peaks = fft.rfft2peak(rfft)

    # check if peaks are correct
    logger.info(f"rms = {rms}, peaks = {peaks}, fs = {fs}")
    assert rms[0] == pytest.approx(value, rel=1e-3)
    assert peaks[0] == pytest.approx(value, rel=1e-3)
    assert fs[0] == pytest.approx(0)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


def test_analyzer_fft_noise(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the FFT Analyzer.
    Test the fft by computing a transfer function between two scaled noise functions."""
    # create objects
    interface = asmu.Interface(samplerate=44100,
                               blocksize=192)
    # reference noise
    noise = asmu.generator.Noise(interface)

    # with other window functions this test is not stable
    win = np.ones(interface.samplerate)
    fft = asmu.analyzer.FFT(interface, win=win)
    rms = asmu.analyzer.RMS(interface, len(win))

    # establish connections
    noise.output().connect(fft.input(0))
    noise.output().connect(rms.input(0))

    # repeatedly call callback
    rfft = fft.get_rfft(block=False)
    resrms = rms.get_rms(block=False)
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        if rfft is False:
            rfft = fft.get_rfft(block=False)
        if resrms is False:
            resrms = rms.get_rms(block=False)
        if rfft is not False and resrms is not False:
            break

    assert (isinstance(rfft, np.ndarray))
    assert (isinstance(resrms, np.ndarray))

    fftrms = fft.rfft2rms(rfft)
    # check if rms is equal correct
    logger.info(f"fftrms = {fftrms}, resrms = {resrms}")
    assert fftrms[0] == pytest.approx(resrms[0], rel=1e-3)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    # test_analyzer_fft_tf(benchmark=None)
    # test_analyzer_fft_sine(False, benchmark=None)
    # test_analyzer_fft_const(benchmark=None)
    # test_analyzer_fft_noise(benchmark=None)
    pass
