# `pylgen.parser` Module (The Syntactic Engine)

Welcome to the parser module, the intellectual heart of PyLGEN's syntactic analysis. If the lexer transforms a stream of characters into tokens, the parser transforms that token stream into an **Abstract Syntax Tree (AST)** , validating the grammatical structure of the input according to a context‑free grammar. This is where the theoretical elegance of [LR parsing](https://en.wikipedia.org/wiki/LR_parser) meets the practical demands of real‑world language processing.

The parser module implements **LALR(1) parser generation** from context‑free grammars, following the classic algorithms described in the ["Dragon Book"](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools) (Aho, Sethi, and Ullman). It builds upon the [`grammar`](../grammar/intro.md) module, using `FIRST` and `FOLLOW` sets to construct the `ACTION` and `GOTO` tables that drive the parsing process. The module is designed to be both **correct** and **fast**, with Cython‑optimized parsing routines that can handle thousands of tokens per second.

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

For more powerful parsers, additional lookahead information is added to the items:

 - **SLR (Simple LR)** parsers use the `FOLLOW` sets of the grammar to decide when to reduce. During table construction, each LR(0) state with a completed item (dot at the end) generates reduce actions for all terminals in the `FOLLOW` set of the production's head. This is a simple and efficient approach, but it is not powerful enough for many practical grammars.

 - **LR(1)** items extend LR(0) items with a **single lookahead terminal**. An LR(1) item is written as [$A \rightarrow \alpha \cdot \beta,a$] where $a$ is a terminal that must follow the production. The closure and goto operations are augmented to propagate these lookaheads precisely. LR(1) parsers are the most powerful (they can handle any deterministic context‑free language), but they can generate a very large number of states (often hundreds or thousands).

 - **LALR(1) (Look‑Ahead LR)** items also carry lookahead information, but they use **set of lookaheads** (instead of a single one) and merge LR(0) states that have identical kernels (the items without lookaheads). This reduces the number of states to that of LR(0), while still retaining much of the power of LR(1). The lookaheads are computed using a propagation algorithm that starts with the lookahead `$` (end‑of‑file) for the initial item and propagates lookaheads through transitions in the LR(0) automaton.

## Core Classes

> ### `LR0Item`, `LR1Item` and `LALRItem` (Parser Items)

These classes represent the fundamental units of LR parsing: items with (for LALR) or without (for LR0) lookahead sets.

#### `LR0Item` (Parser Item without Lookahead)

`LR0Item` represents the fundamental unit of **LR(0) parsing**: a production with a dot somewhere in its right-hand side. It does not carry lookahead information.

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | Human‑readable representation (e.g., `E -> E ◦ + T`). |
| **`head`** | `Symbol` | The non‑terminal on the left‑hand side. |
| **`left`** | 	`list[Symbol]` | The symbols before the dot. |
| **`right`** | `list[Symbol]` | The symbols after the dot. |

The `LR0Item` equality and hashing include the lookahead, making each item unique based on the full LR(1) context, so two items are equal only if they have the same `head`, `left`, and `right`.

#### `LR1Item` (Parser Item with Single Lookahead)

`LR1Item` extends `LR0Item` by adding a single lookahead symbol. This is used in **full LR(1) parser** construction, where each item is augmented with a specific terminal that can follow the production.

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`lookahead`** | `Symbol` | The terminal symbol that can follow this item. |

The `LR1Item` equality and hashing include the lookahead, making each item unique based on the full LR(1) context, so two items are equal only if they have the same `head`, `left`, `right`, and identical `lookahead`.

#### `LALRItem` (Parser Item with Lookahead Set)

`LALRItem` extends `LR0Item` by adding a set of lookahead symbols. This is used in **LALR(1) parser** construction, where multiple lookaheads are merged from **LR(1) items** that share the same kernel.

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`lookaheads`** | `Set[Symbol]` | The set of terminal symbols that can follow this item. |

The `LALRItem` equality and hashing include the lookaheads set, making each item unique based on the full LR(1) context, so two items are equal only if they have the same `head`, `left`, `right`, and identical `lookaheads`.

> ### `LR0State`, `LR1State`, and `LALRState` (Parser States)

States are sets of items. Each state has a unique identifier (a hash of its items) and an index (assigned during construction).

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`id`** | `str` | A unique hash‑based identifier for the state. |
| **`index`** |	`int` | A sequential index (0, 1, 2, ...) assigned during state construction. |
| **`items`** |	`Set[LALRItem]`,`Set[LR1Item]` or `Set[LR0Item]` | The items in this state. |

The `index` is used to create human‑readable state names (`I0`, `I1`, etc.) in the parsing tables.

> ### `ParseTreeNode` (Parse Tree Node)

