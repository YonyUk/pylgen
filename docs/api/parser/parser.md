# `pylgen.parser` Module (The Syntactic Engine)

Welcome to the parser module, the intellectual heart of PyLGEN's syntactic analysis. If the lexer transforms a stream of characters into tokens, the parser transforms that token stream into an **Abstract Syntax Tree (AST)** , validating the grammatical structure of the input according to a context‑free grammar. This is where the theoretical elegance of LR parsing meets the practical demands of real‑world language processing.

The parser module implements **LALR(1) parser generation** from context‑free grammars, following the classic algorithms described in the "Dragon Book" (Aho, Sethi, and Ullman). It builds upon the `grammar` module, using `FIRST` and `FOLLOW` sets to construct the `ACTION` and `GOTO` tables that drive the parsing process. The module is designed to be both **correct** and **fast**, with Cython‑optimized parsing routines that can handle thousands of tokens per second.

This module is also where **attributed grammars** come to life: the parser invokes user‑defined reductors during reductions, building the AST incrementally as the input is consumed. The separation between parser generation (done once, offline) and parsing (done at runtime) allows for efficient, reusable parsers.

## Formal Foundations: LR Parsing

LR parsing is a **bottom‑up**, **shift‑reduce** parsing technique that reads input from left to right (L) and produces a rightmost derivation in reverse (R). It is one of the most powerful and general parsing methods, capable of handling virtually all context‑free grammars that are not ambiguous.

An LR parser consists of:

 - **`1` A parsing table** with two parts:
    - **`ACTION`**: Given the current parser state and the current lookahead token, tells the parser whether to *shift* (consume the token and push a new state), reduce (apply a production), or accept.
    - **`GOTO`**: Given a state and a non‑terminal, tells the parser which state to transition to after a reduction.
 - **`2` A stack** that holds states, grammar symbols, and AST nodes (or parse tree nodes).
 - **`3` A driver loop** that repeatedly consults the **`ACTION`** table, performs the indicated operation, and updates the stack.

The LR parsing algorithm is elegant and efficient: it runs in linear time, requires no backtracking, and can detect syntax errors as soon as they occur. The `BottomUpParser` class is a direct implementation of this algorithm.

> ### LR Items and States

The construction of an LR parser begins with **LR(0) items**, which represent a production with a dot somewhere in its right‑hand side. For example, the production $E \rightarrow E + T$ gives rise to the items:

 - $E \rightarrow \cdot E + T$ (dot at the begining).
 - $E \rightarrow E \cdot + T$ (dot before the `+`).
 - $E \rightarrow E + \cdot T$ (dot before `T`).
 - $E \rightarrow E + T \cdot$ (dot at the end, indicating a completed production).

An **LR(0) state** is a set of LR(0) items that are reachable from the start state via a sequence of symbols. The collection of all such states forms the **canonical LR(0) automaton**. This automaton is the foundation for constructing the parsing tables.

> ### LALR(1) Lookaheads

While LR(0) parsers are simple to build, they are too weak for many practical grammars (they cannot resolve shift‑reduce conflicts). **SLR** and **LALR(1)** parsers address this by adding **lookahead** information to the items:

 - In an **LALR(1) item**, each LR(0) item is augmented with a set of lookahead symbols. The lookahead set tells the parser which terminals can legally follow the production when it is used in a reduction.

 - The lookaheads are computed using a propagation algorithm that starts with the lookahead `$` (end‑of‑file) for the initial item and propagates lookaheads through transitions in the LR(0) automaton.

The LALR(1) construction merges LR(0) states that have identical kernels (the items without lookaheads), then computes the lookaheads for the merged states. This results in a parser that is almost as powerful as a full LR(1) parser but with a much smaller number of states (comparable to LR(0)).

## Core Classes

> ### `LR0Item` and `LALRItem` (Parser Items)

These classes represent the fundamental units of LR parsing: items with (for LALR) or without (for LR0) lookahead sets.

#### `LR0Item`

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | Human‑readable representation (e.g., `E -> E ◦ + T`). |
| **`head`** | `Symbol` | The non‑terminal on the left‑hand side. |
| **`left`** | 	`list[Symbol]` | The symbols before the dot. |
| **`right`** | `list[Symbol]` | The symbols after the dot. |

The hash of an `LR0Item` is computed deterministically from its string representation, ensuring stable hashing across runs.

#### `LALRItem` (extends `LR0Item`)

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`lookaheads`** | `Set[Symbol]` | The set of terminal symbols that can follow this item. |

The equality semantics for `LALRItem` include the lookahead set, so two items are equal only if they have the same `head`, `left`, `right`, and identical `lookaheads`.

