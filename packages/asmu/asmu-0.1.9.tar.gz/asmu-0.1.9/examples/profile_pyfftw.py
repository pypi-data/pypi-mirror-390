"""Profiling example for different fft libraries."""
# mkl_fft was tested but considerably slower than numpy scipy
# https://github.com/IntelPython/mkl_fft

import ducc0
import numpy as np
import pyfftw
import scipy as sp

BLOCKSIZE = 1024


# kernprof -l -v .\profile_pyfftw.py
# @profile
def main():
    indata32 = np.zeros((BLOCKSIZE, 1), dtype=np.float32)

    outdata64_numpy = np.zeros((int(BLOCKSIZE/2+1), 1), dtype=np.complex64)
    outdata64_scipy = np.zeros((int(BLOCKSIZE/2+1), 1), dtype=np.complex64)
    outdata64_fftw = pyfftw.zeros_aligned((int(BLOCKSIZE/2+1), 1), dtype=np.complex64)
    outdata64_ducc0 = np.zeros((int(BLOCKSIZE/2+1), 1), dtype=np.complex64)

    rng = np.random.default_rng()
    rng.standard_normal((BLOCKSIZE, 1), dtype=np.float32, out=indata32)
    print(indata32.shape, outdata64_numpy.shape)

    # numpy
    np.fft.rfft(indata32, axis=0, norm="forward", out=outdata64_numpy)

    # scipy
    outdata64_scipy[:] = sp.fft.rfft(indata32, axis=0, norm="forward")

    # pyfftw extra setup
    indata32_fftw = pyfftw.empty_aligned((BLOCKSIZE, 1), dtype=np.float32)
    fftw = pyfftw.FFTW(indata32_fftw, outdata64_fftw, axes=(0, ), direction="FFTW_FORWARD", flags=("FFTW_MEASURE", ))
    scale = np.complex64(1/BLOCKSIZE)

    # pyfftw
    indata32_fftw[:] = indata32  # this copy can not be removed, because the rfft alogrithm destroys the input array
    fftw.execute()
    outdata64_fftw *= scale  # this is not needed allways!

    # ducc0
    ducc0.fft.r2c(indata32, axes=(0, ), inorm=2, out=outdata64_ducc0)

    # print
    print(f"NUMPY\n{outdata64_numpy[:10]}")
    print(f"SCIPY\n{outdata64_scipy[:10]}")
    print(f"FFTW\n{outdata64_fftw[:10]}")
    print(f"DUCC0\n{outdata64_ducc0[:10]}")

    assert np.allclose(outdata64_numpy, outdata64_scipy)
    assert np.allclose(outdata64_numpy, outdata64_fftw)
    assert np.allclose(outdata64_numpy, outdata64_ducc0)


if __name__ == "__main__":
    main()
