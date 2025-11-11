import pytest
from pytest_mock import MockerFixture

import asmu.acore
import asmu.processor


def test_processor_analyzer_(mocker: MockerFixture) -> None:
    # create mocks
    aanalyzer = mocker.Mock(spec=asmu.acore.AAnalyzer)
    interface = mocker.Mock(spec=asmu.Interface)
    interface.analyzers = ()
    output = mocker.Mock(spec=asmu.io.Output)
    output.idx = 2
    input = mocker.Mock(spec=asmu.io.Input)
    input.connected_output = output
    input2 = mocker.Mock(spec=asmu.io.Input)
    input2.connected_output = None

    # cut
    analyzer = asmu.processor.Analyzer(aanalyzer,
                                       interface,
                                       (input, ),
                                       in_update=False)
    assert interface.analyzers == (analyzer, )

    # test properties
    assert analyzer.acore == aanalyzer

    assert analyzer.inputs == (input, )
    analyzer.inputs = (input, input2)
    assert analyzer.inputs == (input, input2)
    # test if update_acore() was called
    assert aanalyzer.in_as == ((output.acore, 2), (None, 0))
    analyzer.inputs = (input, )

    assert analyzer.in_update is False
    analyzer.in_update = True
    assert analyzer.in_update is True
    analyzer.in_update = False

    # test methods
    assert analyzer.input(0) == input
    with pytest.raises(IndexError):
        analyzer.input(1)

    analyzer.update_acore()
    assert aanalyzer.in_as == ((output.acore, 2), )

    analyzer.disconnect()
    output.disconnect.assert_called_once_with(input)
    assert len(analyzer.inputs) == 0
    assert interface.analyzers == ()

    # test with in_update
    analyzer.in_update = True
    analyzer.inputs = (input, )

    # test methods
    mock_output = mocker.patch("asmu.processor.Input", autospec=True)
    assert analyzer.input(1) is mock_output.return_value
    mock_output.assert_called_once_with(analyzer)
