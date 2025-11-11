import numpy as np
import plotext

import asmu

in_ch = 1  # input channel

interface = asmu.Interface()
afft = asmu.analyzer.FFT(interface)
interface.iinput(ch=in_ch).connect(afft.input())

plotext.title("Spectrum")
plotext.xscale("log")
plotext.grid(True, True)
plotext.clc()  # clear color

stream = interface.start()
try:
    while True:
        rfft = afft.get_rfft()
        assert rfft is not False
        # plot
        plotext.cld()
        plotext.clt()
        fft = afft.rfft2fft(rfft)
        plotext.plot(afft.frequencies[1:], np.abs(fft[1:, 0]), marker="braille")
        plotext.show()
        buf = False
except KeyboardInterrupt:
    stream.stop()
    stream.close()
