"""Use your keyboard to play a sine organ."""
import time

import keyboard

import asmu

KEY_MAP = {
    "a": 261.63,  # C4
    "w": 277.18,  # C#4 / Db4
    "s": 293.66,  # D4
    "e": 311.13,  # D#4 / Eb4
    "d": 329.63,  # E4
    "f": 349.23,  # F4
    "t": 369.99,  # F#4 / Gb4
    "g": 392.00,  # G4
    "z": 415.30,  # G#4 / Ab4
    "h": 440.00,  # A4
    "u": 466.16,  # A#4 / Bb4
    "j": 493.88,  # B4
    "k": 523.25,  # C5
}

interface = asmu.Interface(blocksize=64)
sum = asmu.effect.Sum(interface)
envs = {}
for idx, (key, freq) in enumerate(KEY_MAP.items()):
    sine = asmu.generator.Sine(interface, freq)
    adsr = asmu.effect.ADSR(interface, 0.1, 0.2, 0.6, 0.1, scale="log")
    sine.output().connect(adsr.input())
    adsr.output().connect(sum.input(idx))
    envs[key] = adsr
sum.output().connect(interface.ioutput(ch=1))
sum.output().connect(interface.ioutput(ch=2))


def hook(event):
    if event.event_type == "down":
        try:
            env = envs[event.name]
            if not env.running():
                env.start()
        except KeyError:
            pass
        return
    if event.event_type == "up":
        try:
            envs[event.name].release()
        except KeyError:
            pass
        return


keyboard.hook(hook)

stream = interface.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    stream.stop()
    stream.close()
