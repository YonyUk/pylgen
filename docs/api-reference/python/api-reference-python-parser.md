# Module `parser`

## Submodule `parser.bottom_up_parser_actions`

> ### `BottomUpParserAction`

Enumeration with the possible actions of an LR parser. Inherits from `StrEnum` (`BottomUpParserAction(StrEnum)`).

 - `ACCEPT = 'ACCEPT'`

 - `SHIFT = 'SHIFT'`

 - `REDUCE = 'REDUCE'`

## Submodule `parser.lr0_parser`

> ### `LR0Item`

Class that represents an **LR(0) item**.

 - `__init__(head, left, right)`
    - Args:
        - `head (Symbol)`: non-terminal of the production from which this item comes.
        - `left (Sequence[Symbol])`: the symbols before the dot.
        - `right (Sequence[Symbol])`: the symbols after the dot.

#### Properties 

 - `id (str)`: the id of the item (`f'{head} -> {left} ◦ {right}'`)

 - `head (Symbol)`

 - `left (Sequence[Symbol])`: copy of the symbols before the dot.

 - `right (Sequence[Symbol])`: copy of the symbols before the dot.

#### Methods

 - `__str__`: returns `id`.

 - `__repr__`: returns `id`.

 - `__eq__`: equality based on `head`, `left` and `right` properties.

 - `__hash__`: precomputed hash.


> ### `LR0State`

Class that represents an **LR(0) state**.

 - `__init__(items, index = 0)`:
    - Args:
        - `items (Set[LR0Item])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `id (str)`
 - `index (int)`
 - `items (Set[LR0Item])`

#### Methods

 - `__eq__`: by id.
 - `__hash__`: precomputed hash.

## Submodule `parser.lr1_parser`

> ### `LR1Item`

Class that represents an **LR(1) item**. Inherits from `LR0Item` (`LR1Item(LR0Item)`)

 - `__init__(head, left, right, lookahead)`
    - Args:
        - `head (Symbol)`: non-terminal of the production from which this item comes.
        - `left (Sequence[Symbol])`: the symbols before the dot.
        - `right (Sequence[Symbol])`: the symbols after the dot.
        - `lookahead (Symbol)`: the lookahead symbol.

#### Properties

 - `id (str)`: Differences from `LR0Item` (`f'{self._head} -> {left} ◦ {right} ({lookahead})'`)

 - `lookahead (Symbol)`: the lookahead symbol.

#### Methods

 - `__eq__`: Differences from `LR0Item`, also compares `lookahead`.

> ### `LR1State`

Class that represents an **LR(1) state**.

 - `__init__(items, index = 0)`
    - Args:
        - `items (Set[LR1Item])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `id (str)`
 - `index (int)`
 - `items (Set[LR1Item])`

#### Methods

 - `__eq__`: by id.
 - `__hash__`: precomputed hash.

## Submodule `parser.lalr_parser`

> ### `LALRItem`

Class that represents an **LALR(1) item**. Inherits from `LR0Item` (`LALRItem(LR0Item)`).

 - `__init__(head, left, right, lookaheads = set())`
    - Args:
        - `head (Symbol)`: non-terminal of the production from which this item comes.
        - `left (Sequence[Symbol])`: the symbols before the dot.
        - `right (Sequence[Symbol])`: the symbols after the dot.
        - `lookaheads (Set[Symbol])`: the set of lookahead symbols.

#### Properties

 - `id (str)`: Differences from `LR0Item` (`f'{self._head} -> {left} ◦ {right} {lookaheads}'`)

 - `lookaheads (Set[Symbol])`: the set of lookahead symbols.

#### Methods

 - `__eq__`: also compares `lookaheads`.

> ### `LALRState`

