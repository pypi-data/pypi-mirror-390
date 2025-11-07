from pigeon_transitions import FunctionMachine, RootMachine
import time
import pytest


@pytest.fixture
def test_machine(mocker):
    class TestFunctionMachine(FunctionMachine):
        def request(self):
            self.request_mock()

        def message_callback(self, topic, msg):
            if msg:
                self.success()

    class TestRootMachine(RootMachine):
        request_mock = mocker.MagicMock()

    test_machine = TestFunctionMachine(retries=3, timeout=0.5)
    root_machine = TestRootMachine(
        states=[
            "Start",
            {
                "name": "Function",
                "children": test_machine,
                "remap": {"Success": "Success"},
            },
            "Success",
        ],
        transitions=[
            {"source": "Start", "dest": "Function", "trigger": "start"},
            {"source": "Success", "dest": "Function", "trigger": "start"},
        ],
        initial="Start",
    )

    return root_machine


def test_failure(test_machine):
    assert test_machine.state == "Start"
    test_machine.start()
    assert test_machine.state == "Function_Request"
    test_machine.request_mock.assert_called()
    test_machine.request_mock.reset_mock()

    start = time.time()
    while test_machine.state != "Function_Failure" and (time.time() - start) < 3:
        pass
    assert abs(time.time() - start - 1.5) < 0.1
    assert test_machine.state == "Function_Failure"

    assert test_machine.request_mock.call_count == 2

    test_machine.request_mock.reset_mock()
    test_machine.resume()

    assert test_machine.state == "Function_Request"
    assert test_machine._get_current_machine()._retries_remaining == 2
    test_machine.request_mock.assert_called()


def test_success(test_machine):
    assert test_machine.state == "Start"
    test_machine.start()
    assert test_machine.state == "Function_Request"
    test_machine.request_mock.assert_called()
    test_machine.request_mock.reset_mock()

    test_machine._message_callback("test_topic", True)

    assert test_machine.state == "Success"
    test_machine.request_mock.assert_not_called()


def test_retry_success(test_machine):
    assert test_machine.state == "Start"
    test_machine.start()
    assert test_machine.state == "Function_Request"
    test_machine.request_mock.assert_called()
    test_machine.request_mock.reset_mock()

    start = time.time()
    while not test_machine.request_mock.called and (time.time() - start) < 1:
        pass
    assert abs(time.time() - start - 0.5) < 0.1
    test_machine.request_mock.assert_called()

    time.sleep(0.01)
    test_machine._message_callback("test_topic", True)

    assert test_machine.state == "Success"


def test_reset(test_machine):
    assert test_machine.state == "Start"
    test_machine.start()
    assert test_machine.state == "Function_Request"
    assert test_machine._get_current_machine()._retries_remaining == 2
    test_machine._message_callback("test_topic", True)
    assert test_machine.state == "Success"
    test_machine.start()
    assert test_machine.state == "Function_Request"
    assert test_machine._get_current_machine()._retries_remaining == 2
