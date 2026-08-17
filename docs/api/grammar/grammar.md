# From Theory to Implementation

In PyLGEN, the formal concepts are mapped directly to code:

 - **Non‑terminals** are instances of `Symbol` with `is_terminal=False`.

 - **Terminals** are `Symbol` objects with `is_terminal=True`.

 - **Productions** are represented by the `Production` class, which pairs a head (non‑terminal) with a list of symbols.

 - The **grammar** itself is encapsulated by the `Grammar` class (and its attributed variant `AttributedGrammar`), which manages the sets of symbols, production collections, and the start symbol.

The module also provides methods to compute the `FIRST` and `FOLLOW` sets, which are essential for constructing **LL** and **LR** parsers. These computations follow the algorithms described in standard compiler textbooks, but are implemented in a lazy, cached fashion to optimise performance.

## Core Classes

> ### `Production` (A Single Rewriting Rule)

A `Production` represents a context‑free production rule: `head -> production`, where `head` is a non‑terminal `Symbol` and `production` is a list of `Symbol` objects. It is immutable and hashable, making it suitable for use in sets and dictionaries.

#### Attributes and Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | A human‑readable string representation (e.g., `E -> E + T`). |
| **`head`** | `Symbol` | The left‑hand side non‑terminal. |
| **`production`** | `List[Symbol]` | The right‑hand side sequence (list of symbols). |

#### Creation and Usage

=== "Python"
    ```python
    from pylgen.common.types import Symbol
    from pylgen.grammar.grammar import Production

    E = Symbol('E')
    T = Symbol('T')
    plus = Symbol('+', is_terminal=True)

    # Production: E -> E + T
    p = Production(E, [E, plus, T])
    print(p.id)   # "E -> E + T"
    ```
=== "Cython"
    ```cython
    from pylgen.common.types cimport Symbol
    from pylgen.grammar.grammar cimport Production

    cdef Symbol E = Symbol('E')
    cdef Symbol T = Symbol('T')
    cdef Symbol plus = Symbol('+', is_terminal=True)

    # Production: E -> E + T
    cdef Production p = Production(E, [E, plus, T])
    print(p.id)   # "E -> E + T"
    ```

!!! warning
    The `head` symbol in the production must be a **non‑terminal**; a `ValueError` is thrown if you attempt to use a terminal.

    ```python
    p = Production(plus,[E,T]) # ValueError is thrown
    ```

#### Equality and Hashing

Two `Production` objects are equal if they have the same `head` and the same production list (order matters). The hash is computed deterministically from the `id` using SHA‑256, ensuring stable hashing across runs.

> ### `ProductionsSet` (Grouping Productions by Head)

`ProductionsSet` is a mutable container that holds all productions for a given non‑terminal `head`. It is used internally by `Grammar` to manage the productions of each symbol. It provides a convenient `+=` operator to add a new production.


#### Public API

| **Method/Operator** | **Description** |
| :---: | :---: |
| **`productions` (property)** | Returns a copy of all production lists as `List[List[Symbol]]`. |
| **`__iadd__`** | Adds a production given as a tuple of `Symbol`; returns self for chaining. |

#### Example

```python
from pylgen.grammar.grammar import ProductionsSet
from pylgen.common.types import Symbol

E = Symbol('E')
T = Symbol('T')
plus = Symbol('+', True)

ps = ProductionsSet()
ps += E, plus, T   # adds E -> E + T
ps += T,           # adds E -> T

print(ps.productions)  # [[E, plus, T], [T]]
```

> ### `AttributedProductionsSet` (Productions with Reductors)

`AttributedProductionsSet` extends `ProductionsSet` by allowing each production to carry an associated *reductor*, a callable that transforms the right‑hand side ASTs into a new AST node for the head. This is the cornerstone of attributed grammars.

#### Public API

 - **`__iadd__`**: expects a tuple of `(production_tuple, reductor)`, where `production_tuple` is a tuple of `Symbol` and `reductor` is a callable with signature `(ASTListView) -> AST`. The reductor's signature is validated at addition time (must be annotated with [`ASTListView`](../common/common.md#astlistview-a-lightweight-view-for-reducers) and return [`AST`](../common/common.md#ast-the-root-of-every-tree)).

#### Example

```python
from pylgen.grammar.grammar import AttributedProductionsSet
from pylgen.common.types import Symbol, ASTListView, AST

class MyAddAST(AST):
    # ...

def make_add(asts: ASTListView) -> AST:
    # asts[0] = left, asts[1] = plus token, asts[2] = right
    return MyAddAST(asts[0], asts[2])

E = Symbol('E')
T = Symbol('T')
plus = Symbol('+', True)

aps = AttributedProductionsSet()
aps += (E, plus, T), make_add
```

