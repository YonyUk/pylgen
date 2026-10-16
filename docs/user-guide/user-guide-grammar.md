# The `grammar` Module

The `grammar` module provides the basic tools for defining grammars in PyLGEN: productions, sets of productions, and grammars; both context-free and attributed. Details regarding each class, its attributes, and its methods are explained in the following sections.

!!! note "New to grammars?" 
    If you are unsure about what a non-terminal, a terminal, or a production is, start with [Key Concepts](../getting-started/key-concepts.md) or [Formal Grammars](../formal-foundations/formal-foundations-context-free-grammars.md).

## `Production`

A `Production` is a rule $A \rightarrow \alpha$.

> ### Attributes and Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | A human‑readable string representation (e.g., `E -> E + T`). |
| **`head`** | `Symbol` | The left‑hand side non‑terminal. |
| **`production`** | `List[Symbol]` | The right‑hand side sequence (list of symbols). |

> ### Typical Usage

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

!!! important "`Production`'s equality"
    Two `Production` objects are equal if they have the same `head` and the same production list (order matters).


## `ProductionsSet`

`ProductionsSet` is a mutable container that holds all productions for a given non‑terminal `head`. It is used internally by `Grammar` to manage the productions of each symbol. It provides a convenient `+=` operator to add a new production.


> ### Methods

| **Method/Operator** | **Description** |
| :---: | :---: |
| **`productions` (property)** | Returns a copy of all production lists as `List[List[Symbol]]`. |
| **`__iadd__`** | Adds a production given as a tuple of `Symbol`; returns self for chaining. |

> ### Usage

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

## `AttributedProductionsSet`

`AttributedProductionsSet` extends `ProductionsSet` by allowing each production to carry an associated *reductor*, a callable that transforms the right‑hand side ASTs into a new AST node for the head. This is the cornerstone of attributed grammars.

!!! note "The origin of the term "reductor" (or "reducer")"
    It stems from the `REDUCE` action of an LR parser. In LR parsing, upon recognizing a production, the parser performs a reduction: it replaces a sequence of symbols with a non-terminal and triggers the associated semantic action. In PyLGEN, the semantic value of each symbol is an AST; thus, this action takes the ASTs of the symbols on the right-hand side of the production and returns the AST corresponding to the non-terminal that replaces those symbols. This function is the "reductor": it reduces a list of child ASTs into a single parent AST. The parser invokes it during a `REDUCE` action (the corresponding syntactic operation); the reducer constitutes the semantic reduction action. Hence the name: it collapses the right-hand side ASTs into a single AST for the left-hand side non-terminal.

> ### Methods

 - **`__iadd__`**: expects a tuple of `(production_tuple, reductor)`, where `production_tuple` is a tuple of `Symbol` and `reductor` is a callable with signature `(ASTListView) -> AST`. The reductor's signature is validated at addition time (must be annotated with [`ASTListView`](../user-guide-common#astlistview) and return [`AST`](../user-guide-common#ast)).

> ### Usage

```python
from pylgen.grammar.grammar import AttributedProductionsSet
from pylgen.common.types import Symbol, ASTListView, AST

class MyAddAST(AST):
    # ...

def make_add(asts: ASTListView) -> AST:
    return MyAddAST(asts[0], asts[2])

E = Symbol('E')
T = Symbol('T')
plus = Symbol('+', True)

aps = AttributedProductionsSet()
aps += (E, plus, T), make_add
```

## `Grammar`

`Grammar` is the central class for defining a context‑free grammar. It manages symbols, productions, and computes `FIRST` and `FOLLOW` sets lazily. It also provides utilities for converting the grammar to a dictionary representation.

> ### Constructor

```python
Grammar(start_symbol: Symbol, end_symbol: str = '\x00')
```

 - `start_symbol`: the initial non‑terminal of the grammar.

 - `end_symbol`: a terminal symbol used as end‑of‑file marker (default `'\x00'`). It is automatically added as a terminal.

