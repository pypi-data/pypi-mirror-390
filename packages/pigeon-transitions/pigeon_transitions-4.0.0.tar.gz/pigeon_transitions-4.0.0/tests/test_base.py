import pytest
from pigeon_transitions import BaseMachine, RootMachine
import time
import logging
from inspect import currentframe


def test_getattr(mocker):
    test_machine = BaseMachine()
    test_machine._parent = mocker.MagicMock()
    test_machine._parent._parent._parent = None

    assert test_machine.state == test_machine._parent._parent.state


def test_add_machine_states(mocker):
    super_func = mocker.MagicMock()
    mocker.patch("pigeon_transitions.base.Machine._add_machine_states", super_func)
    mocker.patch(
        "pigeon_transitions.base.Machine.get_global_name",
        mocker.MagicMock(return_value="test_name"),
    )
    test_machine = BaseMachine()

    states = mocker.MagicMock()
    test_machine._add_machine_states(states, "test_arg")

    super_func.assert_called_with(states, "test_arg")
    assert states._parent == test_machine
    assert test_machine._children == {"test_name": states}


def test_hierarchy():
    child2 = BaseMachine(
        states=[
            "five",
        ],
        initial="five",
    )

    child1 = BaseMachine(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
            },
        ],
        initial="three",
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
            },
        ],
        initial="one",
    )

    assert machine._parent is None
    assert len(machine._children) == 1
    assert machine._children["two"] is child1

    assert child1._parent is machine
    assert len(child1._children) == 1
    assert child1._children["four"] is child2

    assert child2._parent is child1
    assert len(child2._children) == 0


def test_client_and_current_machine(mocker):
    child2 = BaseMachine(
        states=[
            "five",
        ],
        initial="five",
    )

    child1 = BaseMachine(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
            },
        ],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "next",
            },
        ],
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "next",
            },
        ],
    )
    machine._client = "the_client"

    assert machine.state == "one"
    assert machine.client == machine._client
    assert not child1._current_machine()
    assert child1.client is None
    assert not child2._current_machine()
    assert child2.client is None

    assert machine.next()

    assert machine.state == "two_three"
    assert machine.client == machine._client
    assert child1._current_machine()
    assert child1.client == machine._client
    assert not child2._current_machine()
    assert child2.client is None

    assert machine.next()

    assert machine.state == "two_four_five"
    assert machine.client == machine._client
    assert child1._current_machine()
    assert child1.client == machine._client
    assert child2._current_machine()
    assert child2.client == machine._client


def test_on_machine_enter_exit(mocker):
    class Child(BaseMachine):
        def __init__(self, **args):
            self.test_enter = mocker.MagicMock()
            self.test_exit = mocker.MagicMock()
            super().__init__(**args)

    child3 = Child(
        states=[
            "eight",
            "nine",
            "ten",
        ],
        initial="eight",
        on_enter="test_enter",
        on_exit="test_exit",
        transitions=[
            {
                "source": "eight",
                "dest": "nine",
                "trigger": "change",
            },
            {
                "source": "nine",
                "dest": "ten",
                "trigger": "change",
            },
        ],
    )

    child2 = Child(
        states=[
            {
                "name": "five",
                "children": child3,
                "remap": {
                    "ten": "six",
                },
            },
            "six",
        ],
        initial="five",
        on_enter="test_enter",
        on_exit="test_exit",
    )

    child1 = Child(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
                "remap": {
                    "six": "seven",
                },
            },
            "seven",
        ],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "go",
            },
        ],
        on_enter="test_enter",
        on_exit="test_exit",
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
                "remap": {
                    "seven": "one",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
            {
                "source": "one",
                "dest": "two_four_five",
                "trigger": "jump",
            },
        ],
    )

    child1.test_enter.assert_not_called()
    child2.test_enter.assert_not_called()
    child3.test_enter.assert_not_called()

    child1.test_exit.assert_not_called()
    child2.test_exit.assert_not_called()
    child3.test_exit.assert_not_called()

    assert machine.start()
    assert machine.state == "two_three"

    child1.test_enter.assert_called_once()
    child2.test_enter.assert_not_called()
    child3.test_enter.assert_not_called()

    child1.test_exit.assert_not_called()
    child2.test_exit.assert_not_called()
    child3.test_exit.assert_not_called()

    assert machine.go()
    assert machine.state == "two_four_five_eight"

    child1.test_enter.assert_called_once()
    child2.test_enter.assert_called_once()
    child3.test_enter.assert_called_once()

    child1.test_exit.assert_not_called()
    child2.test_exit.assert_not_called()
    child3.test_exit.assert_not_called()

    assert machine.change()
    assert machine.state == "two_four_five_nine"

    child1.test_enter.assert_called_once()
    child2.test_enter.assert_called_once()
    child3.test_enter.assert_called_once()

    child1.test_exit.assert_not_called()
    child2.test_exit.assert_not_called()
    child3.test_exit.assert_not_called()

    assert machine.change()
    assert machine.state == "one"

    child1.test_enter.assert_called_once()
    child2.test_enter.assert_called_once()
    child3.test_enter.assert_called_once()

    child1.test_exit.assert_called_once()
    child2.test_exit.assert_called_once()
    child3.test_exit.assert_called_once()

    child1.test_enter.reset_mock()
    child2.test_enter.reset_mock()
    child3.test_enter.reset_mock()

    child1.test_exit.reset_mock()
    child2.test_exit.reset_mock()
    child3.test_exit.reset_mock()

    assert machine.jump()
    assert machine.state == "two_four_five_eight"

    child1.test_enter.assert_called_once()
    child2.test_enter.assert_called_once()
    child3.test_enter.assert_called_once()

    child1.test_exit.assert_not_called()
    child2.test_exit.assert_not_called()
    child3.test_exit.assert_not_called()