> ### `Grammar` (The Base Grammar Class)

`Grammar` is the central class for defining a context‑free grammar. It manages symbols, productions, and computes `FIRST` and `FOLLOW` sets lazily. It also provides utilities for converting the grammar to a dictionary representation.

#### Constructor

```python
Grammar(start_symbol: Symbol, end_symbol: str = '\x00')
```

 - `start_symbol`: the initial non‑terminal of the grammar.

 - `end_symbol`: a terminal symbol used as end‑of‑file marker (default `'\x00'`). It is automatically added as a terminal.

#### Public Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | Unique grammar identifier (SHA‑256 hash). |
| **`productions`** | `Set[Production]` | All productions in the grammar. |
| **`terminals`** |	`Set[Symbol]` | Set of terminal symbols. |
| **`non_terminals`** |	`Set[Symbol]` | Set of non‑terminal symbols. |
| **`symbols`** | `Set[Symbol]` | All symbols (terminals + non‑terminals). |
| **`start_symbol`** | `Symbol` | The start symbol. |
| **`end_symbol`** | `Symbol` |	The end‑of‑file symbol. |

#### Adding Productions

=== "Python"
    ```python
    from pylgen.grammar.grammar import Grammar
    from pylgen.common.types import Symbol

    # ...

    G = Grammar(E)

    G[E] += E, plus, T
    G[E] += T,
    ```
=== "Cython"
    ```cython
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.common.types cimport Symbol

    # ...

    cdef Grammar G = Grammar(E)

    G._add_production(E,[E,plus,T])
    G._add_production(E,[T])
    ```

When a new production is added:

 - New symbols are automatically registered (as terminals or non‑terminals).

 - `FIRST` and `FOLLOW` caches are invalidated (if previously computed), forcing recomputation on demand.


!!! warning
    Only one `epsilon` symbol can exist per grammar; the code throws a `ValueError` if you try to add another one.

#### Computing `FIRST` and `FOLLOW`

The grammar computes these sets lazily when `first()` or `follow()` is called for the first time. They are also used internally by the parser generator.

 - `first(production: List[Symbol]) -> Set[Symbol]`: returns the `FIRST` set of a sequence of symbols.

 - `follow(symbol: Symbol) -> Set[Symbol]`: returns the `FOLLOW` set of a symbol.

These methods raise `SymbolNotPresentInGrammarException` if any symbol in the input is not part of the grammar.

#### Static Utilities

| **Method** | **Description** |
| :---: | :---: |
| **`IsLeftRegular(g: Grammar) -> bool`** | Checks if the grammar is left‑regular. |
| **`IsRightRegular(g: Grammar) -> bool`** | Checks if the grammar is right‑regular. |
| **`IsRegular(g: Grammar) -> bool`** | Checks if the grammar is either left‑ or right‑regular. |
| **`AugmentGrammar(g: Grammar) -> Grammar`** | Creates a new grammar with a new start symbol `S'` and adds production `S' -> S`. |
| **`Reverse(g: Grammar) -> Grammar`** | Reverses the production bodies of every rule, yielding a grammar that recognizes the reversed language. |

#### Serialization

 - `to_dict() -> dict`: returns a dictionary representation of the grammar, listing terminals, non‑terminals, productions, and the epsilon symbol (if any). Useful for debugging or serialization.

> ### `AttributedGrammar` (Grammar with Reductors)

`AttributedGrammar` extends `Grammar` by storing a reductor for each production. It overrides `__getitem__` and `__setitem__` to work with `AttributedProductionsSet`, ensuring that every production added carries a reductor.

#### Constructor

Same as `Grammar`.

#### Public Method

 - `get_reductor(production: Production) -> Callable[[ASTListView], AST]`: returns the reductor associated with the given production.

#### Usage Example

=== "Python"
    ```python
    from pylgen.grammar.grammar import AttributedGrammar
    from pylgen.common.types import Symbol, ASTListView, AST

    class MyAddAST(AST):
        # ...

    E = Symbol('E')
    T = Symbol('T')
    plus = Symbol('+', True)

    def add_reductor(asts: ASTListView) -> AST:
        # build AST for addition
        return MyAddAST(asts[0], asts[2])

    def single_reductor(asts: ASTListView) -> AST:
        return asts[0]

    G = AttributedGrammar(E)
    G[E] += (E, plus, T), add_reductor
    G[E] += (T,), single_reductor   # single reductor
    ```
