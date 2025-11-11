"""File that stores useful commands and a small test code for profiling.
To run uncomment the function of interest at the bottom and rund the file with
`kernprof -l -v ./profiling.py` or
`python -m memory_profiler ./profiling.py`."""
import numpy as np
import plotext

# check for line_profiler or memory_profiler in the local scope, both
# are injected by their respective tools or they're absent
# if these tools aren't being used (in which case we need to substitute
# a dummy @profile decorator)
if 'prof' not in dir() and 'profile' not in dir():
    def profile(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner


# @profile
def copy_test():
    a = np.ones((100000, 2))
    b = np.zeros(100000)

    np.copyto(b, a[:, 1])
    b[:] = a[:, 1]


# @profile
def slice_test():
    buffer = np.ones((100000, 2))
    data = np.zeros(20000)
    data2 = np.zeros((20000, 1))

    np.copyto(buffer[500:20500, 1], data)
    buffer[500:20500, 1] = data

    np.copyto(buffer[500:20500, 1:2], data2)
    buffer[500:20500, 1:2] = data2


# @profile
def random_test():
    buffer = np.zeros(20000)

    rng = np.random.default_rng()
    # normal distribution (slow)
    rng.standard_normal(20000, out=buffer, dtype=np.float64)
    # uniform distribution (faster)
    rng.random(20000, dtype=np.float64, out=buffer)
    buffer -= 0.5  # center

    # normalize (slow)
    norm = np.max(np.abs(buffer))
    # normalize (faster)
    norm = np.abs(buffer).max()
    buffer /= norm


# @profile
def multiply_test():
    a = np.ones(20000)
    b = np.ones(20000)*5

    a[:] *= 5
    a *= 5

    a[:] *= b
    a *= b


@profile
def plotext_test():
    buffer = np.zeros(20000)
    rng = np.random.default_rng()
    rng.standard_normal(20000, out=buffer, dtype=np.float64)

    plotext.title("Time Signal")
    plotext.grid(True, True)
    plotext.clc()  # clear color

    # plot
    for _ in range(10):
        plotext.cld()
        plotext.clt()
        plotext.plot(buffer[::10], marker="braille")
        plotext.show()


if __name__ == "__main__":
    # copy_test()
    # slice_test()
    # random_test()
    # multiply_test()
    plotext_test()
