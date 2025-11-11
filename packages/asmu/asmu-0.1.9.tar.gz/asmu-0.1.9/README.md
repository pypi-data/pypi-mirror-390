# Acoustic Signal Measurement Utilities

The **asmu** Python package enables multichannel real-time audio playback, processing and recording. It is implemented in pure Python with a few additional packages:

- [numpy](https://pypi.org/project/numpy/) - Is the fundamental package for scientific computing, array manipulation and signal processing.
- [sounddevice](https://pypi.org/project/sounddevice/) - Is a Python wrapper for the [PortAudio](https://www.portaudio.com/) functions. It is used for the communication with the soundcard or audio interface.
- [soundfile](https://pypi.org/project/soundfile/) - Is an audio library to read and write sound files through [libsndfile](http://www.mega-nerd.com/libsndfile/).
- [pyFFTW](https://pypi.org/project/pyFFTW/) - A pythonic wrapper around [FFTW](https://www.fftw.org/), presenting a unified interface for all the supported transforms.

The main focus of **asmu** is modularity and easy expandability. It provides a few base classes, to implement nearly every "audio processor". Additionally, **asmu** offer some pre implemented audio processors, that can be used right away.


## Quick links

- [Documentation](https://felhub.gitlab.io/asmu)
- [Repository](https://gitlab.com/felhub/asmu)
- [PyPi](https://pypi.org/project/asmu)


## How to cite

If you use this software in your academic work, please cite it using the following reference:

    @misc{huber_asmu_2025,
    title      = {Acoustic Signal Measurement Utilities},
    shorttitle = {asmu},
    author     = {Huber, Felix},
    year       = {2025},
    copyright  = {GPLv3}
    url        = {https://gitlab.com/felhub/asmu}
    }

Citations help support the project and make it more visible to the community.
