# Module `automaton`

## Submodule `automaton.automaton`

> ### `State`

State class for building automatons. This class is inmutable.

 - `__init__(id, value, is_accept=False)`
    - Args:
        
        - `id (str)`: identifier; two states with the same `id` are equal.

        - `value (Any)`: value contained in the state.

        - `is_accept (bint)`: whether it is an accepting state.

#### Properties

 - `_id (cdef str)`

 - `_value (cdef object)`

 - `_is_accept (cdef bint)`

 - `_hash (cdef int)`

> ### `Automaton`

Base class for automaton definition.

 - `__init__()`:
    - Raises: `ValueError("Can not instance this class")`

#### Properties

 - `_states_by_id (cdef dict[str,State])`: mapping of states by its ids.

 - `_alphabet (cdef set[str])`

 - `_start_state (cdef State)`: start state of the automaton.
 
 - `_current_state (cdef State)`: current state of the automaton.

 - `_trans_func (cdef Table)`: transitions of the automaton in a tabular form.

 - `_epsilons (cdef dict[str,set[str]])`: epsilons transitions of the automaton.

 - `_closures (cdef dict[str,set[State]])`: cache for the closures computations.

 - `_transitions_added_while_completing (cdef list[tuple[str,str]])`: record of the transitions added in a `make_complete()` call.

 - `_is_complete (cdef bint)`: `True` if the every state has defined a transition.
 
 - `_is_stuck (cdef bint)`: `True` if the automaton tried to advance from an state with a symbol that hasn't a transition defined.

 - `_fault_id (cdef str)`: id of the current fault state if exists.

 - `_preimages (cdef dict[tuple[str,str],set[State]])`: used during minimization process.

#### Methods

 - `cpdef void add_transition(from_state, to_state, symbol)`: adds a transition. (Automatically updates the `states` and `is_complete` properties of the current automaton).

    - Args:
        - `from_state (State)`: origin state.
        - `to_state (State)`: destination state.
        - `symbol (str)`: symbol that triggers the transitions.

    - Raises: `ValueError` if `symbol` is not in the alphabet.
  
  - `cpdef bint has_transition(state, symbol)`: returns `True` if the transition `(state, symbol)` exists.
    - Args:
        - `state (State)`: origin state.
        - `symbol (str)`

 - `cpdef State next(state, symbol)`: returns the destination state for the given transition `(state,symbol)`.
    - Args:
        - `state (State)`: origin state.
        - `symbol (str)`

    - Raises: `KeyError` if there is no transition.

 - `cpdef void reset()`: resets the automaton to its initial state before any internal change that has been done.

 - `cpdef set[State] closure(state)`: returns the set of states corresponding to the epsilon-closure of `state`.
    - Args:
        - `state (State)`

 - `cpdef void make_complete()`: adds all missing transitions to a fault state.

 - `cpdef void restore_to_before_complete()`: removes the fault state and added transitions.

 - `cpdef void extend_alphabet(symbols)`: expands the current alphabet with the new set of symbols.
    - Args:
        - `symbols (Set[str])`

> ### `DFA`

Class for a ***Deterministic Finite Automata***. Inherits from `Automaton` (`DFA(Automaton)`).

 - `__init__(start_id, start_value, alphabet, start_accept=False)`
    - Args:
        - `start_id (str)`: id of the start state.
        - `start_value (object)`: value of the start state.
        - `alphabet (set[str])`: alphabet of the automaton.
        - `start_accept (bint)`: if `True`, the start state is an accepting state.

