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

 - `_id (cdef str)`: the id of the item (`f'{head} -> {left} ◦ {right}'`)

 - `_head (cdef Symbol)`

 - `_left (cdef list[Symbol])`: copy of the symbols before the dot.

 - `_right (cdef list[Symbol])`: copy of the symbols before the dot.

 - `_hash (cdef int)`: precomputed hash.

> ### `LR0State`

Class that represents an **LR(0) state**.

 - `__init__(items, index = 0)`:
    - Args:
        - `items (Set[LR0Item])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `_id (cdef str)`

 - `index (cdef int)`

 - `_items (cdef set[LR0Item])`

 - `_hash (cdef int)`

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

 - `_id (cdef str)`: Differences from `LR0Item` (`f'{self._head} -> {left} ◦ {right} ({lookahead})'`)

 - `_lookahead (cdef Symbol)`: the lookahead symbol.

> ### `LR1State`

Class that represents an **LR(1) state**.

 - `__init__(items, index = 0)`
    - Args:
        - `items (Set[LR1Item])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `_id (cdef str)`
 - `_index (cdef int)`
 - `_items (cdef set[LR1Item])`
 - `_hash (cdef int)`

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

 - `_id (cdef str)`: Differences from `LR0Item` (`f'{self._head} -> {left} ◦ {right} {lookaheads}'`)

 - `_lookaheads (cdef set[Symbol])`: the set of lookahead symbols.

> ### `LALRState`

Class that represents an **LR(1) state**.

 - `__init__(items, index = 0)`
    - Args:
        - `items (Set[LALRItem])`: items of the state.
        - `index (int)`: used to produce human-readable string representations like `I0`, `I2`, etc.

#### Properties

 - `_id (cdef str)`
 - `_index (cdef int)`
 - `_items (cdef set[LALRItem])`
 - `_hash (cdef int)`

## Submodule `parser.parser`

> ### `ParsingException`

Exception raised when an attemp is made to obtain the parse tree after when errors where found during the parsing process. Inherits from `Exception` (`ParsingException(Exception)`).

> ### `ParseTreeNode`

Class that represents a node on the resulting parse tree after a token's stream has been parsed.

 - `__init__(symbol, start_line, start_column, end_line, end_column, children=[])`
    - Args:
         - `symbol (Symbol)`: symbol of this node on the parse tree.
         - `start_line (int)`: start line in the source.
         - `start_column (int)`: start column in the source.
         - `end_line (int)`: end line in the source.
         - `end_column (int)`: end column in the source.
         - `children (list[ParseTreeNode])`: children of this node in the parse tree.

#### Properties

- `_symbol (cdef Symbol)`: symbol of this node on the parse tree.
- `_start_line (cdef int)`: start line in the source.
- `_start_column (cdef int)`: start column in the source.
- `_end_line (cdef int)`: end line in the source.
- `_end_column (cdef int)`: end column in the source.
- `_children (cdef list[ParseTreeNode])`: children of this node in the parse tree.

> ### `Parser`

Base class for a parser.

 - `__init__()`
    - Raises: `ValueError('Can not instance this class')`.

#### Properties

 - `_ast (cdef AST)`: the resulting ast when parsing ends succesfully.

 - `_parsed (cdef bint)`: `True` when parsing ends succesfully.

 - `_draw_parse_tree (cdef bint)`: when `True`, the parser builds the parse tree during the parsing.

 - `_parse_tree (cdef ParseTreeNode)`: the resulting parse tree when parsing ends succesfully with `_draw_parse_tree` setted to `True`.

 - `_parse_tree_nodes (cdef list[ParseTreeNode])`: used internally to build the parse tree.

 - `_errors (cdef set[Error])`: the errors collected during the parsing.

 - `_syntax_error (cdef bint)`: `True` if any syntax error.