When the parser is configured to draw the parse tree (via `set_draw_parse_tree_flag(True)`), it builds a tree of `ParseTreeNode` objects that mirrors the syntactic derivation.

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`symbol`** | `Symbol` | The grammar symbol at this node. |
| **`line`** | `int` | The source line where this node begins. |
| **`column`** | `int` | The source column where this node begins. |
| **`childrens`** |	`List[ParseTreeNode]` | The child nodes in the derivation. |

This is the raw parse tree, which includes all non‑terminals and terminals. It is useful for debugging and for visualisation (the [`visual`](../visual/visual.md) module uses it to draw parse trees).

> ### `Parser` (Abstract Base Class)

The abstract base class for all parsers. It defines the public interface that all concrete parsers must implement.

#### Public Methods

| **Method** | **Description** |
| :---: | :---: |
| <span style="white-space: nowrap">**`parse(tokens: Iterable[Token]) -> AST`**</span> | Parses the token stream and returns the AST root. Raises no exception on error; instead, errors are stored in `errors` and parsing continues (error recovery). |
| **`reset()`** | Resets the parser to its initial state, clearing the stack and errors.
| **`set_draw_parse_tree_flag(flag: bool)`** | If `True`, the parser builds a parse tree during parsing (available via the `parse_tree` property). |

!!! important
    The `parse` method assumes that the provided iterable of tokens contains exactly one `EOF` token at the end and that no further tokens are supplied after it. If parse is called with an iterable that continues after the `EOF`, a `ValueError` is raised internally (the implementation checks for this condition). In practice, this situation does not occur if your lexer emits a single `EOF` at the end of the input.

#### Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`parse_tree`** | `ParseTreeNode` | The root of the parse tree (if `draw_parse_tree` is `True` and parsing succeeded). |
| **`errors`** | `List[Error]` | The list of errors encountered during parsing. |

> ### `BottomUpParser` (The LR Parser)

`BottomUpParser` is the concrete implementation of an LR parser. It is instantiated with pre‑computed `ACTION` and `GOTO` tables and then used to parse token streams.

#### Constructor

```python
BottomUpParser(start_state: str, goto_table: Dict[Tuple[str, Symbol], str], action_table: Dict[Tuple[str, Symbol], tuple[str, str | Production]])
```

!!! important
    In the `action_table`, the first element of the tuple is a string that can be `'SHIFT'`, `'REDUCE'`, or `'ACCEPT'`. For `'SHIFT'`, the second element is a string with the destination state identifier (e.g., `'I5'`); for `'REDUCE'`, it is an instance of `Production`; for `'ACCEPT'`, the second element may be `None` (although the type hint does not reflect it, the internal implementation handles this case).

 - **`start_state`**: The identifier of the initial state (typically `'I0'`).

 - **`goto_table`**: Maps `(state_id, non_terminal)` to the next state ID.

 - **`action_table`**: Maps `(state_id, terminal)` to a tuple `(action, value)` where `action` is `'SHIFT'`, `'REDUCE'`, or `'ACCEPT'`, and `value` is either a state ID (for shift) or a `Production` (for reduce).

#### Methods

 - **`__setitem__(self,production:Production,reductor:Callable[[ASTListView],AST])`**: sets the reducer function for the given production.

> ### `ParserBuilder` (The Parser Generator)

`ParserBuilder` is a static class that constructs parsers from grammars.  It implements the parser construction algorithms for **SLR**, **LR(1)**, and **LALR(1)** parsers, including:

 - `1`. Computing `FIRST` and `FOLLOW` sets (from the grammar module).

 - `2`. Building the canonical LR(0) states.

 - `3`. Computing lookahead propagation for LALR(1).

 - `4`. Constructing the `ACTION` and `GOTO` tables.

 - `5`. Handling conflicts (shift‑reduce and reduce‑reduce) by raising appropriate exceptions.

#### Public Static Methods