Class that represents an **LR(1) state**.

 - `__init__(items, index = 0)`
    - Args:
        - `items (Set[LALRItem])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `id (str)`
 - `index (int)`
 - `items (Set[LALRItem])`

#### Methods

 - `__eq__`: by id.
 - `__hash__`: precomputed hash.

## Submodule `parser.parser`

> ### `ParsingException`

Exception raised when an attemp is made to obtain the parse tree after when errors where found during the parsing process. Inherits from `Exception` (`ParsingException(Exception)`).

> ### `ParseTreeNode`

Class that represents a node on the resulting parse tree after a token's stream has been parsed.

 - `__init__(symbol, start_line, start_column, end_line, end_column, childrens=[])`
    - Args:
         - `symbol (Symbol)`: symbol of this node on the parse tree.
         - `start_line (int)`: start line in the source.
         - `start_column (int)`: start column in the source.
         - `end_line (int)`: end line in the source.
         - `end_column (int)`: end column in the source.
         - `children (List[ParseTreeNode])`: children of this node in the parse tree.

#### Properties

 - `symbol (Symbol)`: symbol of this node on the parse tree.

 - `start_position (Tuple[int,int])`: tuple `(start_line, start_column)`, the start position in the source.

 - `end_position (Tuple[int,int])`: tuple `(end_line,end_column)`, the end position in the source.

 - `childrens (List[ParseTreeNode])`: children of this node in the parse tree.

> ### `Parser`

Base class for a parser.

 - `__init__()`
    - Raises: `ValueError('Can not instance this class')`.

#### Properties

 - `parse_tree (ParseTreeNode)`: root of the parse tree, if succesfully builded
    - Raises: `ParsingException` if any syntax error.

 - `syntax_errors (bool)`: `True` if any syntax error.

 - `errors List[Error]`: all errors detected.

#### Methods

 - `parse(tokens)`: returns the root of the resulting ast if succesfully parsed, otherwise `None`.
    - Args:
        - `tokens (Iterable[Token])`: token's stream.

 - `reset()`: resets the parser (not implemented, raises `NotImplementedError`).

 - `set_draw_parse_tree_flag(flag)`: if `flag` is `True`, tells the parser to build the parse tree.
    - Args:
        - `flag (bool)`

> ### `BottomUpParser`

Class for a classic lr parser. Inherits from `Parser` (`BottomUpParser(Parser)`).

 - `__init__(start_state, goto_table, action_table)`
    - Args:
        - `start_state (str)`: initial state id, e.g. `"I0"`.
        - `goto_table (Dict[Tuple[str, Symbol], str])`: the `GOTO` table.
        - `action_table (Dict[Tuple[str, Symbol], Tuple[str, str | Production]])`: the `ACTION` table.

#### Methods

 - `__setitem__(production, reductor)`: sets the reductor for the given production
    - Raises: `ValueError` if the reductor's signature is not `(ASTListView) -> AST`.

## Submodule `parser.parser_builder`

> ### Exceptions

Exceptions raised when the parser building fails.

 - `ParserBuildingConflictException`

 - `SLRParserBuildingConflictException`
    - `__init__(state, symbol)`
        - Args:
            - `state (LR0State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
    
    - Properties:
        - `state (LR0State)`: conflictive state.
        - `symbol (Symbol)`: conflictive symbol.

 - `LR1ParserBuildingConflictException`
    - `__init__(state, symbol)`
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
    
    - Properties:
        - `state (LR1State)`: conflictive state.
        - `symbol (Symbol)`: conflictive symbol.

 - `LALRParserBuildingConflictException`
    - `__init__(state, symbol)`
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
    
    - Properties:
        - `state (LALRState)`: conflictive state.
        - `symbol (Symbol)`: conflictive symbol.

 - `SLRShiftReduceConflictException`: Inherits from `SLRParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LR0State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LR0State)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `state (LR0State)`: possible `SHIFT` state.
        - `production (Production)`: posible `REDUCE` production.

 - `LR1ShiftReduceConflictException`: Inherits from `LR1ParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LR1State)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `state (LR1State)`: possible `SHIFT` state.
        - `production (Production)`: posible `REDUCE` production.

 - `LALRShiftReduceConflictException`: Inherits from `LALRParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LALRState)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `state (LALRState)`: possible `SHIFT` state.
        - `production (Production)`: posible `REDUCE` production.

 - `SLRReduceReduceConflictException`: Inherits from `SLRParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LR0State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `old (Production)`: conflictive production.
        - `new_ (Production)`: conflictive production.

 - `LR1ReduceReduceConflictException`: Inherits from `LR1ParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `old (Production)`: conflictive production.
        - `new_ (Production)`: conflictive production.

 - `LALRReduceReduceConflictException`: Inherits from `LALRParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `old (Production)`: conflictive production.
        - `new_ (Production)`: conflictive production.