#### Methods

 - `cdef void _try_parse(token)`: try to parse the given token. Not implemented raises `NotImplementedError`.
    - Args:
        - `token (Token)`.
    
 - `cpdef void reset()`: resets the parser (not implemented, raises `NotImplementedError`).

 - `cpdef void set_draw_parse_tree_flag(flag)`: if `flag` is `True`, tells the parser to build the parse tree.
    - Args:
        - `flag (bool)`

> ### `BottomUpParser`

Class for a classic lr parser. Inherits from `Parser` (`BottomUpParser(Parser)`).

 - `__init__(start_state, goto_table, action_table)`
    - Args:
        - `start_state (str)`: initial state id, e.g. `"I0"`.
        - `goto_table (Dict[Tuple[str, Symbol], str])`: the `GOTO` table.
        - `action_table (Dict[Tuple[str, Symbol], Tuple[str, str | Production]])`: the `ACTION` table.

#### Properties

 - `_reductor_by_production (cdef dict[int,object])`: mapping of the productions to the corresponding reductor.

 - `_goto_table (cdef dict[tuple[str,Symbol],str])`: `GOTO` table.

 - `_action_table (cdef dict[tuple[str,Symbol],tuple[str,object]])`: `ACTION` table.

 - `_goto_table_optimized (cdef dict[long long,int])`: optimized version of the `GOTO` table.

 - `_action_table_optimized (cdef dict[long long,tuple[str,object]])`: optimized version of the `GOTO` table.

 - `_stack (cdef list[Symbol])`: internal symbols stack for the parsing.

 - `_stack_ast (cdef list[AST])`: internal asts stack for the parsing.

 - `_stack_states (cdef list[int])`: iternal states stack for the parsing.

 - `_start_state (cdef str)`: start state for reseting the parser.

 - `_current_syncronization_set (cdef set[Symbol])`: used internally for the **panic-mode** error recovery strategy.

 - `_panic_mode (cdef bint)`: `True` when the parser is recovering from a syntax error.

 - `_view (cdef ASTListView)`: view passed to reductors.

 - `_stack_top (cdef int)`: updated internally to keep updated `_stack`.

 - `_stack_len (cdef int)`: updated internally to keep updated `_stack`.

 - `_stack_ast_top (cdef int)`: updated internally to keep updated `_stack_ast`.

 - `_stack_ast_len (cdef int)`: updated internally to keep updated `_stack_ast`.

 - `_stack_states_top (cdef int)`: updated internally to keep updated `_stack_states`.

 - `_stack_states_len (cdef int)`: updated internally to keep updated `_stack_states`.

#### Methods

 - `cdef void _start_recovery_mode(symbol, start_line, start_column, end_line, end_column)`: starts the error recovery process.
    - Args:
        - `symbol (Symbol)`: symbol that triggered the error.
        - `start_line (int)`: line where the error starts in source.
        - `start_column (int)`: column where the error starts in source.
        - `end_line (int)`: line where the error ends in source.
        - `end_column (int)`: column where the error ends in source.

 - `cdef void _end_recovery_mode(symbol)`: ends the error recovery process.
    - Args:
        - `symbol (Symbol)`: symbol with which the process stop.

 - `cdef void _set_reductor(production,reductor)`: sets the corresponding reductor to the given production.

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
        - `_state (cdef LR0State)`: conflictive state.
        - `_symbol (cdef Symbol)`: conflictive symbol.

 - `LR1ParserBuildingConflictException`
    - `__init__(state, symbol)`
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
    
    - Properties:
        - `_state (cdef LR1State)`: conflictive state.
        - `_symbol (cdef Symbol)`: conflictive symbol.

 - `LALRParserBuildingConflictException`
    - `__init__(state, symbol)`
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
    
    - Properties:
        - `_state (cdef LALRState)`: conflictive state.
        - `_symbol (cdef Symbol)`: conflictive symbol.

 - `SLRShiftReduceConflictException`: Inherits from `SLRParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LR0State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LR0State)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `_state (cdef LR0State)`: possible `SHIFT` state.
        - `_production (cdef Production)`: posible `REDUCE` production.

 - `LR1ShiftReduceConflictException`: Inherits from `LR1ParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LR1State)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `_state (cdef LR1State)`: possible `SHIFT` state.
        - `_production (cdef Production)`: posible `REDUCE` production.

 - `LALRShiftReduceConflictException`: Inherits from `LALRParserBuildingConflictException`.
    - `__init__(state, symbol, next_state, production)`:
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.    
            - `state (LALRState)`: possible `SHIFT` state.
            - `production (Production)`: posible `REDUCE` production.
    
    - Properties:
        - `_state (cdef LALRState)`: possible `SHIFT` state.
        - `_production (cdef Production)`: posible `REDUCE` production.

 - `SLRReduceReduceConflictException`: Inherits from `SLRParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LR0State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `_old (cdef Production)`: conflictive production.
        - `_new (cdef Production)`: conflictive production.

 - `LR1ReduceReduceConflictException`: Inherits from `LR1ParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LR1State)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `_old (cdef Production)`: conflictive production.
        - `_new (cdef Production)`: conflictive production.

 - `LALRReduceReduceConflictException`: Inherits from `LALRParserBuildingConflictException`.
    - `__init__(state, symbol, old, new_)`
        - Args:
            - `state (LALRState)`: conflictive state.
            - `symbol (Symbol)`: conflictive symbol.
            - `old (Production)`: conflictive production.
            - `new_ (Production)`: conflictive production.
    
    - Properties:
        - `_old (cdef Production)`: conflictive production.
        - `_new (cdef Production)`: conflictive production.

