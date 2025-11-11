"""The Hello World of audio software - play a sine wave."""
import time

import asmu

interface = asmu.Interface()
sine = asmu.generator.Sine(interface, 250)

sine.output().connect(interface.ioutput(ch=1))
sine.output().connect(interface.ioutput(ch=2))

with interface.start():
    time.sleep(5)