#### Methods

 - `cdef set[State] _state_preimage_for_symbol(state, symbol)`: computes the preimage of the given state for the given symbol.
    - Args:
        - `state (State)`
        - `symbol (str)`

 - `cdef set[State] _block_preimage_for_symbol(states, symbol)`: computes the preimage of a set of states for the given symbol.
    - Args:
        - `states (set[State])`
        - `symbol (str)`

 - `cdef Table _build_new_transition_function(old_ids_to_new_ids_map)`: creates the transition function in tabular form from the current transition function and a mapping from old ids of states to new ids of states.
    - Args:
        - `old_ids_to_new_ids_map (dict[str,str])`: mapping from old ids of states to new ids of states.

 - `cdef DFA _build_new_dfa(partition)`: build a new `DFA` based in the given partition of states.
    - Args:
        - `partition (list[set[State]])`

 - `cpdef void walk(symbol)`: advances if not stuck; if no transition, marks `_is_stuck` internal flag as `True`.
    - Args:
        - `symbol (str)`

 - `cpdef bint accept(string)`: `True` if the automaton ends in an accepting state after reading the entire string. Calls `reset` at the end.
    - Args:
        - `string (list[str])`

 - `cpdef DFA minimize(initial_partition = [])`: returns the equivalent minimized `DFA` (Hopcroft's algorithm).
    - Args:
        - `initial_partition (list[set[State]])`: initial partition.

> ### `NFA`

Class for our [Hybrid $\epsilon$-DFA](../../formal-foundations/formal-foundations-automata.md#the-hybrid-epsilon-dfa-a-deterministic-core-with-spontaneous-moves). Inherits from `Automaton` (`NFA(Automaton)`).

 - `__init__(start_id, start_value, alphabet, start_accept=False)`
    - Args:
        - `start_id (str)`: id of the start state.
        - `start_value (Any)`: value of the start state.
        - `alphabte (Set[str])`: alphabet of the automaton.
        - `start_accept (bool)`: if `True`, the start state is an accepting state.

#### Methods

 - `cdef State _build_state(states)`: builds a new state with value `states`.
    - Args:
        - `states (set[State])`

 - `cdef State _build_new_state(state,target_table,current_states)`: used during determinzition of the automaton.
    - Args:
        - `state (State)`
        - `target_table (Table)`
        - `current_states (set[State])`

 - `cpdef void add_epsilon_transition(from_state, to_state)`: adds an epsilon-transition.
    - Args:
        - `from_state (State)`: origin state.
        - `to_state (State)`: destination state.

 - `cpdef DFA to_deterministic()`: returns the equivalent `DFA` (subset construction with epsilon-closure).

> ### Module functions

 - `cdef DFA _copy_dfa(dfa)`: copy the dfa.
    - Args:
        - `dfa (DFA)`

 - `cdef NFA _copy_nfa(nfa)`: copy the nfa.
    - Args:
        - `nfa (NFA)`

 - `cdef NFA _automaton_union(automatons)`: returns the `NFA` equivalent to the union between all the automatons provided.
    - Args:
        - `automatons (set[Automaton])`

 - `cdef DFA _dfa_complement(automaton)`: returns the `DFA` of the complement of the given automaton.
    - Args:
        - `automaton (DFA)`

 - `cdef DFA _nfa_complement(automaton)`: returns the `DFA` of the complement of the given automaton.
    - Args:
        - `automaton (NFA)`

 - `cdef DFA _automaton_complement(automaton)`: returns the `DFA` of the complement of the given automaton.
    - Args:
        - `automaton (Automaton)`

 - `cdef DFA _automaton_intersection(automatons)`: returns the `DFA` equivalent to the intersection between all the automatons provided.
    - Args:
        - `automatons (set[Automaton])`

 - `cdef NFA _automaton_concatenation(first, second)`: returns the `NFA` equivalent to the concatenation of `first` followed by `second`.
    - Args:
        - `first (Automaton)`
        - `second (Automaton)`

 - `cdef NFA _automaton_closure(automaton, type_)`
    - Args:
        - `automaton (Automaton)`
        - `type_ (int)`:
            - `0`: returns the `NFA` equivalent to $L^{*}$, where $L$ is the language of `automaton`.
            - `1`: returns the `NFA` equivalent to $L$+, where $L$ is the language of `automaton`.
            - `2`: returns the `NFA` equivalent to $L$?, where $L$ is the language of `automaton`.

 - `cdef NFA _automaton_reverse(automaton)`:returns the `NFA` equivalent to the given automaton with all its transitions inverted.
    - Args:
        - `automaton (Automaton)`

 - `cpdef DFA create_dfa(states, transition_function, start_id, alphabet)`: creates a `DFA` from the given states, alphabet and transitions.
    - Args:
        - `states (Set[State])`: states of the automaton.
        - `transition_function (Table)`: the transition function in a tabular form.
        - `start_id (str)`: id of the start state.
        - `alphabet (Set[str])`: alphabet of the automaton.
    
    - Raises: `ValueError(f'A initial state is needed, not found any state with given id {start_id}')` if none of `states` has the id `start_id`.

 - `cpdef NFA create_nfa(states, transition_function, epsilon_transitions, start_id, alphabet)`: creates an `NFA` from the given states, alphabet, transitions and epsilon transitions.
    - Args:
        - `states (Set[State])`: states of the automaton.
        - `transition_function (Table)`: the transition function in a tabular form.
        - `epsilon_transitions (Dict[str,Set[str]])`: the epsilon transitions.
        - `start_id (str)`: id of the start state.
        - `alphabet (Set[str])`: alphabet of the automaton.

    - Raises: `ValueError(f'A initial state is needed, not found any state with given id {start_id}')` if none of `states` has the id `start_id`.

 - `cpdef DFA get_word_automaton(word)`: returns a `DFA` that accepts only `word`.
    - Args:
        - `word (str)`

 - `cpdef NFA get_words_automaton(words)`: returns an `NFA` that accepts only the given words (union of DFAs).
    - Args:
        - `words (List[str])`

 - `cpdef DFA get_word_automaton_with_value(word, value, only_finals=False)`: analogous to `get_word_automaton`.
    - Args:
        - `word (str)`
        - `value (Any)`: value to assign to states.
        - `only_finals (bool)`: if `True`, `value` is assigned only to accepting states.

 - `cpdef NFA get_words_automaton_with_value(words, value, only_finals=False)`: analogous to `get_words_automaton`.
    - Args:
        - `words (List[str])`
        - `value (Any)`: value to assign to states.
        - `only_finals (bool)`: if `True`, `value` is assigned only to accepting states.