"""Measure electrical noise of the DUT connected to selceted input."""

import numpy as np

import asmu

PLOT = True


def measure_voltage_noise(interface: "asmu.Interface",
                          in_ch: int,
                          averages: int = 10):

    fft = asmu.analyzer.FFT(interface)
    interface.iinput(ch=in_ch).connect(fft.input())

    rffts = []
    n = 0

    stream = interface.start()
    while n < averages:
        rfft = fft.get_rfft()
        assert rfft is not False, "Timed out."
        rffts.append(rfft)
        n += 1
    stream.stop()
    stream.close()

    cV = interface.iinput(ch=in_ch).cV

    rffts = np.array(rffts)
    rfft = np.mean(rffts, axis=0)

    rms = fft.rfft2rms(rfft)[0]
    dBFS = rms2dBFS(rms)
    print(f"Noise = {dBFS:.2f}dBFS")

    Vrms = rms*cV
    dBu = Vrms2dBu(Vrms)
    asd = np.sqrt(fft.rfft2psd(rfft)[:, 0])*cV

    print(f"Noise = {Vrms:.6f}Vrms ({dBu:.2f}dBu)")

    if PLOT:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.semilogx(fft.frequencies[1:], asd[1:])
        ax.set(xlabel="frequency in Hz",
               ylabel="amplitude spectral density in V/sqrt(Hz)")
        fig.tight_layout()
        plt.show()


def rms2dBFS(rms):
    return 20*np.log10(rms)


def Vrms2dBu(Vrms):
    return 20*np.log10(Vrms/0.775)


if __name__ == "__main__":
    in_ch = 1
    asetup = asmu.ASetup("mysetup.asmu")
    interface = asmu.Interface(asetup=asetup)

    measure_voltage_noise(interface, in_ch)
