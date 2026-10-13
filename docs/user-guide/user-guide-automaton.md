# The `automaton` Module

The `automaton` module implements finite automata: `DFA`, `NFA`, and automata with ε‑moves. It supports manual construction and automatic generation from words.

## `State`

State is immutable. Its `id`, `value`, and `is_accept` cannot be modified after creation.

> ### Attributes

| **Property** | **Type** | **Default** | **Description** |
| :---: | :---: | :---: | :---: |
| **`id`** | `str` | Required | Unique identifier |
| **`value`** | `Any` | Required | Semantic value associated with the state |
| **`is_accept`** | `bool` | `False` | Whether the state is accepting |

!!! important "`State`'s Equality"
    The equality of two states is based solely on their ID; 2 states are considered equals if and only if its ids are equals.

> ### Typical Usage

=== "Python"

    ```python
    from pylgen.automaton import State

    s1 = State('s1', 's1')       # non-accepting
    s2 = State('s2', 10, True)   # accepting, value 10

    print(s1.id, s1.value, s1.is_accept)
    print(s2.id, s2.value, s2.is_accept)
    ```

=== "Cython"

    ```cython
    from pylgen.automaton cimport State

    cdef State s1 = State('s1', 's1')
    cdef State s2 = State('s2', 10, True)

    print(s1._id, s1._value, s1._is_accept)
    print(s2._id, s2._value, s2._is_accept)
    ```

## `Automaton`

`Automaton` is the abstract base class and cannot be instantiated. It provides state management, alphabet, transitions, ε‑transitions, and derived properties.

> ### Attributes

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | Unique identifier computed from the automaton structure |
| **`alphabet`** | `Set[str]` | Copy of the alphabet |
| **`start_state`** | `State` | Copy of the initial state |
| **`current_state`** | `State` | Copy of the current state |
| **`states`** | `Set[State]` | All states |
| **`finals`** | `Set[State]` | Accepting states |
| **`is_complete`** | `bool` | `True` if all transitions are defined |
| **`transition_function`** | `Dict[Tuple[str, str], str]` | Transition table |
| **`epsilon_transitions`** | `Dict[str, Set[str]]` | ε‑transitions |
| **`is_empty`** | `bool` | Whether the accepted language is empty |
| **`is_finite`** | `bool` | Whether the language is finite |

> ### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`add_transition(from_state, to_state, symbol)`** | Adds a deterministic transition |
| **`has_transition(state, symbol) -> bool`** | Checks if a transition exists |
| **`next(state, symbol) -> State`** | Returns the target state |
| **`reset()`** | Resets the current state to the initial state |
| **`closure(state) -> Set[State]`** | Computes the ε‑closure |
| **`make_complete()`** | Adds a sink state and missing transitions |
| **`restore_to_before_complete()`** | Reverts completion |
| **`extend_alphabet(symbols)`** | Extends the alphabet |

> ### Operators

| **Operator** | **Method** | **Return** | **Description** |
| :---: | :---: | :---: | :---: |
| **`|`** | `__or__` | `NFA` | Union |
| **`&`** | `__and__` | `DFA` | Intersection |
| **`+`** | `__add__` | `NFA` | Concatenation |

> ### Static Methods

| **Static** | **Method** | **Return** | **Description** |
| :---: | :---: | :---: | :---: |
| **`Union(automatons)`** | `NFA` | Union with a new start and ε‑transitions |
| **`Complement(automaton)`** | `DFA` | Complement. Determinizes and minimizes if needed |
| **`Intersection(automatons)`** | `DFA` | Cartesian product |
| **`Concat(first, second)`** | `NFA` | Concatenation with ε‑transitions |
| **`KleeneStar(automaton)`** | `NFA` | Kleene star |
| **`PositiveClosure(automaton)`** | `NFA` | Positive closure |
| **`Optional(automaton)`** | `NFA` | Optional |
| **`Reverse(automaton)`** | `NFA` | Reverses the language |

## `DFA`

The `DFA` class inherits from `Automaton` and adds deterministic behavior.

> ### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`walk(symbol)`** | Advances the current state. Enters stuck state on missing transition |
| **`accept(string)`** | Returns `True` if the string is accepted. Resets afterward. |
| **`minimize(initial_partition=[])`** | Applies [**Hopcroft's algorithm**](https://en.wikipedia.org/wiki/DFA_minimization). Completes temporarily if needed |
| **`__iadd__(transition:Tuple[State,str,State])`** | Adds a transition from the tuple `(from_state,symbol,to_state)` with `+=` operator |

#### Typical Usage

=== "Python"

    ```python
    from pylgen.automaton import DFA, State

    dfa = DFA("q0", "even", {"a", "b"}, True)
    q0 = dfa.start_state
    q1 = State("q1", "odd")

    dfa += q0, 'a', q1
    dfa += q1, 'a', q0
    dfa += q0, 'b', q0
    dfa += q1, 'b', q1

    assert dfa.accept(['a', 'b', 'a'])
    ```

=== "Cython"

    ```cython
    from pylgen.automaton cimport DFA, State

    cdef DFA dfa = DFA("q0", "even", {"a", "b"}, True)
    cdef State q0 = dfa._start_state
    cdef State q1 = State("q1", "odd")

    dfa.add_transition(q0, q1, 'a')
    dfa.add_transition(q1, q0, 'a')
    dfa.add_transition(q0, q0, 'b')
    dfa.add_transition(q1, q1, 'b')

    assert dfa.accept(['a', 'b', 'a'])
    ```

## `NFA`

The `NFA` class inherits from `DFA` and adds supporting for ε‑transitions and nondeterminism.

> ### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`add_epsilon_transition(from_state, to_state)`** | Adds an ε‑transition |
| **`to_deterministic()`** | Converts to an equivalent `DFA` via subset construction |
| **`__iadd__(transition:Tuple[State,str,State])`** | Adds a normal transition from the tuple `(from_state,symbol,to_state)` with the `+=` operator |

> ### Typical Usage

=== "Python"

    ```python
    union = dfa1 | dfa2   # NFA with new start and ε‑transitions
    ```

=== "Cython"

    ```cython
    from pylgen.automaton cimport NFA, _automaton_union

    cdef NFA union = _automaton_union({dfa1, dfa2})
    ```

## Factory Functions

| **Function** | **Return** | **Description** |
| :---: | :---: | :---: |
| **`create_dfa(states, transition_function, start_id, alphabet)`** | `DFA` | Builds a `DFA` from serialized data |
| <span style="white-space: nowrap">**`create_nfa(states, transition_function, epsilon_transitions, start_id, alphabet)`**</span> | `NFA` | Builds an `NFA` from serialized data |
| `get_word_automaton(word)` | `DFA` | Builds the `DFA` that recognizes exactly that one word |
| `get_words_automaton(words)` | `NFA` | Builds the `NFA` that recognizes the union of several words |
| `get_word_automaton_with_value(word, value, only_finals=False)` | `DFA` | Assigns a value to states |
| `get_words_automaton_with_value(words, value, only_finals=False)` | `NFA` | Same, for several words |

## Complete Example: Integer Recognizer

=== "Python"

    ```python
    from pylgen.automaton import DFA, State

    digits = set("0123456789")
    alphabet = digits | {"+", "-"}

    q0 = State("q0", None)
    q1 = State("q1", None)
    q2 = State("q2", "integer", is_accept=True)

    dfa = DFA("q0", None, alphabet)
    dfa += q0, '+', q1
    dfa += q0, '-', q1
    for d in digits:
        dfa += q0, d, q2
        dfa += q1, d, q2
        dfa += q2, d, q2

    dfa.make_complete()

    assert dfa.accept(['1', '2', '3'])
    assert dfa.accept(['+', '5'])
    assert not dfa.accept(['-'])
    ```

=== "Cython"

    ```cython
    from pylgen.automaton cimport DFA, State

    cdef set digits = set("0123456789")
    cdef set alphabet = digits | {"+", "-"}

    cdef State q0 = State("q0", None)
    cdef State q1 = State("q1", None)
    cdef State q2 = State("q2", "integer", is_accept=True)

    cdef DFA dfa = DFA("q0", None, alphabet)
    dfa.add_transition(q0, q1, '+')
    dfa.add_transition(q0, q1, '-')
    for d in digits:
        dfa.add_transition(q0, q2, d)
        dfa.add_transition(q1, q2, d)
        dfa.add_transition(q2, q2, d)

    dfa.make_complete()

    assert dfa.accept(['1', '2', '3'])
    assert dfa.accept(['+', '5'])
    assert not dfa.accept(['-'])
    ```