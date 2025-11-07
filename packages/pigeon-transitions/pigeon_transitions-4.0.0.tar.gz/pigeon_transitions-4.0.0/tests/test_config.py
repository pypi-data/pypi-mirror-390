from pigeon_transitions.config import PigeonTransitionsConfig
from pigeon_transitions import RootMachine, FunctionMachine, BaseMachine


def test_config():
    config = PigeonTransitionsConfig.load(
        """
        root: pigeon_transitions.RootMachine
        machines:
            config:
                this: is
                something: 1
            Child:
                config:
                    more: data
                replace: pigeon_transitions.machines.FunctionMachine
        """
    )

    assert config.root is RootMachine
    assert config.machines.config == {"this": "is", "something": 1}
    assert config.machines.Child.config == {"more": "data"}
    assert config.machines.Child.replace is FunctionMachine


def test_replace():
    config = PigeonTransitionsConfig.load(
        """
        root: pigeon_transitions.RootMachine
        machines:
            two:
                replace: pigeon_transitions.machines.FunctionMachine
        """
    )

    class Child(BaseMachine):
        def __init__(self):
            super().__init__(
                states=[
                    "three",
                    "four",
                ]
            )

    class Root(RootMachine):
        def __init__(self, config=None):
            super().__init__(
                states=[
                    "one",
                    {
                        "name": "two",
                        "children": Child.init_child("two", config),
                    },
                ],
                initial="one",
            )

    root = Root(config=config.machines, **config.machines.config)

    assert root.__class__.__name__ == "Root"
    assert root._children["two"].__class__.__name__ == "FunctionMachine"
