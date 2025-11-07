from .config import MachineConfig
from .exceptions import MailboxException
from transitions.extensions import LockedHierarchicalGraphMachine as Machine
from transitions.extensions.states import add_state_features, Timeout
from transitions.core import listify
from copy import copy, deepcopy
import logging
from functools import partial
import traceback
import transitions
from pathlib import Path
from functools import partial


PIGEON_TRANSITIONS_MODULE = Path(__file__).parent
TRANSITIONS_MODULE = Path(transitions.__file__).parent


class State(Timeout, Machine.state_cls):
    def __init__(self, *args, **kwargs):
        self._span = None
        super().__init__(*args, **kwargs)

    def enter(self, event_data):
        self.machine_enter(event_data)
        super().enter(event_data)

    def exit(self, event_data):
        super().exit(event_data)
        self.machine_exit(event_data)

    def get_machine(self, event_data):
        return event_data.machine._get_from_heirarchy(
            self.name.split(event_data.model.separator)
        )

    def machine_enter(self, event_data):
        try:
            event_data.machine.callbacks(
                self.get_machine(event_data)._on_enter,
                event_data,
            )
        except ValueError:
            pass

    def machine_exit(self, event_data):
        try:
            event_data.machine.callbacks(
                self.get_machine(event_data)._on_exit,
                event_data,
            )
        except ValueError:
            pass


class Transition(Machine.transition_cls):
    def execute(self, event_data):
        if success := super().execute(event_data):
            event_data.machine._logger.info(
                f"Transitioned to state: {event_data.model.state}"
            )
        return success


