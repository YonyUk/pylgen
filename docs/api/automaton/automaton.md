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
    print(s2.is_accept)         # True
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
    print(s2._is_accept)         # True

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
 - `make_complete() -> None`: Completes the automaton by adding a sink state (`FAULT`) and missing transitions pointing to it. It records the added transitions so the automaton can be restored to its previous state.
 - `restore_to_before_complete() -> None`: Removes the sink state and the added transitions, reverting the automaton to its original incomplete state.

> ### Overloaded Operators

| **Operator** | **Method** | **Return Type** | **Description** |
| :---: | :---: | :---: | :---: |
| `|` | `__or__` | `NFA` | Union of two automata. |
| `&` | `__and__` | `DFA` | Intersection of two automata. |
| `+` | `__add__` | `NFA` | Concatenation of two automata. |

These operators are syntactic sugar for the homonymous static methods (see below).

> ### Static Methods of `Automaton`: Language Operations

The `Automaton` class exposes static methods that implement the classical operations on regular languages. All of them return new automata (**they do not modify the originals**).

| **Method** | **Return Type** | **Description** |
| :---: | :---: | :---: |
| `Union(automatons: Set[Automaton])` | `NFA` | Constructs the union of several automata via a new initial state with ε‑transitions to each start state. |
| `Complement(automaton: Automaton)` | `DFA` | Computes the complement of the language. If the automaton is an `NFA`, it is determinized and minimized first. |
| `Intersection(automatons: Set[Automaton])` | `DFA` | Intersection via the Cartesian product of the corresponding DFAs. |
| `Concat(first: Automaton, second: Automaton)` | `NFA` | Concatenation: connects the end of the first to the start of the second using ε‑transitions from each final state of the first. |
| `KleeneStar(automaton: Automaton)` | `NFA` | Kleene star (`L*`): new start with an ε‑transition to the original start, and ε from finals to the new start. |
| `PositiveClosure(automaton: Automaton)` | `NFA` | Positive closure (`L+`): similar to Kleene but without making the new start accepting. |
| `Optional(automaton: Automaton)` | `NFA` | Optional operator (`?`, i.e. `L ∪ {ε}`): new accepting start with ε to the original start. |
| `Reverse(automaton: Automaton)` | `NFA` | Reverses the language: swaps source and target of each transition, reverses ε‑moves, and makes the initial state final and finals initial. |

All these operations leverage ε‑transitions to construct the new automata elegantly, and then (when necessary) they are determinized.

## The `DFA` Class (Deterministic Automata)

`DFA` inherits from `Automaton` and adds functionality specific to deterministic complete (or incomplete, but with completion support) automata.

> ### Constructor

=== "Python"
    ```python
    DFA(start_id: str, start_value: Any, alphabet: Set[str], start_accept: bool = False)
    ```
=== "Cython"
    ```cython
    DFA(str start_id, object start_value, set[str] alphabet, bint start_accept = False)
    ```

Creates a DFA with a single initial state (the one provided). Transitions and more states are added afterward.

> ### Specific Methods

 - `walk(symbol: str) -> None`: Advances the current state by consuming the symbol. If the transition does not exist, the automaton enters a stuck state (`_is_stuck = True`) and subsequent calls have no effect until `reset()`.

 - `accept(string: List[str]) -> bool`: Traverses the entire string (list of symbols) and returns True if, after consuming it, the current state is accepting. The automaton is automatically reset at the end.

 - `minimize(initial_partition: List[Set[State]] = []) -> DFA`: Applies **Hopcroft's algorithm** to minimize the DFA. Requires the automaton to be complete (if not, it **temporarily completes it and restores it** afterward). The initial_partition parameter allows specifying an initial partition (useful when additional information about equivalence classes is known). The result is a new minimized DFA.

 - `__iadd__(transition: Tuple[State, str, State]) -> DFA`: Allows adding transitions with the `+=` operator
```python
dfa += from_state, 'a', to_state
```

> ### Usage Example

=== "Python"
    ```python
    from pylgen.automaton import DFA, State

    # Create a DFA that accepts strings with an even number of 'a's
    dfa = DFA("q0", "even", {"a", "b"},True)
    q0 = dfa.start_state
    q1 = State("q1", "odd")
    dfa += q0, 'a', q1
    dfa += q1, 'a', q0
    dfa += q0, 'b', q0
    dfa += q1, 'b', q1

    assert dfa.accept(['a','b','a'])  # True
    ```
=== "Cython"
    ```cython
    from pylgen.automaton cimport DFA, State

    # Create a DFA that accepts strings with an even number of 'a's
    cdef DFA dfa = DFA("q0", "even", {"a", "b"},True)
    cdef State q0 = dfa.start_state
    cdef State q1 = State("q1", "odd")
    
    dfa.add_transition(q0, q1, 'a')
    dfa.add_transition(q1, q0, 'a')
    dfa.add_transition(q0, q0, 'b')
    dfa.add_transition(q1, q1, 'b')

    assert dfa.accept(['a','b','a'])  # True
    ```

