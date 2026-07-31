# `pylgen.automaton` (The Theory in Action)

Having established the mathematical foundations of finite automata, from the classic DFA to the hybrid ε‑DFA, we now turn to the concrete implementation provided by PyLGEN. The `automaton` module materializes all that theory into a clear, efficient, and extensible API, designed both for manual automaton construction and for automatic generation from regular expressions or words.

Below, we break down its architecture, main classes, and functions, showing how each element faithfully reflects the theoretical concepts and how they all integrate to provide a powerful toolkit.

## The `State` Class: Immutability and Representation

Each state of an automaton is represented by an object of the `State` class. Its design is deliberately immutable: once created, its identifier, value, and acceptance status cannot be modified. This decision simplifies reasoning about the automaton and facilitates its use as keys in dictionaries and sets.

> ### Attributes and Properties

| **Property** | **Type** | **Default Value** | **Description** |
| :---: | :---: | :---: | :---: |
| **`id`** | `str` | **N/A** (required) | Unique identifier for the state. Two states with the same `id` are considered equal. |
| **`value`** | `Any` | **N/A** (required) | Any object associated with the state. This field is particularly useful for storing semantic information (e.g., the token or pattern it represents). |
| **`is_accept`** | `bool` | `False` | Indicates whether the state is an accepting (final) state. |

> ### Usage
=== "Python"
    ```python
    from pylgen.automaton import State

    s1 = State('s1','s1')       # non-accepting state
    s2 = State('s2',10,True)    # accepting state with value 10

    print(s1.id)                # 's1'
    print(s1.value)             # 's1'
    print(s1.is_accept)         # False

    print(s2.id)                # 's2'
    print(s2.value)             # 10
    print(s2,is_accept)         # True
    ```
=== "Cython"
    ```cython
    from pylgen.automaton cimport State

    cdef State s1 = State('s1','s1')       # non-accepting state
    cdef State s2 = State('s2',10,True)    # accepting state with value 10

    print(s1._id)                # 's1'
    print(s1._value)             # 's1'
    print(s1._is_accept)         # False

    print(s2._id)                # 's2'
    print(s2._value)             # 10
    print(s2,_is_accept)         # True

    ```

> ### Hash and Equality Behavior

The `__hash__` method is computed from the **SHA‑256** of the `id`, ensuring uniform distribution. Equality (`__eq__`) is based solely on the id, allowing two distinct State objects with the same identifier to be considered identical, a fundamental property for union and product operations.

```python
from pylgen.automaton import State

s1 = State("q0", "start", is_accept=False)
s2 = State("q0", "different value", is_accept=True)     # same id!

assert s1 == s2                                         # True, because they share the id
```

## The Base Class `Automaton`

`Automaton` is the abstract class from which `DFA` and `NFA` inherit. It provides the common infrastructure: state management, alphabet, transition function, ε-transitions, and derived properties. **It cannot be instantiated directly**; its constructor raises an exception.

> ### Attributes

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| `id` | `str` | Unique identifier for the automaton, computed from its structure (states, transitions, ε-moves, etc.). Two automata with the same content will have the same `id`, allowing semantic comparision. |
| `alphabet` | `Set[str]` | Copy of the alphabet. |
| `start_state` | `State` | Copy of the initial state. |
| `current_state` | `State` | Copy of the current state. |
| `states` | `Set[State]` | Set of all states. |
| `finals` | `Set[State]` | Set of accepting states. |
| `is_complete` | `bool` | `True` if the automaton is complete (all transitions defined). |
| `transition_function` | `Dict[Tuple[str,str],str]` | Dictionary of transitions. |
| `epsilon_transitions` | `Dict[str,Set[str]]` | Dictionary of ε-transitions. |
| `is_empty` | `bool` | Indicates whether the accepted language is empty. |
| `is_finite` | `bool` | Indicates whether the language is finite. |

> ### Core Methods

 - `add_transition(from_state:State,to_state:State,symbol:str) -> None`: Adds a deterministic transition (single target) for the given symbol. If the source or target state does not exist inside of the automata, it is created automatically. Raises `ValueError` if the symbol is not in the alphabet.
 - `has_transition(state:State, symbol:str) -> bool`: Checks whether a transition exists for the pair `(state, symbol)`.
 - `next(state:State, symbol:str) -> State`: Returns the target state for the transition. Raises `KeyError` if it does not exist.
 - `reset() -> None`: Resets the current state to the initial state.
 - `closure(state) -> Set[State]`: Computes the ε‑closure of the given state, using an internal cache to avoid recomputation. It implements an iterative stack-based traversal, correctly handling cyclic dependencies through a notification system.