| **Method** | **Description** |
| :---: | :---: |
| **`build_parser(g: Grammar, type_: ParserType) -> Parser`** | Builds a parser from a grammar (without reductors). Supports `SLR`, `LR1`, and `LALR1` parser types. |
| **`build_parser_from_attributed(g: AttributedGrammar, type_: ParserType) -> Parser`** | Builds a parser from an attributed grammar, attaching reductors to productions. |
| **`clear_cache()`** | Clears the internal cache of closures and states. Useful when modifying grammars dynamically. |
| **`closure_lr0(items: Set[LR0Item], g: Grammar) -> Set[LR0Item]`** | Computes the LR(0) closure of a set of items. |
| **`closure_lr1(items: Set[LR1Item], g: Grammar) -> Set[LR1Item]`** | Computes the LR(1) closure of a set of items. |
| **`closure_lalr(items: Set[LALRItem], g: Grammar) -> Set[LALRItem]`** | Computes the LALR(1) closure of a set of items (including lookahead propagation). |
| **`goto_lr0(items: Set[LR0Item], x: Symbol, g: Grammar) -> Set[LR0Item]`** | Computes the LR(0) `GOTO` of a set of items on symbol `x`. |
| **`goto_lr1(items: Set[LR1Item], x: Symbol, g: Grammar) -> Set[LR1Item]`** | Computes the LR(1) `GOTO` of a set of items on symbol `x`. |
| **`goto_lalr(items: Set[LALRItem], x: Symbol, g: Grammar) -> Set[LALRItem]`** | Computes the LALR(1) `GOTO` of a set of items on symbol `x`. |
| **`get_canonical_lr0_states(g: Grammar) -> Set[LR0State]`** | Returns the canonical collection of LR(0) states for the grammar. |
| **`get_canonical_lr1_states(g: Grammar) -> Set[LR1State]`** | Returns the canonical collection of LR(1) states for the grammar. |
| **`get_canonical_lalr_states(g: Grammar) -> Set[LALRState]`** | Returns the canonical collection of LALR(1) states. |
| **`get_kernel_items_lr0(state: LR0State, g: Grammar) -> Set[LR0Item]`** | Extracts the kernel items (items with dot not at the beginning) from an LR(0) state. |
| **`get_kernel_items_lr1(state: LR1State, g: Grammar) -> Set[LR1Item]`** | Extracts the kernel items (items with dot not at the beginning) from an LR(1) state. |
| **`get_kernel_items_lalr(state: LALRState, g: Grammar) -> Set[LALRItem]`** | Extracts the kernel items from an LALR(1) state. |
| **`build_lookaheads_propagation_edges(g: Grammar) -> Tuple[Dict[LR0State, Dict[Tuple[LR0Item, Symbol], Tuple[LR0State, LR0Item]]], Set[LR0State]]`** | Builds the lookahead propagation edges used in LALR(1) construction. |
| **`get_goto_action_tables_slr(g: Grammar) -> Tuple[Dict[Tuple[LR0State, Symbol], LR0State], Dict[Tuple[LR0State, Symbol], Tuple[str, LR0State | Production]]]`** | Returns the `GOTO` and `ACTION` tables as dictionaries keyed by `(LR0State, Symbol)`. |
| **`get_goto_action_tables_lr1(g: Grammar) -> Tuple[Dict[Tuple[LR1State, Symbol], LR1State], Dict[Tuple[LR1State, Symbol], Tuple[str, LR1State | Production]]]`** | Returns the `GOTO` and `ACTION` tables as dictionaries keyed by `(LR1State, Symbol)`. |
| **`get_goto_action_tables_lalr(g: Grammar) -> Tuple[Dict[Tuple[LALRState, Symbol], LALRState], Dict[Tuple[LALRState, Symbol], Tuple[str, LALRState | Production]]]`** | Returns the `GOTO` and `ACTION` tables as dictionaries keyed by `(LALRState, Symbol)`. |
| **`get_propagated_lookaheads(g: Grammar) -> Tuple[Dict[Tuple[LR0State, LR0Item], Set[Symbol]], Dict[Tuple[str, LR0Item, Symbol, str, LR0Item], Set[Symbol]]]`** | Returns detailed lookahead propagation information for debugging. |

!!! note
    `build_parser` and `build_parser_from_attributed` automatically augments the grammar. 

> ### Conflict Exceptions

LR parsers can have conflicts where the parser cannot decide between shifting and reducing (shift‑reduce conflict) or between two different reductions (reduce‑reduce conflict). The parser builder detects these conflicts and raises specific exceptions that include detailed information for debugging.

| **Exception** | **Description** |
| :---: | :---: |
| **`SLRShiftReduceConflictException`** | Raised when a state has both a `SHIFT` and a `REDUCE` action. Includes the state, symbol, the next state (for shift), and the production (for reduce). |
| **`SLRReduceReduceConflictException`** | Raised when a state has two different `REDUCE` actions. Includes the state, symbol, and the two conflicting productions. |
| **`LR1ShiftReduceConflictException`** | Raised during LR(1) construction when a state has both a `SHIFT` and a `REDUCE` action for the same lookahead symbol. Includes the state, symbol, the next state (for shift), and the production (for reduce). |
| **`LR1ReduceReduceConflictException`** | Raised during LR(1) construction when a state has two different `REDUCE` actions for the same lookahead symbol. Includes the state, symbol, and the two conflicting productions. |
| **`LALRShiftReduceConflictException`** | Raised when a state has both a SHIFT and a REDUCE action for the same lookahead symbol. Includes the state, symbol, the next state (for shift), and the production (for reduce). |
| **`LALRReduceReduceConflictException`** | Raised when a state has two different REDUCE actions for the same lookahead symbol. Includes the state, symbol, and the two conflicting productions. |