> ### `LR0State` and `LALRState` (Parser States)

States are sets of items. Each state has a unique identifier (a hash of its items) and an index (assigned during construction).

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | A unique hash‑based identifier for the state. |
| **`index`** |	`int` | A sequential index (0, 1, 2, ...) assigned during state construction. |
| **`items`** |	`Set[LALRItem]` or `Set[LR0Item]` | The items in this state. |

The `index` is used to create human‑readable state names (`I0`, `I1`, etc.) in the parsing tables.

> ### `ParseTreeNode` (Parse Tree Node)

When the parser is configured to draw the parse tree (via `set_draw_parse_tree_flag(True)`), it builds a tree of `ParseTreeNode` objects that mirrors the syntactic derivation.

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`symbol`** | `Symbol` | The grammar symbol at this node. |
| **`line`** | `int` | The source line where this node begins. |
| **`column`** | `int` | The source column where this node begins. |
| **`childrens`** |	`List[ParseTreeNode]` | The child nodes in the derivation. |

This is the raw parse tree, which includes all non‑terminals and terminals. It is useful for debugging and for visualisation (the `visual` module uses it to draw parse trees).

> ### `Parser` (Abstract Base Class)

The abstract base class for all parsers. It defines the public interface that all concrete parsers must implement.

#### Public Methods

| **Method** | **Description** |
| :---: | :---: |
| **`parse(tokens: Iterable[Token]) -> AST`** | Parses the token stream and returns the AST root. Raises no exception on error; instead, errors are stored in `errors` and parsing continues (error recovery). |
| **`reset()`** | Resets the parser to its initial state, clearing the stack and errors.
| **`set_draw_parse_tree_flag(flag: bool)`** | If `True`, the parser builds a parse tree during parsing (available via the `parse_tree` property). |

!!! important
    The token's stream must always end with an `EOF` token, so the parser can accept it. This token comes from the lexer.

#### Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`parse_tree`** | `ParseTreeNode` | The root of the parse tree (if `draw_parse_tree` is `True` and parsing succeeded). |
| **`errors`** | `List[SyntaxError]` | The list of syntax errors encountered during parsing. |

> ### `BottomUpParser` (The LR Parser)

`BottomUpParser` is the concrete implementation of an LR parser. It is instantiated with pre‑computed `ACTION` and `GOTO` tables and then used to parse token streams.

#### Constructor

```python
BottomUpParser(start_state: str, goto_table: Dict[Tuple[str, Symbol], str], action_table: Dict[Tuple[str, Symbol], tuple[str, str | Production]])
```

 - **`start_state`**: The identifier of the initial state (typically `'I0'`).

 - **`goto_table`**: Maps `(state_id, non_terminal)` to the next state ID.

 - **`action_table`**: Maps `(state_id, terminal)` to a tuple `(action, value)` where `action` is `'SHIFT'`, `'REDUCE'`, or `'ACCEPT'`, and `value` is either a state ID (for shift) or a `Production` (for reduce).

#### Methods

 - **`__setitem__(self,production:Production,reductor:Callable[[ASTListView],AST])`**: sets the reducer function for the given production.

> ### `ParserBuilder` (The Parser Generator)

`ParserBuilder` is a static class that constructs parsers from grammars. It implements the LALR(1) construction algorithm, including:

 - `1`. Computing `FIRST` and `FOLLOW` sets (from the grammar module).

 - `2`. Building the canonical LR(0) states.

 - `3`. Computing lookahead propagation for LALR(1).

 - `4`. Constructing the `ACTION` and `GOTO` tables.

 - `5`. Handling conflicts (shift‑reduce and reduce‑reduce) by raising appropriate exceptions.

#### Public Static Methods

| **Method** | **Description** |
| :---: | :---: |
| **`build_parser(g: Grammar, type_: ParserType) -> Parser`** | Builds a parser from a grammar (without reductors). Currently supports `ParserType.LALR1`; others raise `NotImplementedError`. |
| **`build_parser_from_attributed(g: AttributedGrammar, type_: ParserType) -> Parser`** | Builds a parser from an attributed grammar, attaching reductors to productions. |
| **`clear_cache()`** | Clears the internal cache of closures and states. Useful when modifying grammars dynamically. |

!!! note
    `build_parser` and `build_parser_from_attributed` automatically augments the grammar. 

> ### Conflict Exceptions

LALR(1) grammars can sometimes have conflicts, where the parser cannot decide between shifting and reducing (shift‑reduce conflict) or between two different reductions (reduce‑reduce conflict). The parser builder detects these conflicts and raises specific exceptions that include detailed information for debugging.

