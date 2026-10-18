# Module `lexer`

## Submodule `lexer.base_lexer`

> ### `LexerNotInitializedException`

Exception raised when an attempt is made to obtain the internal `DFA` without initializing the lexer first. Inherits from `Exception` (`LexerNotInitializedException(Exception)`).

> ### `LexerNotTokensProvidedException`

Exception raised when an attemp is made to initialize the lexer without any token automata provided. Inherits from `Exception` (`LexerNotTokensProvidedException(Exception)`).

> ### `BaseLexer`

Base class for a lexer.

 - `__init__(get_symbol_function, ignore_pattern,check_annotation = True)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: mapping function that maps a tuple `(Any,str)` to a `Symbol`. The mapping function must be annotated with the specific signature `Callable[[Any, str], Symbol]` if `check_annotation` is `True`, where the first argument annotation must be a subclass of `TokenType`. If `check_annotation` is `False`, the annotation checking is not performed.
        - `ignore_pattern (DFA)`: the `DFA` used to skip text patterns.
    
    - Raises: `ValueError` if the signature of `get_symbol_function` is invalid.

!!! warning
    This class is not meant to be used directly.
    
#### Properties

 - `_text (cdef str)`: the text to tokenize.

 - `_text_readed (cdef str)`: the text currently readed.

 - `_text_position_pointer (cdef int)`: the position pointer to the character to read in the tokenization process.

 - `_line (cdef int)`: current line in the text.

 - `_column (cdef int)`: current column in the text.

 - `_fault_state (cdef State)`: used internally during the tokenization process.

 - `_automatons (cdef set[Automaton])`: the set of automatons used to build the global `DFA` for tokenization.

 - `_initialized (cdef bint)`: `True` if the lexer has been initialized.

 - `_priorites (cdef dict[int,object])`: used to select the type of token to return when a conflictive state is reached.

 - `_priorities_sorted (cdef list[int])`: used to select the type of token to return when a conflictive state is reached.

 - `_dfa_transition_function (cdef dict[str,str])`: used to accelerate the tokenization process.

 - `_dfa (cdef DFA)`: the internal `DFA` used for tokenization.

 - `_get_symbol_function (cdef object)`: the mapping function.

 - `_types_by_state (cdef dict[str,set[object]])`: used internally to assign the type to each token.

 - `_current_token (cdef Token)`: the current token.

 - `_ignore (cdef DFA)`: the `DFA` used to skip tokens.

 - `_enum_type (cdef object)`: the enumeration of types for the tokens.

#### Methods

 - `cdef Token _get_token(text,line,column)`: used to build `_current_token`.
    - Args:
        - `text (str)`: the text of the token to build.
        - `line (int)`: the current line.
        - `column (int)`: the current column.

 - `cdef void _add_token(priority,type_,automaton)`: adds a new token automaton.
    - Args:
        - `priority (int)`
        - `type_ (object)`: the type of the new token.
        - `automaton (Automaton)`: the automaton to recognize the token.

 - `cdef Symbol _get_symbol(type_,text)`: the internal mapping function.
    - Args:
        - `type_ (Any)`: the type of token.
        - `text (str)`: the text of the token.
    
    - Raise: `ValueError('type_ must be a subclass of TokenType')`

 - `cdef set[object] _get_dfa_state_values(state)`: used to get the internal `DFA` states values.
    - Args:
        - `state (State)`: gets the token types of the given state.

 - `cdef bint _move_next()`: iterates until a new token is readed.

 - `cdef Token _current()`: gets the current token readed.

 - `cdef bint _is_fault_state(state)`: returns `True` if the given state is the fault state of the internal `DFA` used during the tokenization.
    - Args:
        - `state (State)`

 - `cpdef void initialize()`: initializes the lexer.
    - Raises: `LexerNotTokensProvidedException` if there are no automata provided for tokens.

 - `cpdef void load_text(text)`: prepares the lexer for the tokenization.

## Submodule `lexer.lexer`

> ### `Lexer`

Subclass of `BaseLexer`.

 - `__init__(get_symbol_function, ignore_pattern)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: analogous to `BaseLexer.__init__`.
        - `ignore_pattern (str)`: regex of the tokens to skip in the tokenization.

#### Properties

 - `_rules (cdef dict[object,set[LexicalRule]])`: lexical rules to apply during the tokenization.

 - `_errors (cdef set[LexicalError])`: set of lexical errors detected during the tokenization.

 - `_eof (cdef Token)`: the `EOF` token.

#### Methods

 - `cpdef void clear_errors()`: clears all the lexical errors detected.

 - `cpdef void set_eof_token(symbol, type_)`: sets the `EOF` token to be emmited at the end of the tokenization.
    - Args:
        - `symbol (str)`: the text of the symbol for the `EOF` token. The symbol of `EOF` token is always a terminal.
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
    
    - Raises: `ValueError` if `type_` does not belong to the enum of the annotation for the first argument of `get_symbol_function`.

 - `cpdef void add_token_regex(priority, type_, re)`: compiles `re`, assigns `type_` to accepting states of the compilation result of `re` and registers the token.
    - Args:
        - `priority (int)`
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
        - `re (str)`: the regex for the token.

 - `cpdef void add_rule(type_, rule)`: adds a `LexicalRule` to the set associated with `type_`.
    - Args:
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
        - `rule (LexicalRule)`: the rule to be applied during tokenization.

> ### `IdentedLexer`

Subclass of `Lexer` specialized on languages with identation.

 - `__init__(get_symbol_function, ignore_pattern)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: analogous to `BaseLexer.__init__`.
        - `ignore_pattern (str)`: regex of the tokens to skip in the tokenization.

#### Properties

 - `_ident_counter (cdef int)`: used to decide when to emit a `INDENT` or a `DEDENT` token.

 - `_last_ident_value (cdef int)`: used to decide when to emit a `INDENT` or a `DEDENT` token.

 - `_ident_type (cdef object)`: the enumeration value associated to the `INDENT` or `DEDENT` token (must be a member of a subclass of `TokenType`).

 - `_indent_symbol (cdef Symbol)`: associated symbol for the `INDENT` token.

 - `_dedent_symbol (cdef Symbol)`: associated symbol for the `DEDENT` token.

 - `_sanitaze_function (cdef object)`: function used for sanitaze the text before the tokenization, if provided, it's automatically called during `load_text(text)`.

#### Methods

- `cpdef void set_ident(ident_type)`: sets the set of tokens associated to identation (`'    ', '\t'`, etc.) 
    - Args:
        - `ident_type (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
    
    - Raises: `ValueError` if not in the enum.

 - `cpdef void set_indent_symbol(symbol)`: sets the symbol for the `INDENT` token.
    - Args:
        - `symbol (Symbol)`

 - `cpdef void set_dedent_symbol(symbol)`: sets the symbol for the `DEDENT` token.
    - Args:
        - `symbol (Symbol)`

 - `cpdef void set_text_sanitize_function(sanitaze_function)`: stores the sanitization function, if provided, is automatically called during `IdentedLexer.load_text(text)`.
    - Args:
        - `sanitaze_function (Callable[[str],str])`.