## The `NFA` Class (Nondeterministic Automata with ε‑Moves)

`NFA` incorporates the ability to have ε‑transitions, directly modeling the hybrid ε‑DFA described in the theory.

> ### Constructor

Identical to the one for `DFA`.

> ### Specific Methods

 - `add_epsilon_transition(from_state: State, to_state: State) -> None`: Adds an ε‑transition between the given states.

 - `to_deterministic() -> DFA`: Converts the NFA into an equivalent DFA using the **subset (powerset) construction**.

 - `__iadd__` similar to DFA's, but for normal transitions (not ε).

> ### Example: Union via ε

=== "Python"
    ```python
    from pylgen.automaton import DFA, State

    # Automaton for "ab" and "cd"
    dfa1 = DFA("start", None, {"a","b","c","d"})
    # ... build ...
    dfa2 = DFA(...)

    union = dfa1 | dfa2   # Uses the overloaded operator
    # union is an NFA with a new initial state and ε to the starts of dfa1 and dfa2
    ```
=== "Cython"
    ```cython
    from pylgen.automaton cimport DFA,NFA,State,_automaton_union

    # Automaton for "ab" and "cd"
    cdef DFA dfa1 = DFA("start", None, {"a","b","c","d"})
    # ... build ...
    cdef DFA dfa2 = DFA(...)

    cdef NFA union = _automaton_union({dfa1,dfa2})   # Uses the C-method
    # union is an NFA with a new initial state and ε to the starts of dfa1 and dfa2
    ```

## Global Factory Functions

The module provides several helper functions to create automata from high-level specifications.

 - `create_dfa(states, transition_function, start_id, alphabet) -> DFA`: Builds a DFA from a set of states, a transition table (a `Table` object), the initial state identifier, and the alphabet. Useful for reconstructing automata from serialized representations.

 - `get_word_automaton(word: str) -> DFA`: Returns a DFA that recognizes exactly the given word (a string of characters). The alphabet is the set of characters in the word.

 - `get_words_automaton(words: List[str]) -> NFA`: Returns an NFA that recognizes the union of several words (one for each string in the list). Internally, it builds a DFA for each word and unions them with Union.

 - `get_word_automaton_with_value(word:str, value:Any, only_finals:bool=False) -> DFA`: Similar to `get_word_automaton`, but assigns the given `value` to the states. If `only_finals` is `True`, only the final states receive the value; the others get a generic identifier.

 - `get_words_automaton_with_value(words:str, value:Any, only_finals:bool=False) -> NFA`: Analogous, but for a set of words.

These functions are especially useful for building automata that associate semantic labels with final states, facilitating integration with lexical analyzers.

## Complete Example: Integer Recognizer

To illustrate combined usage, let us build an automaton that recognizes integers (optionally with a sign).

=== "Python"
    ```python
    from pylgen.automaton import DFA, State

    # Alphabet: digits and signs
    digits = set("0123456789")
    alphabet = digits | {"+", "-"}

    # States
    q0 = State("q0", None)                      # initial
    q1 = State("q1", None)                      # after sign
    q2 = State("q2", "integer", is_accept=True) # at least one digit

    dfa = DFA("q0", None, alphabet)
    dfa += q0, '+', q1
    dfa += q0, '-', q1
    for d in digits:
        dfa += q0, d, q2
        dfa += q1, d, q2
        dfa += q2, d, q2  # digit loop

    # Complete with a failure state (optional)
    dfa.make_complete()

    # Test
    assert dfa.accept(['1','2','3'])   # True
    assert dfa.accept(['+','5'])       # True
    assert dfa.accept(['-'])           # False (no digits)
    ```
=== "Cython"
    ```cython
    from pylgen.automaton cimport DFA, State

    # Alphabet: digits and signs
    cdef set digits = set("0123456789")
    cdef set alphabet = digits | {"+", "-"}

    # States
    cdef State q0 = State("q0", None)                      # initial
    cdef State q1 = State("q1", None)                      # after sign
    cdef State q2 = State("q2", "integer", is_accept=True) # at least one digit

    cdef DFA dfa = DFA("q0", None, alphabet)
    dfa.add_transition(q0, q1, '+')
    dfa.add_transition(q0, q1, '-')
    for d in digits:
        dfa.add_transition(q0, q2, d)
        dfa.add_transition(q1, q2, d)
        dfa.add_transition(q2, q2, d)  # digit loop

    # Complete with a failure state (optional)
    dfa.make_complete()

    # Test
    assert dfa.accept(['1','2','3'])   # True
    assert dfa.accept(['+','5'])       # True
    assert dfa.accept(['-'])           # False (no digits)
    ```

## Conclusion

The `automaton` module in PyLGEN not only implements the fundamental concepts of automata theory but does so with a design that prioritizes clarity, efficiency, and extensibility. From the immutability of states to the integration of complex operations such as minimization and determinization, every piece is built to offer a smooth and reliable development experience.

Whether used to build lexical analyzers, validate patterns, or explore properties of regular languages, this module provides a solid foundation that directly connects to the mathematical underpinnings presented.