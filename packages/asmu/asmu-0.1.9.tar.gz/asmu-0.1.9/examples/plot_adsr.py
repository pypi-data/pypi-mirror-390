"""Simple program to test and visualize the ramp produced by the ADSR effect."""
import matplotlib.pyplot as plt
import numpy as np

import asmu


def plot_adsr():
    # create objects
    interface = asmu.Interface(samplerate=44100,
                               blocksize=1024)
    const = asmu.generator.Constant(interface, 1)
    adsr = asmu.effect.ADSR(interface, 0.1, 0.2, 0.6, 0.1)

    # establish connections
    const.output().connect(adsr.input())
    adsr.output().connect(interface.ioutput(ch=1))

    # inti plot
    fig, ax = plt.subplots()

    # setup vectors
    outdata = np.zeros((interface.blocksize, 1), dtype=np.float32)
    x = np.linspace(0, 1, interface.blocksize)

    # run callback loop
    for i in range(50):
        if i == 5:
            adsr.start()
            ax.vlines(i, 0, 1, color="k", label="start()")
        if i == 40:
            adsr.release()
            ax.vlines(i, 0, 1, linestyles="--", color="k", label="release()")
        interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]
        ax.plot(x + i, outdata)

    # setup plot and show
    ax.set(title="ADSR for attack = 0.1s, decay = 0.2s, sustain = 0.6, release = 0.1s", xlabel="frames", ylabel="gain")
    ax.grid()
    ax.legend()

    fig.tight_layout()
    fig.savefig("docs/imgs/plot_adsr.png", dpi=300)

    # Uncomment this if you want to see the plot
    # plt.show()


if __name__ == "__main__":
    plot_adsr()