> ### Module functions.

 - **`CLOSURE`** implementation:
    - `cdef set[LR0Item] _closure_lr0(items, g)`
        - Args:
            - `items (set[LR0Item])`
            - `g (Grammar)`

    - `cdef set[LR1Item] _closure_lr1(items, g)`
        - Args:
            - `items (set[LR1Item])`
            - `g (Grammar)`

    - `cdef set[LALRItem] _closure_lalr(items, g)`
        - Args:
            - `items (set[LALRItem])`
            - `g (Grammar)`

 - **`GOTO`** implementation:

    - `cdef set[LR0Item] _goto_lr0(items, x, g)`
        - Args:
            - `items (set[LR0Item])`
            - `x (Symbol)`
            - `g (Grammar)`

    - `cdef set[LR1Item] _goto_lr1(items, x, g)`
        - Args:
            - `items (set[LR1Item])`
            - `x (Symbol)`
            - `g (Grammar)`

    - `cdef set[LALRItem] _goto_lalr(items, x, g)`
        - Args:
            - `items (set[LALRItem])`
            - `x (Symbol)`
            - `g (Grammar)`

 - `cdef set[LR0State] get_canonical_lr0_states(g)`: returns the set of the canonical LR(0) states.
    - Args:
        - `g (Grammar)`

 - `cdef set[LR1State] get_canonical_lr1_states(g)`: returns the set of the canonical LR(1) states.
    - Args:
        - `g (Grammar)`

 - `cdef tuple[set[LALRState],dict[tuple[LR0State,LR0Item],set[Symbol]],dict[tuple[str,LR0Item,Symbol,str,LR0Item],set[Symbol]]] _get_canonical_lalr_states(g,keep_edge_propagation_info=False)`: returns the set of the canonical LALR(1) states and optionally, a record of the symbols propagated for the propagation edges (used in the `visual` module for visual debugging).
    - Args:
        - `g (Grammar)`
        - `keep_edge_propagation_info (bint)`: if `True`, the info is saved and returned.