| **Exception** | **Description** |
| :---: | :---: |
| **`LALRShiftReduceConflictException`** | Raised when a state has both a SHIFT and a REDUCE action for the same lookahead symbol. Includes the state, symbol, the next state (for shift), and the production (for reduce). |
| **`LALRReduceReduceConflictException`** | Raised when a state has two different REDUCE actions for the same lookahead symbol. Includes the state, symbol, and the two conflicting productions. |

These exceptions allow you to inspect the conflict and, if necessary, resolve it by modifying the grammar (e.g., by changing precedence, restructuring productions, or adding disambiguation rules).

> ### Integration with Attributed Grammars

The parser's ability to build ASTs comes from its integration with attributed grammars. The `ParserBuilder.build_parser_from_attributed` method attaches a reductor to each production in the `AttributedGrammar`. When the parser performs a reduce action, it looks up the reductor for that production and invokes it with an `ASTListView` containing the children AST nodes.

The `ASTListView` is a lightweight, immutable view over the AST stack. It provides:

 - Indexed access to children (0‑based).

 - Length (number of children).

 - It is implemented as a view over the internal stack, so it does not copy any data, making it extremely efficient.

## Code Examples

> ### Building a Parser from a Grammar

=== "Python"

    ```python
    from pylgen.grammar.grammar import Grammar
    from pylgen.parser.parser_builder import ParserBuilder
    from pylgen.parser.parser_type import ParserType
    from pylgen.common.types import Symbol

    # Define the grammar
    E = Symbol('E')
    T = Symbol('T')
    plus = Symbol('+', True)
    number = Symbol('number', True)

    G = Grammar(E)
    G[E] += E, plus, T
    G[E] += T,
    G[T] += number,

    # Build a parser
    parser = ParserBuilder.build_parser(G, ParserType.LALR1)
    ```

=== "Cython"

    ```cython
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.parser.parser_builder cimport _build_lalr_parser 
    from pylgen.parser.parser cimport BottomUpParser
    from pylgen.parser.parser_type import ParserType
    from pylgen.common.types cimport Symbol

    # Define the grammar
    cdef Symbol E = Symbol('E')
    cdef Symbol T = Symbol('T')
    cdef Symbol plus = Symbol('+', True)
    cdef Symbol number = Symbol('number', True)

    cdef Grammar G = Grammar(E)
    G._add_production(E,[E, plus, T])
    G._add_production(E,[T])
    G._add_production(T,[number])

    # Build a parser
    cdef BottomUpParser parser = _build_lalr_parser(G)
    ```

> ### Building an Attributed Parser with Reductors

=== "Python"

    ```python
    from pylgen.grammar.grammar import AttributedGrammar
    from pylgen.parser.parser_builder import ParserBuilder
    from pylgen.common.types import ASTListView, AST

    # Define a reductor
    def add_reductor(asts: ASTListView) -> AST:
        return MyAddAST(asts[0], asts[2])

    def single_reductor(asts: ASTListView) -> AST:
        return asts[0]

    G = AttributedGrammar(E)
    G[E] += (E, plus, T), add_reductor
    G[E] += (T,), single_reductor

    parser = ParserBuilder.build_parser_from_attributed(G, ParserType.LALR1)
    ```

=== "Cython"

    ```cython
    from pylgen.grammar.grammar cimport AttributedGrammar
    from pylgen.parser.parser_builder cimport _build_lalr_parser_from_attribute
    from pylgen.parser.parser cimport BottomUpParser
    from pylgen.common.types cimport ASTListView, AST

    # Define a reductor
    cdef AST add_reductor(ASTListView asts):
        return MyAddAST(asts._get(0), asts._get(2))
    
    cdef AST single_reductor(ASTListView asts):
        return asts._get(0)

    cdef AttributedGrammar G = AttributedGrammar(E)
    G._add_attributed_production(E,[E, plus, T], add_reductor)
    G._add_attributed_production(E,[T] single_reductor)

    cdef BottomUpParser parser = _build_lalr_parser_from_attribute(G)
    ```


> ### Parsing and Error Handling

```python

# ... configure lexer and parser ...

lexer.load_text("1 + 2 * 3")
ast = parser.parse(lexer.tokens)

if parser.errors:
    for error in parser.errors:
        print(error)
else:
    print("Parsing successful!")
    # ast is the root of the AST
```

## Summary

The `parser` module is the culmination of the grammar module, implementing a full LALR(1) parser generator and runtime. With this module, you can go from a grammar specification to a working parser in a few lines of code. The parser generated by PyLGEN is production‑grade, capable of handling the syntax of complex languages with ease.

In the next and final module, we will explore the **analysis** module, which provides the framework for semantic analysis, visitors, and traversal strategies, the tools you need to give meaning to the AST that the parser produces.