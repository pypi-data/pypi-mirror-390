from .base import BaseMachine
from .exceptions import MailboxException, NotCollectedError
from transitions.core import listify, EventData, Event
from pigeon import Pigeon
from pigeon.utils import call_with_correct_args
import logging
from time import sleep, time
from threading import Timer


class RootMachine(BaseMachine):
    _model = BaseMachine.self_literal

    def __init__(self, logger=None, **kwargs):
        """This constructor builds on the BaseMachine constructor adding the following:

        * The state machine model is the class instance.
        * Auto transitions are disabled.
        * State attributes (callbacks etc.), and transition conditions and callbacks are
            configured to be displayed on the graph.
        * Active and previous states are styled the same as the inactive states on the graph.
        * A logger is created if not provided.
        """
        self._client = None
        self._parent = None
        self._collected = {}
        self.style_attributes["node"]["active"] = self.style_attributes["node"][
            "inactive"
        ]
        self.style_attributes["node"]["previous"] = self.style_attributes["node"][
            "inactive"
        ]
        super().__init__(
            show_conditions=True,
            show_state_attributes=True,
            **kwargs,
        )
        self._logger = logger if logger is not None else logging.getLogger(__name__)
        self.rename_loggers()
        self.check_mailboxes()

    def send_to_parent(self, *args):
        raise MailboxException("Root machine has no parent.")

    def get_from_parent(self, *args):
        raise MailboxException("Root machine has no parent.")

    def check_mailboxes(self):
        if self.sends_to_parent != []:
            raise MailboxException(
                f"Root machine has no parent. '{self.__class__.__name__}' must have 'sends_to_parent' set to '[]'."
            )
        if self.gets_from_parent != []:
            raise MailboxException(
                f"Root machine has no parent. '{self.__class__.__name__}' must have 'gets_from_parent' set to '[]'."
            )
        super().check_mailboxes()

    def _init_graphviz_engine(self, graph_engine):
        """This method takes the existing graph class selected based on what
        graph engine and creates and returns a subclass."""

        class Graph(super()._init_graphviz_engine(graph_engine)):
            def _transition_label(self, trans):
                """This method is overridden to add displaying of the before and
                after transition callbacks on the graph."""
                label = super()._transition_label(trans)
                if "before" in trans and trans["before"]:
                    label += r"\lbefore: {}".format(", ".join(trans["before"]))
                if "after" in trans and trans["after"]:
                    label += r"\lafter: {}".format(", ".join(trans["after"]))
                return label

        return Graph

    def add_client(
        self,
        service=None,
        host="127.0.0.1",
        port=61616,
        username=None,
        password=None,
    ):
        """This method adds a Pigeon client to the class, and subscribes to all
        known messages."""
        self._client = Pigeon(
            service if service is not None else "pigeon-transitions",
            host=host,
            port=port,
        )
        self._client.connect(username=username, password=password)
        self._client.subscribe_all(self._message_callback)

    def save_graph(self, path):
        """This method saves a graph of the hierarchical state machine to the
        provided path."""
        extension = path.split(".")[-1].lower()
        self.get_graph().render(format=extension, cleanup=True, outfile=path)

    def _get_from_heirarchy(self, state_list):
        child = self
        for state in state_list:
            if state not in child._children:
                raise ValueError(f"Machine {child} has no child {state}.")
            child = child._children[state]
        return child

    def _get_machine(self, state):
        """This method returns the machine instance which a given state is part of."""
        return self._get_from_heirarchy(state.split(self.separator)[:-1])

    def _get_current_machine(self):
        """This method returns the machine instance which the current state is part of."""
        return self._get_machine(self.state)

    def _get_current_machines(self):
        """This generator first yields the full hierarchical state of the current
        machine then continues yielding states descending to the root machine."""
        state_list = self.state.split(self.separator)
        yield self._get_current_machine()
        for i in range(1, len(state_list)):
            yield self._get_machine(self.separator.join(state_list[:-i]))

    def _message_callback(self, msg, topic, *args, **kwargs):
        """This method is the main callback for Pigeon messages. It stores the
        most recent message on each topic, and it takes the message and calls
        the message_callback function in each machine, starting at the leaf,
        and traversing to the root."""
        self._collect(topic, msg)
        for machine in self._get_current_machines():
            try:
                call_with_correct_args(
                    machine.message_callback, msg, topic, *args, **kwargs
                )
            except Exception as e:
                self._logger.warning(
                    f"Callback for a message on topic '{topic}' with data '{msg}' resulted in an exception:",
                    exc_info=True,
                )

    def _collect(self, topic, msg):
        """This method stores the most recent message recieved on each topic."""
        self._collected[topic] = msg

    def get_collected(self, topic, timeout=0):
        """This function returns the most recent message recieved on a given topic.

        args:
            topic (str): The topic to get the latest message from.
            timeout (float): The number of seconds to wait until the topic is available.
                If None, immediately return None if a message has not been recieved on
                the topic. If 0, wait indefinitely."""
        self._client._ensure_topic_exists(topic)
        if timeout is None:
            return self._collected.get(topic, None)
        start = time()
        while topic not in self._collected and (
            timeout == 0 or time() - start <= timeout
        ):
            sleep(0.1)
        if topic not in self._collected:
            raise NotCollectedError(
                f"A message on topic {topic} has not been received after {timeout} seconds."
            )
        return self._collected[topic]

    def _get_initial_states(self):
        """This method returns the set of initial states of the hierarchical state machine."""
        states = [self.states[self.initial]]
        while len(states[-1].states):
            states.append(states[-1].states[states[-1].initial])
        return states

    def _collect_states(self, states=None):
        for state in self.states.values() if states is None else states.values():
            yield state
            yield from self._collect_states(state.states)

    def _start(self):
        """This method can be called at the beginning of execution of the state
        machine. It runs the on_enter callback of each of the machines that are
        part of the initial state."""
        self.callbacks(
            self._on_enter, EventData(None, Event("_start", self), self, self, [], {})
        )
        heirarchy = []
        for state in self._get_initial_states():
            event = EventData(state, Event("_start", self), self, self, [], {})
            heirarchy.append(state.name)
            try:
                machine = self._get_from_heirarchy(heirarchy)
                self.callbacks(machine._on_enter, event)
            except ValueError:
                pass
            self.callbacks(state.on_enter, event)
        self._start_timer()

    def _start_timer(self):
        state = self.get_state(self.state)
        if state.timeout > 0:
            event_data = EventData(self.state, "_start", self, self, (), {})
            timer = Timer(state.timeout, state._process_timeout, args=(event_data,))
            timer.daemon = True
            timer.start()
            state.runner[id(self)] = timer

    def _run_once(self):
        sleep(1)

    def _loop(self):
        while True:
            self._run_once()

    def _run(self):
        """This method runs the _start routine, then enters an infinte loop."""
        self._start()
        self._loop()
