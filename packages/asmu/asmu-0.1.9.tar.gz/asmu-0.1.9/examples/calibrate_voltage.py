"""This example can be used to calibrate an Interface IInput and IOutput channel for voltage."""
import asmu


def calibrate_iinput_cV(interface: "asmu.Interface",
                        iinput: "asmu.io.IInput",
                        Vp: float = 1,
                        gain: float = 20,
                        averages: int = 10):
    """Calibrate the given input for voltage.

    Args:
        interface: Reference to an Interface instance.
        iinput: The iinput to calibrate.
        Ap: The voltage amplitude in V used for calibration.
        gain: The gain set on the interface (stored in iinput).
        averages: Averages used for the calibration.
    """
    calcV = asmu.analyzer.CalIInput(interface, Vp, "Vp", gain=gain, averages=averages)
    iinput.connect(calcV.input())

    print(f"Connect iinput channel {iinput.channel} to {calcV.actual:.1f}V peak sine generator.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcV.evaluate()
    while result is False:
        result = calcV.evaluate()
    stream.stop()
    stream.close()
    calcV.disconnect()
    print(result)
    print(f"cV = {iinput.cV}")
    print(f"fV = {iinput.fV}")
    print(f"dateV = {iinput.dateA}")


def calibrate_ioutput_cV(interface: "asmu.Interface",
                         iinput: "asmu.io.IInput",
                         ioutput: "asmu.io.IOutput",
                         outgain: float = 0.01,
                         averages: int = 10):
    """Calibrate the given ioutput for voltage, by using the given calibrated iinput.

    Args:
        interface: Reference to an Interface instance.
        iinput: The pre calibrated iinput used as reference for calibration.
        ioutput: The ioutput to calibrate.
        outgain: The calibration gain.
        averages: Averages used for the calibration.
    """
    sine = asmu.generator.Sine(interface, 1000)
    gain = asmu.effect.Gain(interface, outgain)
    calcV = asmu.analyzer.CalIOutput(interface, outgain, "V", ioutput, gain=0, averages=averages)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)
    iinput.connect(calcV.input())

    print(f"Connect iinput channel {iinput.channel} "
          f"to output channel {ioutput.channel}.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcV.evaluate()
    while result is False:
        result = calcV.evaluate()
    stream.stop()
    stream.close()
    calcV.disconnect()
    print(f"cV = {ioutput.cV}")
    print(f"fV = {ioutput.fV}")
    print(f"dateV = {ioutput.dateA}")


def generate_sine(interface: "asmu.Interface",
                  ioutput: "asmu.io.IOutput",
                  freq: float = 1000,
                  Vp: float = 0.5):
    """Generate a sinewave on the given ioutput.

    Args:
        interface: Reference to an Interface instance.
        ioutput: The ioutput used for signal generation.
        freq: The frequency of the generator.
        Vp: Set the voltage amplitude of the generator in V.
    """
    sine = asmu.generator.Sine(interface, freq)

    cV = interface.ioutput().cV
    gain = asmu.effect.Gain(interface, Vp / cV)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)

    print("Starting sine generator...")
    stream = interface.start()
    print(f"You now should measure a {Vp:.2f}Vp sine wave "
          f"on the output channel {ioutput.channel}.")
    input("\tPress ENTER to stop.")
    stream.stop()
    stream.close()


if __name__ == "__main__":
    in_ch = 1
    out_ch = 1
    asetup = asmu.ASetup("mysetup.asmu")
    interface = asmu.Interface(device="ASIO MADIface USB",
                               blocksize=1024,
                               samplerate=44100)
    asetup.interface = interface

    calibrate_iinput_cV(interface,
                        interface.iinput(ch=in_ch))

    calibrate_ioutput_cV(interface,
                         interface.iinput(ch=in_ch),
                         interface.ioutput(ch=out_ch))

    if input("Save setup? (y|n)") == "y":
        asetup.save()

    if input("Start generator? (y|n)") == "y":
        generate_sine(interface,
                      interface.ioutput(ch=out_ch))
