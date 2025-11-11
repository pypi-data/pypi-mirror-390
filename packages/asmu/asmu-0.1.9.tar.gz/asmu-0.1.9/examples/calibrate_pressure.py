"""This example can be used to calibrate an Interface IInput and IOutput channel for pressure."""
from math import sqrt

import asmu


def calibrate_iinput_cPa(interface: "asmu.Interface",
                         iinput: "asmu.io.IInput",
                         spl: float = 94,
                         gain: float = 20,
                         averages: int = 10):
    """Calibrate the given input for pressure.

    Args:
        interface: Reference to an Interface instance.
        iinput: The iinput to calibrate.
        spl: The SPL used for calibration.
        gain: The gain set on the interface (stored in iinput).
        averages: Averages used for the calibration.
    """
    calcPa = asmu.analyzer.CalIInput(interface, spl, "SPL", gain=gain, averages=averages)
    iinput.connect(calcPa.input())

    print(f"Connect iinput channel {iinput.channel} to {calcPa.actual:.1f}dB calibrator.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcPa.evaluate()  # blocking
    while result is False:
        result = calcPa.evaluate()
    stream.stop()
    stream.close()
    calcPa.disconnect()
    print(f"cPa = {iinput.cPa}")
    print(f"fPa = {iinput.fPa}")
    print(f"datePa = {iinput.datePa}")


def calibrate_ioutput_cPa(interface: "asmu.Interface",
                          iinput: "asmu.io.IInput",
                          ioutput: "asmu.io.IOutput",
                          outgain: float = 0.01,
                          averages: int = 10):
    """Calibrate the given ioutput for pressure, by using the given calibrated iinput.

    Args:
        interface: Reference to an Interface instance.
        iinput: The pre calibrated iinput used as reference for calibration.
        ioutput: The ioutput to calibrate.
        outgain: The calibration gain.
        averages: Averages used for the calibration.
    """
    sine = asmu.generator.Sine(interface, 1000)
    gain = asmu.effect.Gain(interface, outgain)
    calcPa = asmu.analyzer.CalIOutput(interface, outgain, "Pa", ioutput, gain=0, averages=averages)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)
    iinput.connect(calcPa.input())

    print(f"Place the sensor on iinput channel {iinput.channel} "
          f"next to the source driven by output channel {ioutput.channel}.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcPa.evaluate()
    while result is False:
        result = calcPa.evaluate()
    stream.stop()
    stream.close()
    calcPa.disconnect()
    print(f"cPa = {ioutput.cPa}")
    print(f"fPa = {ioutput.fPa}")
    print(f"datePa = {ioutput.datePa}")


def generate_sine(interface: "asmu.Interface",
                  ioutput: "asmu.io.IOutput",
                  freq: float = 1000,
                  spl: float = 85):
    """Generate a sinewave on the given ioutput.

    Args:
        interface: Reference to an Interface instance.
        ioutput: The ioutput used for signal generation.
        freq: The frequency of the generator.
        spl: Set the SPL of the generator in dB.
    """
    sine = asmu.generator.Sine(interface, freq)
    Pap = 2e-5 * 10**(spl / 20) * sqrt(2)  # set desired peak amplitude

    cPa = ioutput.cPa
    gain = asmu.effect.Gain(interface, Pap / cPa)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)

    print("Starting sine generator...")
    stream = interface.start()
    print(f"You now should measure a {spl:.2f}dB sine wave "
          f"on the output channel {ioutput.channel}.")
    input("\tPress ENTER to stop.")
    stream.stop()
    stream.close()


if __name__ == "__main__":
    in_ch = 15
    out_ch = 3
    asetup = asmu.ASetup("mysetup.asmu")
    interface = asmu.Interface(device="ASIO MADIface USB",
                               blocksize=1024,
                               samplerate=96000)
    asetup.interface = interface

    calibrate_iinput_cPa(interface,
                         interface.iinput(ch=in_ch))

    calibrate_ioutput_cPa(interface,
                          interface.iinput(ch=in_ch),
                          interface.ioutput(ch=out_ch))

    if input("Save setup? (y|n)") == "y":
        asetup.save()

    if input("Start generator? (y|n)") == "y":
        generate_sine(interface,
                      interface.ioutput(ch=out_ch))
