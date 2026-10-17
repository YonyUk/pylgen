# Module `automaton`

## Submodule `automaton.automaton`

> ### `State`

State class for building automatons. This class is inmutable.

 - `__init__(id, value,is_accept=False)`
    - Args:
        
        - `id (str)`: identifier; two states with the same `id` are equal.

        - `value (Any)`: value contained in the state.

        - `is_accept (bool)`: whether it is an accepting state.

#### Properties

 - `id (str)`

 - `value (Any)`

 - `is_accept (bool)`

#### Methods

 - `__str__`: returns `str(value)`.

 - `__repr__`: returns `str(value)`.

 - `__eq__`: equality by `id`.

 - `__hash__`: returns the precomputed hash.

> ### `Automaton`

Base class for automaton definition.

 - `__init__()`:
    - Raises: `ValueError("Can not instance this class")`

#### Properties

 - `id (str)`: deterministic hash of start state, states, transitions and epsilon-transitions.

 - `alphabet (Set[str])`: copy of the alphabet.

 - `start_state (State)`: copy of the start state (deep copy if value is a set).

 - `current_state (State)`: copy of the current state.

 - `states (Set[State])`: copy of states.

 - `finals (Set[State])`: accepting states.

 - `is_complete (bool)`: `True` if every state has defined a transition, `False` otherwise.

 - `transition_function (Dict[Tuple[str,str], str])`: a plain representation of the automaton transition function.

 - `epsilon_transitions (Dict[str, Set[str]])`: a plain representation of the automaton epsilon transitions.

 - `is_empty (bool)`: `True` if the language is empty.

 - `is_finite (bool)`: `True` if the language is finite.

