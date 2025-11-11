import pytest
from pytest_mock.plugin import MockerFixture

import asmu.acore
import asmu.processor


def test_generator_(mocker: MockerFixture) -> None:
    # create mocks
    agenerator = mocker.Mock(spec=asmu.acore.AGenerator)
    interface = mocker.Mock(spec=asmu.Interface)
    output = mocker.Mock(spec=asmu.io.Output)
    input = mocker.Mock(spec=asmu.io.Input)
    # connect input
    output.inputs = (input, )

    # cut
    generator = asmu.processor.Generator(agenerator,
                                         interface,
                                         (output, ),
                                         out_update=False)

    # test properties
    assert generator.acore == agenerator
    assert generator.outputs == (output, )

    # test methods
    assert generator.output() == output
    with pytest.raises(IndexError):
        generator.output(1)

    generator.update_acore()
    assert agenerator.out_chs == 1  # len(outputs)

    generator.disconnect()
    output.disconnect.assert_called_once_with(input)

    # cut + out_update
    generator = asmu.processor.Generator(agenerator,
                                         interface,
                                         (output, ),
                                         out_update=True)

    # test methods
    mock_output = mocker.patch("asmu.processor.Output", autospec=True)
    assert generator.output(1) is mock_output.return_value
    mock_output.assert_called_once_with(generator)
