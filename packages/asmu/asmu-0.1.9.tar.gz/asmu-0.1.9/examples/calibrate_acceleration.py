"""This example can be used to calibrate an Interface IInput and IOutput channel for acceleration."""
import asmu


def calibrate_iinput_cA(interface: "asmu.Interface",
                        iinput: "asmu.io.IInput",
                        Ap: float = 1,
                        gain: float = 20,
                        averages: int = 10):
    """Calibrate the given input for acceleration.

    Args:
        interface: Reference to an Interface instance.
        iinput: The iinput to calibrate.
        Ap: The acceleration amplitude in m/s^2 used for calibration.
        gain: The gain set on the interface (stored in iinput).
        averages: Averages used for the calibration.
    """
    calcA = asmu.analyzer.CalIInput(interface, Ap, "Ap", gain=gain, averages=averages)
    iinput.connect(calcA.input())

    print(f"Connect iinput channel {iinput.channel} to {calcA.actual:.1f}m/s^2 peak sine calibrator.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcA.evaluate()
    while result is False:
        result = calcA.evaluate()
    stream.stop()
    stream.close()
    calcA.disconnect()
    print(f"cA = {iinput.cA}")
    print(f"fA = {iinput.fA}")
    print(f"dateA = {iinput.dateA}")


def calibrate_ioutput_cA(interface: "asmu.Interface",
                         iinput: "asmu.io.IInput",
                         ioutput: "asmu.io.IOutput",
                         outgain: float = 0.01,
                         averages: int = 10):
    """Calibrate the given ioutput for acceleration, by using the given calibrated iinput.

    Args:
        interface: Reference to an Interface instance.
        iinput: The pre calibrated iinput used as reference for calibration.
        ioutput: The ioutput to calibrate.
        outgain: The calibration gain.
        averages: Averages used for the calibration.
    """
    sine = asmu.generator.Sine(interface, 1000)
    gain = asmu.effect.Gain(interface, outgain)
    calcA = asmu.analyzer.CalIOutput(interface, outgain, "A", ioutput, gain=0, averages=averages)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)
    iinput.connect(calcA.input())

    print(f"Place the sensor on iinput channel {iinput.channel} "
          f"on the trancducer driven by output channel {ioutput.channel}.")
    input("\tPress ENTER to start.")
    stream = interface.start()
    result = calcA.evaluate()
    while result is False:
        result = calcA.evaluate()
    stream.stop()
    stream.close()
    calcA.disconnect()
    print(result)
    print(f"cA = {ioutput.cA}")
    print(f"fA = {ioutput.fA}")
    print(f"dateA = {ioutput.dateA}")


def generate_sine(interface: "asmu.Interface",
                  ioutput: "asmu.io.IOutput",
                  freq: float = 1000,
                  Ap: float = 0.5):
    """Generate a sinewave on the given ioutput.

    Args:
        interface: Reference to an Interface instance.
        ioutput: The ioutput used for signal generation.
        freq: The frequency of the generator.
        Ap: Set the acceleration amplitude of the generator in m/s^2.
    """
    sine = asmu.generator.Sine(interface, freq)

    cA = interface.ioutput().cA
    gain = asmu.effect.Gain(interface, Ap / cA)
    sine.output().connect(gain.input())
    gain.output().connect(ioutput)

    print("Starting sine generator...")
    stream = interface.start()
    print(f"You now should measure a {Ap:.2f}m/s^2 sine wave "
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

    calibrate_iinput_cA(interface,
                        interface.iinput(ch=in_ch))

    calibrate_ioutput_cA(interface,
                         interface.iinput(ch=in_ch),
                         interface.ioutput(ch=out_ch))

    if input("Save setup? (y|n)") == "y":
        asetup.save()

    if input("Start generator? (y|n)") == "y":
        generate_sine(interface,
                      interface.ioutput(ch=out_ch))
