from pytest_mock import MockerFixture

import asmu.io


def test_io_output_(mocker: MockerFixture) -> None:
    # create mocks
    processor = mocker.Mock()
    input = mocker.Mock(spec=asmu.io.Input)
    input2 = mocker.Mock(spec=asmu.io.Input)

    # cut
    output = asmu.io.Output(processor)

    # test __bool__
    assert not output

    # test properties
    assert output.inputs == ()
    output.idx
    processor.outputs.index.assert_called_once_with(output)
    assert output.acore == processor.acore

    # test methods
    # connect
    output.connect(input)
    assert output.inputs == (input, )
    assert input.connected_output == output
    processor.update_acore.assert_called_once()
    assert output  # test __bool__ again
    # call with the same input should not change anything
    output.connect(input)
    assert output.inputs == (input, )
    # call with a new input should add it
    output.connect(input2)
    assert output.inputs == (input, input2)
    assert input.connected_output == output
    assert input2.connected_output == output
    assert output  # test __bool__ again

    # disconnect
    processor.update_acore.reset_mock()
    output.disconnect(input)
    assert output.inputs == (input2, )
    assert input.connected_output is None
    processor.update_acore.assert_called_once()
    # call with the same input should not change anything
    assert output.inputs == (input2, )
    # call with last connected input should remove it
    processor.update_acore.reset_mock()
    output.disconnect(input2)
    assert output.inputs == ()
    assert input2.connected_output is None
    processor.update_acore.assert_called_once()
    assert not output  # test __bool__