!!! note
    `_get_canonical_lr0_states`, `_get_canonical_lr1_states` and `_get_canonical_lalr_states`, already adds the production `S -> S'` to the grammar, so it is unnecessary to do this manually.

 - `cdef set[LR0Item] _get_kernel_items_lr0(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LR0State)`
        - `g (Grammar)`

 - `cdef set[LR1Item] _get_kernel_items_lr1(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LR1State)`
        - `g (Grammar)`

 - `cdef set[LALRItem] _get_kernel_items_lalr(state, g)`: returns the set of the kernel items of the given state.
    - Args:
        - `state (LALRState)`
        - `g (Grammar)`

 - `cdef tuple[dict[LR0State,dict[tuple[LR0Item,Symbol],tuple[LR0State,LR0Item]]],set[LR0State]] _build_lookaheads_propagation_edges(g)`: builds the propagation edges for a LALR(1) parser building, returns a tuple `(edges,lr0_states)`.
    - Args:
        - `g (Grammar)`

 - `cdef tuple[dict[tuple[LALRState,Symbol],LALRState],dict[tuple[LALRState,Symbol],tuple]] _get_goto_action_tables_lalr(g)`, `cdef tuple[dict[tuple[LR0State,Symbol],LR0State],dict[tuple[LR0State,Symbol],tuple]] _get_goto_action_tables_slr(g)`, `cdef tuple[dict[tuple[LR1State,Symbol],LR1State],dict[tuple[LR1State,Symbol],tuple]] _get_goto_action_tables_lr1(g)`: builds the `GOTO` / `ACTION` tables.
    - Args:
        `g (Grammar)`

 - `cdef dict[tuple[str,Symbol],str] _plain_goto_table_lalr(table)`: plains a LALR(1) `GOTO` table.
    - Args:
        - `table (dict[tuple[LALRState,Symbol],LALRState])`

 - `cdef dict[tuple[str,Symbol],str] _plain_goto_table_slr(table)`: plains a SLR `GOTO` table.
    - Args:
        - `table (dict[tuple[LR0State,Symbol],LR0State])`

 - `cdef dict[tuple[str,Symbol],str] _plain_goto_table_lr1(table)`: plains a LR(1) `GOTO` table.
    - Args:
        - `table (dict[tuple[LR1State,Symbol],LR1State])`

 - `cdef dict[tuple[str,Symbol],tuple[str,object]] _plain_action_table_lalr(table)`: plains a LALR(1) `ACTION` table.
    - Args:
        - `table (dict[tuple[LALRState,Symbol],tuple])`

 - `cdef dict[tuple[str,Symbol],tuple[str,object]] _plain_action_table_slr(table)`: plains a SLR `ACTION` table.
    - Args:
        - `table (dict[tuple[LR0State,Symbol],tuple])`

 - `cdef dict[tuple[str,Symbol],tuple[str,object]] _plain_action_table_lr1(table)`: plains a LR(1) `ACTION` table.
    - Args:
        - `table (dict[tuple[LR1State,Symbol],tuple])`

 - `cdef BottomUpParser _build_lalr_parser(g)`: builds a LALR(1) parser.
    - Args:
        - `g (Grammar)`

 - `cdef BottomUpParser _build_slr_parser(g)`: builds a SLR parser.
    - Args:
        - `g (Grammar)`

 - `cdef BottomUpParser _build_lr1_parser(g)`: builds a LR(1) parser.
    - Args:
        - `g (Grammar)`

 - `cdef BottomUpParser _build_lalr_parser_from_attributed(g)`: builds a LALR(1) parser from an attributed grammar and sets the corresponding reductors.
    - Args:
        - `g (AttributedGrammar)`

 - `cdef BottomUpParser _build_slr_parser_from_attributed(g)`: builds a SLR parser from an attributed grammar and sets the corresponding reductors.
    - Args:
        - `g (AttributedGrammar)`

 - `cdef BottomUpParser _build_lr1_parser_from_attributed(g)`: builds a LR(1) parser from an attributed grammar and sets the corresponding reductors.
    - Args:
        - `g (AttributedGrammar)`

## Submodule `parser.parser_type`

> ### `ParserType`

Enumeration with the parser types. Inherits from `StrEnum` (`ParserType(StrEnum)`).

 - `LL1 = 'LL1'`: **currently not supported**.

 - `SLR = 'SLR'`

 - `LR1 = 'LR1'`

 - `LALR1 = 'LALR1'`