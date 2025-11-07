import pytest
from pigeon_transitions import BaseMachine, RootMachine
from pigeon_transitions.exceptions import MailboxException


def test_check_mailboxes():
    class Child3(BaseMachine):
        sends_to_parent = ["something", "something_else"]
        gets_from_parent = ["another"]

    class Child2(BaseMachine):
        sends_to = {"Child3": ["another"]}
        gets_from = {"Child3": ["something_else", "something"]}
        sends_to_parent = ["baz"]

        def __init__(self):
            super().__init__(states=[{"name": "Child3", "children": Child3()}])

    class Child1(BaseMachine):
        sends_to_parent = ["foo"]
        gets_from_parent = ["bar"]

    class Root(RootMachine):
        sends_to = {"Child1": ["bar"]}
        gets_from = {"Child1": ["foo"], "Child2": ["baz"]}

        def __init__(self):
            super().__init__(
                states=[
                    {"name": "Child2", "children": Child2()},
                    {"name": "Child1", "children": Child1()},
                ]
            )

    root = Root()


@pytest.mark.parametrize(
    "machine, attr, value",
    (
        ("child3", "sends_to_parent", []),
        ("child3", "gets_from_parent", []),
        ("child3", "sends_to", {"Another": ["value"]}),
        ("child3", "gets_from", {"Another": ["value"]}),
        ("child2", "sends_to", {}),
        ("child2", "gets_from", {}),
        ("child2", "sends_to_parent", []),
        ("child1", "sends_to_parent", []),
        ("child1", "gets_from_parent", []),
        ("root", "sends_to", {}),
        ("root", "gets_from", {}),
        ("root", "sends_to_parent", ["test"]),
        ("root", "gets_from_parent", ["test"]),
    ),
)
def test_check_mailboxes_bad(machine, attr, value):
    class Child3(BaseMachine):
        sends_to_parent = ["something", "something_else"]
        gets_from_parent = ["another"]

    class Child2(BaseMachine):
        sends_to = {"Child3": ["another"]}
        gets_from = {"Child3": ["something_else", "something"]}
        sends_to_parent = ["baz"]

    class Child1(BaseMachine):
        sends_to_parent = ["foo"]
        gets_from_parent = ["bar"]

    class Root(RootMachine):
        sends_to = {"Child1": ["bar"]}
        gets_from = {"Child1": ["foo"], "Child2": ["baz"]}

    child3 = Child3()
    child2 = Child2(states=[{"name": "Child3", "children": child3}])
    child1 = Child1()

    root = Root(
        states=[
            {"name": "Child2", "children": child2},
            {"name": "Child1", "children": child1},
        ]
    )

    setattr(locals()[machine], attr, value)

    with pytest.raises(MailboxException):
        root.check_mailboxes()


def test_send_to_parent_root():
    machine = RootMachine()

    with pytest.raises(MailboxException):
        machine.send_to_parent("something", 1)


def test_get_from_parent_root():
    machine = RootMachine()

    with pytest.raises(MailboxException):
        machine.send_to_parent("another")


@pytest.fixture
def test_machine():
    class Child1(BaseMachine):
        sends_to_parent = ["foo", "bar"]
        gets_from_parent = ["baz"]

    class Child2(BaseMachine):
        gets_from_parent = ["test"]

    class Root(RootMachine):
        sends_to = {"A": ["baz"], "B": ["test"]}
        gets_from = {"A": ["foo", "bar"]}

    child1 = Child1()
    child2 = Child2()
    child3 = BaseMachine()

    root = Root(
        states=[
            {"name": "A", "children": child1},
            {"name": "B", "children": child2},
            {"name": "C", "children": child3},
        ]
    )

    root.A = child1
    root.B = child2
    root.C = child3

    return root


def test_from_parent(test_machine):
    with pytest.raises(MailboxException):
        test_machine.B.get_from_parent("test")

    with pytest.raises(MailboxException):
        test_machine.send_to("B", "foo", 125)

    test_machine.send_to("B", "test", 125)

    assert test_machine.B.get_from_parent("test") == 125

    with pytest.raises(MailboxException):
        test_machine.C.get_from_parent("test")

    with pytest.raises(MailboxException):
        test_machine.A.get_from_parent("baz")

    test_machine.send_to("A", "baz", -5)

    assert test_machine.A.get_from_parent("baz") == -5


def test_to_parent(test_machine):
    with pytest.raises(MailboxException):
        test_machine.get_from("A", "bar")

    with pytest.raises(MailboxException):
        test_machine.A.send_to_parent("baz", 52)

    test_machine.A.send_to_parent("bar", 35)

    assert test_machine.get_from("A", "bar") == 35

    with pytest.raises(MailboxException):
        test_machine.get_from("C", "bar")

    with pytest.raises(MailboxException):
        test_machine.get_from("A", "foo")

    test_machine.A.send_to_parent("foo", -27)

    assert test_machine.get_from("A", "foo") == -27