> ### Attributes

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | Unique grammar identifier |
| **`productions`** | `Set[Production]` | All productions in the grammar. |
| **`terminals`** |	`Set[Symbol]` | Set of terminal symbols. |
| **`non_terminals`** |	`Set[Symbol]` | Set of non‑terminal symbols. |
| **`symbols`** | `Set[Symbol]` | All symbols (terminals + non‑terminals). |
| **`start_symbol`** | `Symbol` | The start symbol. |
| **`end_symbol`** | `Symbol` |	The end‑of‑file symbol. |

> ### Methods

| **Method** | **Return Type** | **Description** |
| :---: | :---: | :---: |
| <span style="white-space: nowrap">**`first(production: List[Symbol])`**</span> | <span style="white-space: nowrap">**`Set[Symbol]`**</span> | returns the `FIRST` set of a sequence of symbols. |
| <span style="white-space: nowrap">**`follow(symbol: Symbol)`**</span> | <span style="white-space: nowrap">**`Set[Symbol]`**</span> | returns the `FOLLOW` set of a symbol |
| **`to_dict()`** | **`dict`** | returns a dictionary representation of the grammar, listing terminals, non‑terminals, productions, and the epsilon symbol (if any). Useful for debugging or serialization. |

!!! warning
    A `SymbolNotPresentInGrammarException` is raised if any symbol in the input is not part of the grammar.

> ### Static Utilities

| **Method** | **Description** |
| :---: | :---: |
| **`IsLeftRegular(g: Grammar) -> bool`** | Checks if the grammar is left‑regular. |
| **`IsRightRegular(g: Grammar) -> bool`** | Checks if the grammar is right‑regular. |
| **`IsRegular(g: Grammar) -> bool`** | Checks if the grammar is either left‑ or right‑regular. |
| **`AugmentGrammar(g: Grammar) -> Grammar`** | Creates a new grammar with a new start symbol `S'` and adds production `S' -> S`. |
| **`Reverse(g: Grammar) -> Grammar`** | Reverses the production bodies of every rule, yielding a grammar that recognizes the reversed language. |

> ### Typical Usage

=== "Python"

    ```python
    from pylgen.grammar.grammar import Grammar
    from pylgen.common.types import Symbol

    # symbols definitions ...

    G = Grammar(E)

    G[E] += E, plus, T
    G[E] += T,
    ```

=== "Cython"
    
    ```cython
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.common.types cimport Symbol

    # symbols definitions ...

    cdef Grammar G = Grammar(E)

    G._add_production(E,[E,plus,T])
    G._add_production(E,[T])
    ```

!!! warning
    Only one `epsilon` symbol can exist per grammar; the code throws a `ValueError` if you try to add another one.

## `AttributedGrammar`

`AttributedGrammar` extends `Grammar` by storing a reductor for each production. It overrides `__getitem__` and `__setitem__` to work with `AttributedProductionsSet`, ensuring that every production added carries a reductor.

> ### Methods

 - `get_reductor(production: Production) -> Callable[[ASTListView], AST]`: returns the reductor associated with the given production.

> ### Typical Usage

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
        return MyAddAST(asts._get(0), asts._get(2))

    cdef AST single_reductor(ASTListView asts):
        return asts._get(0)

    G = AttributedGrammar(E)
    G._add_attributed_production(E,[E, plus, T], add_reductor)
    G._add_attributed_production(E, [T], single_reductor)   # single reductor
    ```

!!! warning
    In pure python, the reducer's signature is verified at addition time and must comply with the annotation `(ASTListView) -> AST`.

The parser builder uses the reductors stored in the attributed grammar to construct the AST during parsing.

## Complete Example: Defining an Arithmetic Expression Grammar

Here is a minimal complete example that defines a simple arithmetic grammar with attributed productions (similar to the [Quick Start: Step 6 example](../getting-started/quick-start.md#step-6-attributed-grammar)).

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
        return MyBinaryAST(asts._get(0), asts._get(2), asts._get(1))

    cdef AST single(ASTListView asts):
        return asts._get(0)

    cdef AST paren(ASTListView asts):
        return asts._get(1)

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