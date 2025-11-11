import numpy as np
from pytest_mock import MockerFixture

import asmu.acore


def test_generator_constant_(mocker: MockerFixture) -> None:
    # create mocks
    interface = mocker.Mock(spec=asmu.Interface)
    interface.blocksize = 512
    interface.start_frame = 1312

    # cut
    constant = asmu.generator.Constant(interface, 0.161)

    # test properties
    aconstant = constant.acore
    assert isinstance(aconstant, asmu.acore.AGenerator)

    # test methods
    outdata = np.empty(interface.blocksize, dtype=np.float32)
    ch = 0
    frame = 0
    aconstant.upstream(outdata, ch, frame)
    assert np.allclose(outdata, 0.161)
