import plotext

import asmu

threshold = 0.01
in_ch = 1  # input channel

interface = asmu.Interface()
osc = asmu.analyzer.Oscilloscope(interface,
                                 xpos=int(interface.samplerate/2),
                                 ythreshold=threshold,
                                 mode="rising_edge",
                                 buffersize=interface.samplerate)
interface.iinput(ch=in_ch).connect(osc.input())

plotext.title("Osciloscope")
plotext.grid(True, True)
plotext.clc()  # clear color

stream = interface.start()
try:
    buf = osc.get_buffer(block=False)
    while True:  # endless loop -> auto trigger mode
        while buf is False:
            buf = osc.get_buffer(block=False)
        # plot
        plotext.cld()
        plotext.clt()
        plotext.plot(buf[::10, 0], marker="braille")
        plotext.show()
        buf = False
except KeyboardInterrupt:
    stream.stop()
    stream.close()