=== "Cython"
    ```cython
    from pylgen.grammar.grammar cimport AttributedGrammar
    from pylgen.common.types cimport Symbol, ASTListView, AST

    cdef class MyAddAST(AST):
        # ...

    cdef Symbol E = Symbol('E')
    cdef Symbol T = Symbol('T')
    cdef Symbol plus = Symbol('+', True)

    cdef AST add_reductor(ASTListView asts):
        # build AST for addition
        return MyAddAST(asts[0], asts[2])

    cdef AST single_reductor(ASTListView asts):
        return asts[0]

    G = AttributedGrammar(E)
    G._add_attributed_production(E,[E, plus, T], add_reductor)
    G._add_attributed_production(E, [T], single_reductor)   # single reductor
    ```

!!! warning
    In pure python, the reducer's signature is verified at addition time and must comply with the annotation `(ASTListView) -> AST`.

The parser builder uses the reductors stored in the attributed grammar to construct the AST during parsing.

> ### `SymbolNotPresentInGrammarException`

Exception raised when a method (e.g., `first()`, `follow()`) is called with a symbol that is not part of the grammar. It inherits from `Exception` and stores a descriptive message.

## Complete Example: Defining an Arithmetic Expression Grammar

Here is a minimal complete example that defines a simple arithmetic grammar with attributed productions (similar to the [tutorial](../../section-1/example-1-step-2.md#designing-our-language)).

=== "Python"
    ```python
    from pylgen.common.types import Symbol, ASTListView, AST
    from pylgen.grammar.grammar import AttributedGrammar

    # classes definitions
    # ...

    # Symbols
    E = Symbol('E')
    T = Symbol('T')
    F = Symbol('F')
    plus = Symbol('+', True)
    mul = Symbol('*', True)
    number = Symbol('number', True)
    lp = Symbol('(', True)
    rp = Symbol(')', True)

    # Reductors (simplified)
    def binary(asts: ASTListView) -> AST:
        return MyBinaryAST(asts[0], asts[2], asts[1])

    def single(asts: ASTListView) -> AST:
        return asts[0]

    def paren(asts: ASTListView) -> AST:
        return asts[1]

    # Build attributed grammar
    G = AttributedGrammar(E, end_symbol='$')
    G[E] += (E, plus, T), binary
    G[E] += (T,), single
    G[T] += (T, mul, F), binary
    G[T] += (F,), single
    G[F] += (lp, E, rp), paren
    G[F] += (number,), single
    ```
=== "Cython"
    ```cython
    from pylgen.common.types cimport Symbol, ASTListView, AST
    from pylgen.grammar.grammar cimport AttributedGrammar

    # classes definitions
    # ...

    # Symbols
    cdef Symbol E = Symbol('E')
    cdef Symbol T = Symbol('T')
    cdef Symbol F = Symbol('F')
    cdef Symbol plus = Symbol('+', True)
    cdef Symbol mul = Symbol('*', True)
    cdef Symbol number = Symbol('number', True)
    cdef Symbol lp = Symbol('(', True)
    cdef Symbol rp = Symbol(')', True)

    # Reductors (simplified)
    cdef AST binary(ASTListView asts):
        return MyBinaryAST(asts[0], asts[2], asts[1])

    cdef AST single(ASTListView asts):
        return asts[0]

    cdef AST paren(ASTListView asts):
        return asts[1]

    # Build attributed grammar
    cdef AttributedGrammar G = AttributedGrammar(E, end_symbol='$')
    G._add_attributed_production(E,[E, plus, T], binary)
    G._add_attributed_production(E,[T], single)
    G._add_attributed_production(T,[T, mul, F], binary)
    G._add_attributed_production(T,[F], single)
    G._add_attributed_production(F,[lp, E, rp], paren)
    G._add_attributed_production(F,[number], single)
    ```

This grammar correctly handles precedence (multiplication before addition) and parentheses.

## Summary

The `grammar` module is the linchpin that connects the lexical and syntactic phases. It provides a clean, Pythonic interface for defining context‑free and attributed grammars, computing essential sets, and preparing the grammar for parser generation. Its design emphasizes:

 - **Clarity**: Intuitive syntax for adding productions and reductors.

 - **Performance**: Lazy computation and Cython acceleration.

 - **Extensibility**: Easy to subclass or extend for custom grammar types (e.g., ambiguous grammars, with conflict resolution).

With this module, you can specify any context‑free language and automatically generate an efficient parser, complete with semantic actions. The rest of the pipeline, lexical analysis, parsing, and semantic processing, then integrates seamlessly to produce a full language implementation.

In the next module, we will explore the [`regex`](../regex/regex.md) engine, which underpins the lexer's pattern matching. But first, take a moment to experiment with the grammar API, it is the heart of your language definition.