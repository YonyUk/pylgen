# Module `common`

## Submodule `common.types`

> ### `Symbol`

Class that represents a grammar symbol.

 - `__init__(str symbol, bint is_terminal = False, bint is_epsilon = False)`
    - Args:
        - `symbol (str)`: the symbol.

        - `is_terminal (bint)`: whether it is a terminal.

        - `is_epsilon (bint)`: whether it is the epsilon symbol. A symbol can only be epsilon if it is a terminal.

    - Raises: `ValueError('A symbol only can be epsilon if its a terminal symbol')`.

#### Properties

 - `_symbol (cdef str)`
 - `_is_terminal (cdef bint)`
 - `_is_epsilon (cdef bint)`
 - `_hash (cdef int)`

> ### `AST`

Abstract Syntax Tree class.

 - `__init__(Symbol symbol, int start_line, int start_column, int end_line, int end_column)`
    - Args:
        - `symbol (Symbol)`: internal symbol of the AST.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.


    - Raises: `ValueError` if positions are invalid.

#### Properties

 - `_symbol (cdef Symbol)`.
 - `_start_line (cdef int)`: line of the start position in source.
 - `_start_column (cdef int)`: column of the start position in source.
 - `_end_line (cdef int)`: line of the end position in source.
 - `_end_column (cdef int)`: column of the end position in source.
 - `_is_error (cdef bint)`: `True` if is an `ErrorAST`, `False` otherwise.

#### Methods

 - `cpdef list[AST] children()`: method to be implemented by subclasses (`raise NotImplementedError`). It must return the children of the current AST (by general consensus, in the same order that must be processed normally).

> ### `Error`

Abstract error class.

 - `__init__(object type_, int start_line, int start_column, int end_line, int end_column, str msg)`
    - Args:
        - `type_ (object)`.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.
        - `msg (str)`.

    - Raises: `TypeError` if `type_` is not a member of `ErrorType` and is not an `str`, `ValueError` if `type_` is not an `ErrorType`, or `ValueError` if positions are invalid.

#### Properties

 - `_start_line (cdef int)`: line of the start position in source.
 - `_start_column (cdef int)`: column of the start position in source.
 - `_end_line (cdef int)`: line of the end position in source.
 - `_end_column (cdef int)`: column of the end position in source.
 - `_type (cdef object)`: The type of the error.
 - `_msg (cdef str)`: The message of the error.
 - `_hash (cdef int)`.

> ### `Error` subclasses

All this classes inherits from `Error` class.

#### `LexicalError`

 - `__init__(str msg, int start_line, int start_column, int end_line, int end_column)`: sets `type_ = ErrorType.LEXICAL`.

#### `SyntaxError`

 - `__init__(str msg, int start_line, int start_column, int end_line, int end_column)`: sets `type_ = ErrorType.SYNTAX`.

#### `SemanticError`

 - `__init__(str msg, int start_line, int start_column, int end_line, int end_column)`: sets `type_ = ErrorType.SEMANTIC`.

#### `RuntimeError`

 - `__init__(list[str] stack_trace, int start_line, int start_column, int end_line, int end_column, str msg)`: sets `type_ = ErrorType.RUNTIME`.

 - **Property**: `_stack_trace (cdef list[str])`.

> ### `ErrorAST`

Error Syntax Tree Class (inherits from `AST`: `ErrorAST(AST)`).

 - `__init__(Symbol symbol, int start_line, int start_column, int end_line, int end_column, set[SemanticError] errors)`
    - Args:
        - `symbol (Symbol)`: internal symbol of the AST.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.
        - `errors (set[SemanticError])`: errors inside the ast.
    
    - Raises: `ValueError` if positions are invalid.
    - Sets `_is_error` internal flag to `True`.

 - **Property**: `_errors (cdef set[SemanticError])`.

> ### `ASTListView`

View over a list of `AST`.

#### Properties
    
 - `_data (cdef list[AST])`
 - `_start (cdef int)`
 - `_end (cdef int)`

#### Methods

 - `cdef inline AST _get(int idx)`:
     - Raises: `IndexError('ASTListView index out of range')` if `idx < 0` or `idx >= _end - _start`.
 
 - `cdef inline int _size()`: returns `self._end - self._start`

!!! warning
    This class is internally managed by the parser, it is not meant to be used directly by the user.

> ### `Token`

Token class (inherits from `AST`: `Token(AST)`).

 - `__init__(str text, object type_, Symbol symbol, int line, int column)`
    - Raises: `ValueError` if `type_` is not a subclass of `TokenType`.
    - Calls `super().__init__(symbol, line, column, line, column + len(text))`.

#### Properties

 - `_text (cdef str)`: The text of the token.
 - `_type (cdef object)`: The type of the token.

#### Methods

 - `cpdef list[AST] children()`: returns `[]`

## Submodule `common.table`

> ### `Table`

Class used to store the transitions of an automata.

 - `__init__()`: initializes `_table = {}`.

#### Properties

 - `_table (cdef dict)`

#### Methods

 - `cpdef dict to_dict()`: returns copy as a plain dict.
 - `cpdef void from_dict(dict data)`: updates `_table` with `data`.