def test_on_machine_re_enter_exit(mocker):
    class Child(BaseMachine):
        def __init__(self, **args):
            self.test_enter = mocker.MagicMock()
            self.test_exit = mocker.MagicMock()
            super().__init__(**args)

    child = Child(
        states=[
            "one",
            "two",
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "go",
            },
        ],
        on_enter="test_enter",
        on_exit="test_exit",
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child,
                "remap": {
                    "two": "two",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
        ],
    )

    assert machine.start()
    assert machine.state == "two_one"

    child.test_enter.assert_called_once()
    child.test_exit.assert_not_called()

    child.test_enter.reset_mock()

    assert machine.go()
    assert machine.state == "two_one"

    child.test_enter.assert_called_once()
    child.test_exit.assert_called_once()


def test_var_to_func():

    class Root(RootMachine):
        def __init__(self):
            self.condition = False
            super().__init__(
                states=[
                    "one",
                    "two",
                ],
                initial="one",
                transitions=[
                    {
                        "source": "one",
                        "dest": "two",
                        "trigger": "go",
                        "conditions": "condition",
                    },
                ],
            )

    machine = Root()
    assert machine.state == "one"
    assert not machine.go()
    assert machine.state == "one"
    machine.condition = True
    assert machine.go()
    assert machine.state == "two"


def test_str_conditions_nested():

    class Child(BaseMachine):
        def __init__(self, **kwargs):
            self.condition = False
            super().__init__(**kwargs)

    child = Child(
        states=[
            "two",
            "three",
        ],
        initial="two",
        transitions=[
            {
                "source": "two",
                "dest": "three",
                "trigger": "change",
                "conditions": "condition",
            },
        ],
    )

    root = RootMachine(
        states=[
            {
                "name": "one",
                "children": child,
            },
        ],
        initial="one",
    )

    assert root.state == "one_two"
    assert not root.change()
    assert root.state == "one_two"
    child.condition = True
    assert root.change()
    assert root.state == "one_three"


def test_get_state_path():
    child2 = BaseMachine(states=["three"], initial="three")
    child1 = BaseMachine(
        states=[
            {
                "name": "two",
                "children": child2,
            }
        ],
        initial="two",
    )
    machine = RootMachine(
        states=[
            {
                "name": "one",
                "children": child1,
            }
        ],
        initial="one",
    )

    assert machine.get_state_path() == ""
    assert child1.get_state_path() == "one"
    assert child2.get_state_path() == "one_two"


def test_get_machine_state():
    child = BaseMachine(
        states=["three", "four"],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "go",
            },
        ],
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child,
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
        ],
    )

    assert machine.state == "one"
    assert machine.get_machine_state() == "one"
    assert child.get_machine_state() is None

    assert machine.start()

    assert machine.state == "two_three"
    assert machine.get_machine_state() == "two"
    assert child.get_machine_state() == "three"

    assert machine.go()

    assert machine.state == "two_four"
    assert machine.get_machine_state() == "two"
    assert child.get_machine_state() == "four"


def test_remap():
    child = BaseMachine(
        states=[
            "C",
        ],
        initial="C",
    )
    child.add_state("D")
    child.add_transition(
        source="C",
        dest="D",
        trigger="test",
    )

    machine = RootMachine(
        states=[
            {
                "name": "A",
                "children": child,
                "remap": {"D": "B"},
            },
            "B",
        ],
        initial="A",
    )

    assert machine.state == "A_C"
    assert machine.test()
    assert machine.state == "B"


