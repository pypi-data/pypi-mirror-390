"""This example calibrates the latency between given input and output."""
import time
from typing import TYPE_CHECKING

from asmu_utils.correlation import get_corrs_sampleshifts

import asmu

if TYPE_CHECKING:
    from asmu.typing import ABuffer


def calibrate_latency(interface: "asmu.Interface",
                      iinput: "asmu.io.IInput",
                      ioutput: "asmu.io.IOutput",
                      frequency: float = 1000,
                      periods: int = 10) -> int:
    sineburst = asmu.generator.SineBurst(interface, frequency, periods)
    with asmu.AFile(interface, mode="w+", channels=2, temp=True) as afile:
        rec = asmu.analyzer.Recorder(interface, afile)

        sineburst.output().connect(ioutput)
        sineburst.output().connect(rec.input(0))
        iinput.connect(rec.input(1))

        stream = interface.start(end_frame=16)
        while stream.active:
            time.sleep(0.1)
        stream.stop()
        stream.close()

        data: ABuffer = afile.data  # type: ignore

    corrs, shifts = get_corrs_sampleshifts(data,
                                           data[:, 0],
                                           round(periods / frequency * interface.samplerate))
    assert shifts[0] == 0
    return int(shifts[1])


if __name__ == "__main__":
    in_ch = 1
    out_ch = 1
    asetup = asmu.ASetup("mysetup.asmu")
    interface = asmu.Interface(asetup)

    latency = calibrate_latency(interface,
                                interface.iinput(ch=in_ch),
                                interface.ioutput(ch=out_ch))
    print(f"Found latency = {latency}")
    ilatency = interface.get_latency()
    print(f"Interface internal latency = {ilatency}")

    if input("Save setup? (y|n)") == "y":
        interface.latency = latency
        asetup.save()