#### Static Methods

 - `Union(automatons)`: returns the `NFA` equivalent to the union between all the automatons provided.
    - Args:
        - `automatons (Set[Automaton])`

 - `Complement(automaton)`: returns the `DFA` of the complement of the given automaton.
    - Args:
        - `automaton (Automaton)`

 - `Intersection(automatons)`: returns the `DFA` equivalent to the intersection between all the automatons provided.
    - Args:
        - `automatons (Set[Automaton])`

 - `Concat(first, second)`: returns the `NFA` equivalent to the concatenation of `first` followed by `second`.
    - Args:
        - `first (Automaton)`
        - `second (Automaton)`

 - `KleeneStar(automaton)`: returns the `NFA` equivalent to $L^{*}$, where $L$ is the language of `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `PositiveClosure(automaton)`: returns the `NFA` equivalent to $L$+, where $L$ is the language of `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `Optional(automaton)`: returns the `NFA` equivalent to $L$?, where $L$ is the language of `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `Reverse(automaton)`: returns the `NFA` equivalent to the given automaton with all its transitions inverted.
    - Args:
        - `automaton (Automaton)`

#### Methods

 - `add_transition(from_state, to_state, symbol)`: adds a transition. (Automatically updates the `states` and `is_complete` properties of the current automaton).

    - Args:
        - `from_state (State)`: origin state.
        - `to_state (State)`: destination state.
        - `symbol (str)`: symbol that triggers the transitions.

    - Raises: `ValueError` if `symbol` is not in the alphabet.
  
  - `has_transition(state, symbol)`: returns `True` if the transition `(state, symbol)` exists.
    - Args:
        - `state (State)`: origin state.
        - `symbol (str)`

 - `next(state, symbol)`: returns the destination state for the given transition `(state,symbol)`.
    - Args:
        - `state (State)`: origin state.
        - `symbol (str)`

    - Raises: `KeyError` if there is no transition.

 - `reset()`: resets the automaton to its initial state before any internal change that has been done.

 - `closure(state)`: returns the set of states corresponding to the epsilon-closure of `state`.
    - Args:
        - `state (State)`

 - `make_complete()`: adds all missing transitions to a fault state.

 - `restore_to_before_complete()`: removes the fault state and added transitions.

 - `extend_alphabet(symbols)`: expands the current alphabet with the new set of symbols.
    - Args:
        - `symbols (Set[str])`

#### Operators

 - `__or__`(`|`): union, `aut1 | aut2` is equivalent to `Automaton.Union({aut1,aut2})`.
 - `__and__`(`&`): intersection, `aut1 & aut2` is equivalent to `Automaton.Intersection({aut1,aut2})`.
 - `__add__`(`+`): concatenation, `aut1 + aut2` is equivalent to `Automaton.Concat(aut1,aut2)`.

> ### `DFA`

Class for a ***Deterministic Finite Automata***. Inherits from `Automaton` (`DFA(Automaton)`).

 - `__init__(start_id, start_value, alphabet, start_accept=False)`
    - Args:
        - `start_id (str)`: id of the start state.
        - `start_value (Any)`: value of the start state.
        - `alphabet (Set[str])`: alphabet of the automaton.
        - `start_accept (bool)`: if `True`, the start state is an accepting state.

#### Methods

 - `walk(symbol)`: advances if not stuck; if no transition, marks `_is_stuck` internal flag as `True`.
    - Args:
        - `symbol (str)`

 - `accept(string)`: `True` if the automaton ends in an accepting state after reading the entire string. Calls `reset` at the end.
    - Args:
        - `string (List[str])`

 - `minimize(initial_partition = [])`: returns the equivalent minimized `DFA` (Hopcroft's algorithm).
    - Args:
        - `initial_partition (List[Set[State]])`: initial partition.

#### Operators

 - `__iadd__(transition)`: adds a transition via the `+=` operator.
    - Args:
        - `transition (Tuple[State,str,State])`: has the form `(from_state,symbol,to_state)`, where `from_state` is the origin state, `from_state` is the destination state, and `symbol` is the trigger of the transition.

> ### `NFA`

Class for our [Hybrid $\epsilon$-DFA](../../formal-foundations/formal-foundations-automata.md#the-hybrid-epsilon-dfa-a-deterministic-core-with-spontaneous-moves). Inherits from `Automaton` (`NFA(Automaton)`).

 - `__init__(start_id, start_value, alphabet, start_accept=False)`
    - Args:
        - `start_id (str)`: id of the start state.
        - `start_value (Any)`: value of the start state.
        - `alphabte (Set[str])`: alphabet of the automaton.
        - `start_accept (bool)`: if `True`, the start state is an accepting state.

#### Methods

 - `add_epsilon_transition(from_state, to_state)`: adds an epsilon-transition. (Automatically updates the `states` property of the current automaton).
    - Args:
        - `from_state (State)`: origin state.
        - `to_state (State)`: destination state.

 - `to_deterministic()`: returns the equivalent `DFA` (subset construction with epsilon-closure).

#### Operators

 - `__iadd__(transition)`: adds a transition via the `+=` operator.
    - Args:
        - `transition (Tuple[State,str,State])`: has the form `(from_state,symbol,to_state)`, where `from_state` is the origin state, `from_state` is the destination state, and `symbol` is the trigger of the transition.

> ### Module functions

 - `create_dfa(states, transition_function, start_id, alphabet)`: creates a `DFA` from the given states, alphabet and transitions.
    - Args:
        - `states (Set[State])`: states of the automaton.
        - `transition_function (Table)`: the transition function in a tabular form.
        - `start_id (str)`: id of the start state.
        - `alphabet (Set[str])`: alphabet of the automaton.
    
    - Raises: `ValueError(f'A initial state is needed, not found any state with given id {start_id}')` if none of `states` has the id `start_id`.

 - `create_nfa(states, transition_function, epsilon_transitions, start_id, alphabet)`: creates an `NFA` from the given states, alphabet, transitions and epsilon transitions.
    - Args:
        - `states (Set[State])`: states of the automaton.
        - `transition_function (Table)`: the transition function in a tabular form.
        - `epsilon_transitions (Dict[str,Set[str]])`: the epsilon transitions.
        - `start_id (str)`: id of the start state.
        - `alphabet (Set[str])`: alphabet of the automaton.

    - Raises: `ValueError(f'A initial state is needed, not found any state with given id {start_id}')` if none of `states` has the id `start_id`.

 - `get_word_automaton(word)`: returns a `DFA` that accepts only `word`.
    - Args:
        - `word (str)`

 - `get_words_automaton(words)`: returns an `NFA` that accepts only the given words (union of DFAs).
    - Args:
        - `words (List[str])`

 - `get_word_automaton_with_value(word, value, only_finals=False)`: analogous to `get_word_automaton`.
    - Args:
        - `word (str)`
        - `value (Any)`: value to assign to states.
        - `only_finals (bool)`: if `True`, `value` is assigned only to accepting states.

 - `get_words_automaton_with_value(words, value, only_finals=False)`: analogous to `get_words_automaton`.
    - Args:
        - `words (List[str])`
        - `value (Any)`: value to assign to states.
        - `only_finals (bool)`: if `True`, `value` is assigned only to accepting states.