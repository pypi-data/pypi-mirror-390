import logging

import numpy as np
import pytest

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_effect_adsr(in_buffer: bool, out_buffer: bool, benchmark) -> None:  # type: ignore[no-untyped-def]
    """PyTest for the ADSR effect, with "lin" scale and for all buffer settings."""
    attack = 0.1
    decay = 0.2
    sustain = 0.6
    release = 0.1
    # create objects
    interface = asmu.Interface(samplerate=44100,
                               blocksize=1024)
    const = asmu.generator.Constant(interface, 1)
    adsr = asmu.effect.ADSR(interface,
                            attack,
                            decay,
                            sustain,
                            release,
                            in_buffer=in_buffer,
                            out_buffer=out_buffer)

    # establish connections
    const.output().connect(adsr.input())
    adsr.output().connect(interface.ioutput(ch=1))

    # setup vector for callback to write to
    outdata = np.zeros((interface.blocksize, 1), dtype=np.float32)

    # call callback twice, nothing should happen
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    assert np.allclose(outdata, 0)
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    assert np.allclose(outdata, 0)

    # now start the ramp
    adsr.start()
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
    # the ramp should reach 1 after attack seconds, so after a frame we get:
    value = 1/attack/interface.samplerate*interface.blocksize
    assert outdata[-1] == pytest.approx(value)

    # after some calls we expect to reach peak and settle on sustain
    peak_reached = False
    sustain_reached = False
    for _ in range(30):
        interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
        if np.max(outdata) == pytest.approx(1):
            peak_reached = True
        if peak_reached and outdata[-1] == pytest.approx(sustain):
            sustain_reached = True
            break
    assert peak_reached
    assert sustain_reached

    # now start the decay
    adsr.release()
    zero_reached = False
    for _ in range(10):
        interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
        if outdata[-1] == pytest.approx(0):
            zero_reached = True
            break
    assert zero_reached

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, outdata, None, None, None)


if __name__ == "__main__":
    test_effect_adsr(True, False, None)