All conflict exceptions inherit from a common base class (e.g., `SLRParserBuildingConflictException`, `LR1ParserBuildingConflictException`, `LALRParserBuildingConflictException`) and include the state, symbol, and the conflicting actions (next state or production). This allows you to inspect the conflict and resolve it by modifying the grammar (e.g., by changing precedence, restructuring productions, or adding disambiguation rules).

> ### Integration with Attributed Grammars

The parser's ability to build ASTs comes from its integration with attributed grammars. The `ParserBuilder.build_parser_from_attributed` method attaches a reductor to each production in the [`AttributedGrammar`](../grammar/grammar.md#attributedgrammar-grammar-with-reductors). When the parser performs a reduce action, it looks up the reductor for that production and invokes it with an [`ASTListView`](../common/common.md#astlistview-a-lightweight-view-for-reducers) containing the children AST nodes.

The `ASTListView` is a lightweight, immutable view over the AST stack. It provides:

 - Indexed access to children (0‑based).

 - Length (number of children).

 - It is implemented as a view over the internal stack, so it does not copy any data, making it extremely efficient.

 > ### Semantic Error Collection via `ErrorAST`

A critical feature of the parsing runtime is its unified handling of **semantic errors** during reductions. Reductors are not limited to constructing valid ASTs; they can also detect semantic violations (such as type mismatches) by returning an [`ErrorAST`](../common/common.md#errorast-handling-semantic-errors-during-syntactic-analysis) object (an AST subclass with the `_is_error` flag set to `True` and an `_errors` attribute containing a **set of [`SemanticError`](../analysis/analysis.md#concrete-error-classes) instances**). This allows collecting multiple semantic errors from a single reduction and aggregating them without interrupting the parsing process.

This design provides several advantages:

 - **Non‑interruptive error handling**: The parser does not raise an exception upon semantic errors. It records the error and continues parsing, enabling the detection of multiple semantic issues in a single pass.

 - **Unified error reporting**: Both syntactic errors (detected by the LR automaton during panic‑mode recovery) and semantic errors (reported by reductors) are stored in the same errors collection. This simplifies the implementation of diagnostics for IDEs, linters, and compilers.

 - **Robust recovery**: Since the parser ignores the error AST for the purpose of stack management (it still pushes it as a valid child for the reduction), the parser state remains consistent and can attempt to shift subsequent tokens, finding more errors.

To leverage this feature, your reductor signature must remain `Callable[[ASTListView], AST]`, but it is free to return an ErrorAST (which is a subtype of `AST`) instead of a regular AST node. For example:

```python
def complex_number_reductor(asts:ASTListView) -> AST:
    token:Token = asts[1]
    img:NumberAST = asts[0]
    _value = complex(0,img._type(img._value))

    if token._text != 'j':
        error = SemanticError(f'Unexpected symbol {token._text}',token._line,token._column)
        return ErrorAST(semantic_error_symbol,img._line,img._column,{error})
    
    return NumberAST(str(_value),np.complex128,img._line,img._column)
```

!!! note "Clarification on ErrorAST Usage"
    Although `ErrorAST` is a concrete class and can be instantiated directly (as shown above), it is also **intended to be subclassed** by users who wish to add additional error‑specific attributes or methods. The example provided here is merely illustrative of the direct usage pattern.

This tight integration between syntactic analysis (shift/reduce) and semantic checks (reductors) makes PyLGEN parsers exceptionally suitable for production-grade compilers and interpreters, where collecting all errors in a single run is a hard requirement.

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
    slr_parser = ParserBuilder.build_parser(G, ParserType.SLR)
    lr1_parser = ParserBuilder.build_parser(G, ParserType.LR1)
    lalr_parser = ParserBuilder.build_parser(G, ParserType.LALR1)
    ```

=== "Cython"

    ```cython
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.parser.parser_builder cimport _build_lalr_parser , _build_slr_parser, _build_lr1_parser
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
    cdef BottomUpParser slr_parser = _build_slr_parser(G, ParserType.SLR)
    cdef BottomUpParser lr1_parser = _build_lr1_parser(G, ParserType.LR1)
    cdef BottomUpParser lalr_parser = _build_lalr_parser(G, ParserType.LALR1)
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

In the next and final module, we will explore the [**analysis**](../analysis/analysis.md) module, which provides the framework for semantic analysis, visitors, and traversal strategies, the tools you need to give meaning to the AST that the parser produces.