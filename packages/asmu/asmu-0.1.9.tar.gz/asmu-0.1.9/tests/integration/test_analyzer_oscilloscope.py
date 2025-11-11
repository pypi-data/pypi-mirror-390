import logging

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_analyzer_oscilloscope(benchmark):  # type: ignore[no-untyped-def]
    """PyTest for the Oscilloscope Analyzer.
    Test rising_edge and falling_edge trigger for sine signal."""
    interface = asmu.Interface()
    gen = asmu.generator.Sine(interface, 20)
    osc_r = asmu.analyzer.Oscilloscope(interface,
                                       xpos=2000,
                                       ythreshold=0.1,
                                       mode="rising_edge",
                                       buffersize=4000)
    osc_f = asmu.analyzer.Oscilloscope(interface,
                                       xpos=2000,
                                       ythreshold=0,
                                       mode="falling_edge",
                                       buffersize=4000)
    gen.output().connect(osc_r.input())
    gen.output().connect(osc_f.input())

    # obtain data
    buf_r = osc_r.get_buffer(block=False)
    buf_f = osc_f.get_buffer(block=False)
    while buf_r is False or buf_f is False:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        if buf_r is False:
            buf_r = osc_r.get_buffer(block=False)
        if buf_f is False:
            buf_f = osc_f.get_buffer(block=False)

    # rising edge with threshold 0.1
    assert buf_r.shape == (4000, 1)
    assert buf_r[2000-1, 0] < 0.1
    assert buf_r[2000, 0] >= 0.1

    # falling edge with threshold 0
    assert buf_f.shape == (4000, 1)
    assert buf_f[2000-1, 0] > 0
    assert buf_f[2000, 0] <= 0

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    # test_analyzer_oscilloscope(benchmark=None)
    pass