class BaseMachine(Machine):
    state_cls = State
    transition_cls = Transition
    _model = []
    sends_to = {}
    sends_to_parent = []
    gets_from = {}
    gets_from_parent = []

    def __init__(
        self,
        states=None,
        transitions=None,
        on_enter=None,
        on_exit=None,
        before_state_change=None,
        after_state_change=None,
        prepare_event=None,
        finalize_event=None,
        on_exception=None,
        on_final=None,
        **kwargs,
    ):
        """The standard transitions Machine constructor with the folowing changes:

        * The model is disabled.
        * An on_enter callback is created on the machine and transformed using _get_callables and _get_callable.
        * The before_state_change, after_state_change, prepare_event, finalize_event, on_exception, and on_final
            callbacks are transformed using _get_callables and _get_callable.
        """
        self._logger = logging.getLogger(__name__)
        self._parent = None
        self.state_name = None
        self._children = {}
        self._on_enter = self._get_callables(on_enter)
        self._on_exit = self._get_callables(on_exit)
        self._mailbox = {}
        super().__init__(
            states=states,
            transitions=transitions,
            model=self._model,
            before_state_change=self._get_callables(before_state_change),
            after_state_change=self._get_callables(after_state_change),
            prepare_event=self._get_callables(prepare_event),
            finalize_event=self._get_callables(finalize_event),
            on_exception=self._get_callables(on_exception),
            on_final=self._get_callables(on_final),
            auto_transitions=False,
            **kwargs,
        )

    def send_to(self, child, field, data):
        if child not in self._children:
            raise MailboxException(
                f"Cannot send to '{child}' as it is not a child of '{self.get_state_path()}'."
            )
        if field not in self.sends_to.get(child, []):
            raise MailboxException(
                f"The field '{field}' is not specified in '{self.__class__.__name__}.sends_to'."
            )
        self._send_to(self._children[child], "parent", field, data)

    def send_to_parent(self, field, data):
        if field not in self.sends_to_parent:
            raise MailboxException(
                f"The field '{field}' is not specified in '{self.__class__.__name__}.sends_to_parent'."
            )
        self._send_to(self._parent, self.state_name, field, data)

    def _send_to(self, state, source, field, data):
        if source not in state._mailbox:
            state._mailbox[source] = {field: data}
        else:
            state._mailbox[source][field] = data

    def get_from(self, child, field):
        if child not in self._children:
            raise MailboxException(
                f"Cannot get from '{child}' as it is not a child of '{self.get_state_path()}'."
            )
        if field not in self.gets_from.get(child, []):
            raise MailboxException(
                f"The field '{field}' is not specified in '{self.__class__.__name__}.gets_from'."
            )
        if field not in self._mailbox.get(child, {}):
            raise MailboxException(
                f"The field '{field}' has not been sent to '{self.get_state_path()}' by '{child}' yet."
            )
        return self._mailbox[child][field]

    def get_from_parent(self, field):
        if field not in self.gets_from_parent:
            raise MailboxException(
                f"The field '{field}' is not specified in '{self.__class__.__name__}.gets_from_parent'."
            )
        if field not in self._mailbox.get("parent", {}):
            raise MailboxException(
                f"The field '{field}' has not been sent to '{self.get_state_path()}' by the parent."
            )
        return self._mailbox["parent"][field]

    def rename_loggers(self):
        if self._parent is not None:
            self._logger = self._parent._logger.getChild(self.state_name)
        for child in self._children.values():
            child.rename_loggers()

    def check_mailboxes(self):
        for name in self.sends_to:
            if name not in self._children:
                raise MailboxException(
                    f"Cannot send {self.sends_to[name]} to '{name}' as the child does not exist."
                )
        for name in self.gets_from:
            if name not in self._children:
                raise MailboxException(
                    f"Cannot get {self.gets_from[name]} from '{name}' as the child does not exist."
                )
        for name, child in self._children.items():
            if set(self.sends_to.get(name, [])) != set(child.gets_from_parent):
                raise MailboxException(
                    f"Inconsistent specifications, '{self.get_state_path()}' expects to send {self.sends_to.get(name, [])} to '{name}' which expects to recieve {child.gets_from_parent}."
                )
            if set(self.gets_from.get(name, [])) != set(child.sends_to_parent):
                raise MailboxException(
                    f"Inconsistent specifications, '{self.get_state_path()}' expects to recieve {self.gets_from.get(name, [])} from '{name}' which expects to send {child.sends_to_parent}."
                )
            child.check_mailboxes()

    @classmethod
    def init_child(cls, name, config, *args, **kwargs):
        """This is a helper routine for propogating configuration to child machines."""
        if isinstance(config, MachineConfig) and hasattr(config, name):
            machine_config = getattr(config, name)
            kwargs["config"] = machine_config
            kwargs.update(machine_config.config)
            if machine_config.replace is not None:
                return machine_config.replace(*args, **kwargs)
        return cls(*args, **kwargs)

    def _create_state(
        self, *args, on_enter=None, on_exit=None, on_timeout=None, **kwargs
    ):
        """Transform callbacks using _get_callables"""
        return super()._create_state(
            *args,
            on_enter=self._get_callables(on_enter),
            on_exit=self._get_callables(on_exit),
            on_timeout=self._get_callables(on_timeout),
            **kwargs,
        )

    def add_transition(
        self,
        *args,
        conditions=None,
        unless=None,
        before=None,
        after=None,
        prepare=None,
        **kwargs,
    ):
        """Transform callbacks using _get_callables"""
        return super().add_transition(
            *args,
            conditions=self._get_callables(conditions),
            unless=self._get_callables(unless),
            before=self._get_callables(before),
            after=self._get_callables(after),
            prepare=self._get_callables(prepare),
            **kwargs,
        )

    def _get_callable(self, func):
        """Get a class member function of the same name as the input if available.
        If the class member is not a function, create a lambda function which
        returns the current value of the class member variable. If the input is
        a variable, return a lambda function which returns the current value of
        the variable."""
        if isinstance(func, str):
            if hasattr(self, func):
                tmp = getattr(self, func)
                if callable(tmp):
                    return tmp
                else:
                    geter = lambda: getattr(self, func)
                    # Setting the __name__ attribute shows the function name on the graph
                    geter.__name__ = func
                    return geter
            else:
                return func
        if not callable(func):
            return lambda: func
        return func

    def _get_callables(self, funcs):
        """Returns a transformed list of callbacks with string entries substituted
        for class member functions when available."""
        if funcs is None:
            return []
        return [self._get_callable(func) for func in listify(funcs)]

    def _add_machine_states(self, state, remap):
        """This method is overridden to build the parent, child relationships
        between each machine in the hierarchy."""
        state._parent = self
        assert (
            self.get_global_name() != "parent"
        ), "The state name 'parent' is reserved."
        state.state_name = self.get_global_name()
        self._children[self.get_global_name()] = state
        super()._add_machine_states(state, remap)

    def _remap_state(self, state, remaps):
        """This function overrides the normal _remap_state method to add the following:
        * Remove the remaped state so it does not appear in the diagram.
        * Add any on_enter callbacks of the remapped state to the after callbacks of
        the transition.
        * Allow passing a list of dicts for remaps where the dict specifies the original state,
        destination, and any conditions or callbacks for the transition."""
        if isinstance(remaps, dict):
            return self._remap_state(
                state, [{"orig": orig, "dest": new} for orig, new in remaps.items()]
            )
        dummy_remaps = {}
        dest_ind = 0
        for remap in remaps:
            if remap["orig"] not in dummy_remaps:
                dummy_remaps[remap["orig"]] = str(dest_ind)
                dest_ind += 1
        dummy_transitions = super()._remap_state(state, dummy_remaps)
        remapped_transitions = []
        for remap in remaps:
            dest_ind = dummy_remaps[remap["orig"]]
            transition = None
            for dummy in dummy_transitions:
                if dummy["dest"] == dest_ind:
                    transition = {key: copy(val) for key, val in dummy.items()}
            assert transition is not None
            transition["dest"] = remap["dest"]
            for key, val in remap.items():
                if key not in ("orig", "dest"):
                    transition[key] += listify(val)
            transition["before"] += self.states[remap["orig"]].on_enter
            remapped_transitions.append(transition)
        for remap in remaps:
            old_state = remap["orig"]
            if old_state in self.states:
                del self.states[old_state]
        return remapped_transitions

    def message_callback(self):
        """This message callback can be overridden with the desired functionality
        for the machine. All machines in the hierarchy of active states will have
        this method called, starting at the leaf."""
        pass

    @property
    def root(self):
        """Traverse the tree of hierarchical machines to the root and return it."""
        root = self
        while root._parent is not None:
            root = root._parent
        return root

    @property
    def client(self):
        """Returns the Pigeon client, or None, if the machine is not part of the
        current state."""
        if self._current_machine():
            return self.root._client
        return None

    def get_state_path(self, join=True):
        """Returns the hierarchical state that leads to this machine.

        If join is False, returns a list of hierarchical states which lead to
            this machine."""
        parent = self
        states = []
        while parent._parent is not None:
            states.insert(0, parent.state_name)
            parent = parent._parent
        if join:
            return self.separator.join(states)
        return states

    def get_machine_state(self):
        """Returns the current state of this machine, or None, if the current
        state is not a state in this machine, or a substate."""
        state_path = self.get_state_path(join=False)
        state = self.state.split(self.separator)
        if any(
            [
                state_comp != state_path_comp
                for state_comp, state_path_comp in zip(state, state_path)
            ]
        ):
            return None
        return state[len(state_path)]

    def _current_machine(self):
        """Returns True if the current state is a state of this machine, or a substate."""
        return self.get_machine_state() is not None

    def current_machine(self):
        """Returns True if the current state is a state of this machine strictly."""
        if not self._current_machine():
            return False
        state = self.state.split(self.separator)
        state_path = self.get_state_path(join=False)
        return len(state_path) + 1 == len(state)

    def __getattr__(self, name):
        """If a class attribute is not available in this class, try to get it
        from the root class."""
        if self._parent is None:
            return super().__getattr__(name)
        return getattr(self.root, name)

    def callback(self, func, event_data):
        if isinstance(func, str):
            name = func
        else:
            name = func
            if isinstance(func, partial) and func.func == self._locked_method:
                name = func.args[0]
            if hasattr(name, "__name__"):
                name = name.__name__
            else:
                name = repr(name)
        try:
            super().callback(func, event_data)
        except Exception as e:
            tb = []
            for frame in traceback.extract_tb(e.__traceback__)[::-1]:
                parents = Path(frame.filename).parents
                if (
                    PIGEON_TRANSITIONS_MODULE in parents
                    or TRANSITIONS_MODULE in parents
                ):
                    break
                tb.insert(0, frame)
            self._logger.warning(
                f'An error was encountered while running callback "{name}":\n'
                + "\n".join(traceback.format_list(tb))
            )