> ### `ParserBuilder`

Static class that contains all the methods necessary for parser building.

 - `clear_cache()`: clears the internal cache.

 - **`CLOSURE`** implementation:
    - `closure_lr0(items, g) -> Set[LR0Item]`
        - Args:
            - `items (Set[LR0Item])`
            - `g (Grammar)`

    - `closure_lr1(items, g) -> Set[LR1Item]`
        - Args:
            - `items (Set[LR1Item])`
            - `g (Grammar)`

    - `closure_lalr(items, g) -> Set[LALRItem]`
        - Args:
            - `items (Set[LALRItem])`
            - `g (Grammar)`

 - **`GOTO`** implementation:

    - `goto_lr0(items, x, g) -> Set[LR0Item]`
        - Args:
            - `items (Set[LR0Item])`
            - `x (Symbol)`
            - `g (Grammar)`

    - `goto_lr1(items, x, g) -> Set[LR1Item]`
        - Args:
            - `items (Set[LR1Item])`
            - `x (Symbol)`
            - `g (Grammar)`

    - `goto_lalr(items, x, g) -> Set[LALRItem]`
        - Args:
            - `items (Set[LALRItem])`
            - `x (Symbol)`
            - `g (Grammar)`

 - `get_canonical_lr0_states(g)`: returns the set of the canonical LR(0) states.
    - Args:
        - `g (Grammar)`

 - `get_canonical_lr1_states(g)`: returns the set of the canonical LR(1) states.
    - Args:
        - `g (Grammar)`

 - `get_canonical_lalr_states(g)`: returns the set of the canonical LALR(1) states.
    - Args:
        - `g (Grammar)`

!!! note
    `get_canonical_lr0_states`, `get_canonical_lr1_states` and `get_canonical_lalr_states`, already adds the production `S -> S'` to the grammar, so it is unnecessary to do this manually.

 - `get_kernel_items_lr0(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LR0State)`
        - `g (Grammar)`

 - `get_kernel_items_lr1(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LR1State)`
        - `g (Grammar)`

 - `get_kernel_items_lalr(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LALRState)`
        - `g (Grammar)`

 - `build_lookaheads_propagation_edges(g)`: builds the propagation edges for a LALR(1) parser building, returns a tuple `(edges,lr0_states)`.
    - Args:
        - `g (Grammar)`

 - `get_goto_action_tables_slr(g)`, `get_goto_action_tables_lr1(g)`, `get_goto_action_tables_lalr(g)`: builds the `GOTO` / `ACTION` tables.
    - Args:
        `g (Grammar)`

 - `build_parser(g, type_)`: builds a parser.
    - Args:
        - `g (Grammar)`
        - `type_ (ParserType)`

 - `build_parser_from_attributed(g, type_)`: builds a parser from an attributed grammar.
    - Args:
        - `g (AttributedGrammar)`
        - `type_ (ParserType)`

 - `get_propagated_lookaheads(g)`: returns the propagation edges for LALR(1) parser building after and before they are filled, in a tuple `(final_lookaheads, propagated_lookaheads)`. Used internally for the module `visual` for visual debuging.
    - Args:
        - `g (Grammar)`

## Submodule `parser.parser_type`

> ### `ParserType`

Enumeration with the parser types. Inherits from `StrEnum` (`ParserType(StrEnum)`).

 - `LL1 = 'LL1'`: **currently not supported**.

 - `SLR = 'SLR'`

 - `LR1 = 'LR1'`

 - `LALR1 = 'LALR1'`