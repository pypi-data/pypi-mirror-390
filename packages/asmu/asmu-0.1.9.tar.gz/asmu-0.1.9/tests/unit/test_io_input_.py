from pytest_mock import MockerFixture

import asmu.io


def test_io_input_(mocker: MockerFixture) -> None:
    # create mocks
    processor = mocker.Mock()
    output = mocker.Mock(spec=asmu.io.Output)

    # cut
    inpu = asmu.io.Input(processor)

    # test __bool__
    assert not inpu

    # test properties
    assert inpu.connected_output is None

    inpu.connected_output = output
    assert inpu.connected_output == output
    processor.update_acore.assert_called_once()

    # test __bool__
    assert inpu