def test_remap_on_enter():
    class TimeRecorder:
        def __init__(self, duration=0.1):
            self.called = False
            self.call_time = None
            self.duration = duration

        def __call__(self):
            self.called = True
            self.call_time = time.time()
            time.sleep(self.duration)

        def assert_called(self):
            assert self

        def __bool__(self):
            return self.called

        def __lt__(self, other):
            return self.call_time < other.call_time

        def __le__(self, other):
            return self.call_time <= other.call_time

        def __eq__(self, other):
            return self.call_time == other.call_time

        def __ne__(self, other):
            return self.call_time != other.call_time

        def __gt__(self, other):
            return self.call_time > other.call_time

        def __ge__(self, other):
            return self.call_time >= other.call_time

    enter_callback = TimeRecorder()
    before_callback = TimeRecorder()
    after_callback = TimeRecorder()
    parent_enter_callback = TimeRecorder()

    child = BaseMachine(
        states=[
            "A",
            {
                "name": "B",
                "on_enter": enter_callback,
            },
        ],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "next",
                "before": before_callback,
                "after": after_callback,
            },
        ],
    )
    machine = RootMachine(
        states=[
            "A",
            {
                "name": "B",
                "children": child,
                "remap": {"B": "C"},
            },
            {
                "name": "C",
                "on_enter": parent_enter_callback,
            },
        ],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "next",
            },
        ],
    )

    assert machine.state == "A"
    machine.next()
    assert machine.state == "B_A"
    machine.next()
    assert machine.state == "C"

    enter_callback.assert_called()
    before_callback.assert_called()
    after_callback.assert_called()
    parent_enter_callback.assert_called()

    assert before_callback < enter_callback < parent_enter_callback < after_callback


def test_remap_with_callbacks():
    child = BaseMachine(
        states=[
            "A",
            "B",
        ],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "trigger",
                "conditions": "test",
                "unless": "not",
                "before": "function",
            }
        ],
    )
    machine = RootMachine(
        states=[
            {
                "name": "A",
                "children": child,
                "remap": (
                    {
                        "orig": "B",
                        "dest": "B",
                        "conditions": "another_test",
                        "before": ["another_function", "last_func"],
                        "after": "final",
                    },
                    {
                        "orig": "B",
                        "dest": "C",
                    },
                ),
            },
            "B",
            "C",
        ],
        initial="A",
    )

    transition = machine.events["trigger"].transitions["A_A"][0]

    assert {cond.func: cond.target for cond in transition.conditions} == {
        "test": True,
        "not": False,
        "another_test": True,
    }
    assert transition.before == ["function", "another_function", "last_func"]
    assert transition.after == ["final"]

    transition = machine.events["trigger"].transitions["A_A"][1]

    assert {cond.func: cond.target for cond in transition.conditions} == {
        "test": True,
        "not": False,
    }
    assert transition.before == ["function"]
    assert transition.after == []


def test_current_machine():
    child2 = BaseMachine(
        states=["A", "B"],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "next",
            },
        ],
    )
    child1 = BaseMachine(
        states=[
            "A",
            "B",
            {
                "name": "C",
                "children": child2,
            },
        ],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "next",
            },
            {
                "source": "B",
                "dest": "C",
                "trigger": "next",
            },
        ],
    )
    machine = RootMachine(
        states=[
            "A",
            {
                "name": "B",
                "children": child1,
            },
        ],
        initial="A",
        transitions=[
            {
                "source": "A",
                "dest": "B",
                "trigger": "next",
            },
        ],
    )

    assert machine.state == "A"
    assert not child1.current_machine()
    machine.next()
    assert machine.state == "B_A"
    assert child1.current_machine()
    machine.next()
    assert machine.state == "B_B"
    assert child1.current_machine()
    machine.next()
    assert machine.state == "B_C_A"
    assert not child1.current_machine()
    machine.next()
    assert machine.state == "B_C_B"
    assert not child1.current_machine()


def test_parent_reserved():
    with pytest.raises(AssertionError):
        RootMachine(states=[{"name": "parent", "children": BaseMachine()}])


def test_logger_hierarchy():
    child3 = BaseMachine(
        states=[
            "eight",
            "nine",
        ],
        initial="eight",
        transitions=[
            {
                "source": "eight",
                "dest": "nine",
                "trigger": "change",
            },
        ],
    )

    child2 = BaseMachine(
        states=[
            {
                "name": "five",
                "children": child3,
                "remap": {
                    "nine": "six",
                },
            },
            "six",
        ],
        initial="five",
    )

    child1 = BaseMachine(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
                "remap": {
                    "six": "seven",
                },
            },
            "seven",
        ],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "go",
            },
        ],
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
                "remap": {
                    "seven": "one",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
            {
                "source": "one",
                "dest": "two_four_five",
                "trigger": "jump",
            },
        ],
    )

    assert machine._logger.name == "pigeon_transitions.root"
    assert child1._logger.name == "pigeon_transitions.root.two"
    assert child2._logger.name == "pigeon_transitions.root.two.four"
    assert child3._logger.name == "pigeon_transitions.root.two.four.five"


def test_log_exception(mocker):

    class TestMachine(RootMachine):
        def error(self):
            raise Exception

    error_line = currentframe().f_lineno - 2

    machine = TestMachine(
        states=[
            "A",
            {
                "name": "B",
                "on_enter": "error",
            },
        ],
        initial="A",
        transitions=[
            {
                "trigger": "change",
                "source": "A",
                "dest": "B",
            },
        ],
        logger=mocker.MagicMock(),
    )

    machine._start()

    assert machine.state == "A"
    assert machine.change()

    machine._logger.warning.assert_called_once_with(
        f'An error was encountered while running callback "error":\n  File "{__file__}", line {error_line}, in error\n    raise Exception\n'
    )
