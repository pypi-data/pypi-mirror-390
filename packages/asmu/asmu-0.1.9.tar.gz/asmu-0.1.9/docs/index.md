---
hide:
  - toc
---
{! ../README.md !}


## Class structure

!!! quote "General philosophy"
    **asmu** uses a two layer structure:

    - **Audio Layer:** [ACore](api/asmu_acore.md) classes with minimal functionality that run in the audio thread and are repeatedly called by the callback function.
    - **User Layer:** [Processors](api/asmu_processor.md) with [Inputs and Outputs](api/asmu_io.md) that are connected like analog audio devices. These classes also contain (slower) convenience functions.

In general each Processor houses an ACore class. These *blocks* can be connected to send and receive time-signal audio buffers with arbitrary `np.float32` unit between [-1, 1].
This simplifies the buffer structure and allows correct read/write from/to audio files.

If real units are required, scaling factors are stored in the respective interface analog input (IInput) and interface analog output (IOutput) and can be applied where needed (but never on the buffer itself).

![Class Structure](imgs/classes.svg)
