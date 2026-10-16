# Module `common`

## Submodule `common.enums`

> ### `TokenTypeMeta(EnumMeta)`

Metaclass for `TokenType`. In its `__new__`, it injects `INVALID_TOKEN` into subclasses (except `TokenType` itself).

> ### `TokenType(StrEnum, metaclass=TokenTypeMeta)`

Base enumeration for token types. Subclasses automatically receive an `INVALID_TOKEN` member.

> ### `ErrorType(StrEnum)`

Compiler error types.

 - `LEXICAL = 'LEXICAL'`

 - `SYNTAX = 'SYNTAX'`
 
 - `SEMANTIC = 'SEMANTIC'`
 
 - `RUNTIME = 'RUNTIME'`

## Submodule `common.types`

> ### `Symbol`

Class that represents a grammar symbol.

 - `__init__(symbol: str, is_terminal: bool = False, is_epsilon: bool = False)`
    - Args:
        - `symbol (str)`: the symbol.

        - `is_terminal (bool)`: whether it is a terminal.

        - `is_epsilon (bool)`: whether it is the epsilon symbol. A symbol can only be epsilon if it is a terminal.

    - Raises: `ValueError('A symbol only can be epsilon if its a terminal symbol')`.

#### Properties

 - `symbol (str)`
 - `is_terminal (bool)`
 - `is_epsilon (bool)`

#### Methods

 - `__str__`: returns the symbol.
 - `__repr__`: returns the symbol.
 - `__eq__`: equality by `symbol`, `is_terminal` and `is_epsilon` properties.
 - `__hash__`: precomputed hash using **SHA-256**.

> ### `AST`

Abstract Syntax Tree class.

 - `__init__(symbol:Symbol, start_line:int, start_column:int, end_line:int, end_column:int)`
    - Args:
        - `symbol (Symbol)`: internal symbol of the AST.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.


    - Raises: `ValueError` if positions are invalid.

#### Properties

 - `symbol (Symbol)`.
 - `start_position (Tuple[int,int])`: The tuple `(start_line,start_column)`.
 - `end_position (Tuple[int,int])`: The tuple `(end_line,end_column)`.
 - `is_error (bool)`: `True` if is an `ErrorAST`, `False` otherwise.
 - `start_position.setter` / `end_position.setter`: validate ranges.

#### Methods

 - `children() -> List[AST]`: method to be implemented by subclasses (`raise NotImplementedError`). It must return the children of the current AST (by general consensus, in the same order that must be processed normally).
 - `__str__`, `__repr__`: returns `symbol._symbol`.

> ### `Error`

Abstract error class.

 - `__init__(type_:ErrorType | str, start_line:int, start_column:int, end_line:int, end_column:int, msg:str)`
    - Args:
        - `type_ (ErrorType | str)`.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.
        - `msg (str)`.

    - Raises: `TypeError` if `type_` is not a member of `ErrorType` and is not an `str`, `ValueError` if `type_` is not an `ErrorType`, or `ValueError` if positions are invalid.

#### Properties

 - `symbol (Symbol)`.
 - `start_position (Tuple[int,int])`: The tuple `(start_line,start_column)`.
 - `end_position (Tuple[int,int])`: The tuple `(end_line,end_column)`.
 - `type (ErrorType)`: The type of the error.
 - `message (str)`: The message of the error.

#### Methods

 - `__str__`, `__repr__`: returns `f'{type} ERROR at line {start_line}: {msg}'`
 - `__hash__`: precomputed hash using **SHA-256**.
 - `__eq__`: equality by `type`, `message`, and positional values.

> ### `Error` subclasses

All this classes inherits from `Error` class.

#### `LexicalError`

 - `__init__(msg:str, start_line:int, start_column:int, end_line:int, end_column:int)`: sets `type_ = ErrorType.LEXICAL`.

#### `SyntaxError`

 - `__init__(msg:str, start_line:int, start_column:int, end_line:int, end_column:int)`: sets `type_ = ErrorType.SYNTAX`.

#### `SemanticError`

 - `__init__(msg:str, start_line:int, start_column:int, end_line:int, end_column:int)`: sets `type_ = ErrorType.SEMANTIC`.

#### `RuntimeError`

 - `__init__(stack_trace:List[str], start_line:int, start_column:int, end_line:int, end_column:int, msg:str)`: sets `type_ = ErrorType.RUNTIME`.

 - **Property**: `stack_trace (List[str])`.

> ### `ErrorAST`

Error Syntax Tree Class (inherits from `AST`: `ErrorAST(AST)`).

 - `__init__(symbol:Symbol, start_line:int, start_column:int, end_line:int, end_column:int, errors: Set[SemanticError])`
    - Args:
        - `symbol (Symbol)`: internal symbol of the AST.
        - `start_line (int)`, `start_column (int)`: start position in source.
        - `end_line (int)`, `end_column (int)`: end position in source.
        - `errors (Set[SemanticError])`: errors inside the ast.
    
    - Raises: `ValueError` if positions are invalid.
    - Sets `_is_error` internal flag to `True`.

> ### `ASTListView`

View over a list of `AST`.

#### Methods

 - `__len__`: The size of the view (`len(view)`).
 - `__getitem__`: For indexing (`view[idx]`).
    - Raises: `IndexError('ASTListView index out of range')` if `idx < 0` or `idx >= len(view)`

> ### `Token`

Token class (inherits from `AST`: `Token(AST)`).

 - `__init__(text:str, type_:Any, symbol:Symbol, line:int, column:int)`
    - Raises: `ValueError` if `type_` is not a subclass of `TokenType`.
    - Calls `super().__init__(symbol, line, column, line, column + len(text))`.

#### Properties

 - `text`: The text of the token.
 - `type`: The type of the token.

#### Methods

 - `children() -> List[AST]`: returns `[]`

## Submodule `common.table`

> ### `Table`

Class used to store the transitions of an automata.

 - `__init__()`: initializes `_table = {}`.

#### Properties

 - `entries (List[Tuple[str,str]])`: keys of the internal dict.
 - `values (List[str])`: values of the internal dict.
 - `items (List[Tuple[str,str,str]])`: tuples `(from, symbol, value)`.

#### Methods

 - `to_dict() (Dict[Tuple[str,str], str])`: returns copy as a plain dict.
 - `from_dict(data: Dict[Tuple[str,str], str])`: updates `_table` with `data`.
 - `__getitem__`: to access values via `table['f','s']`.
    - Raises: `ValueError` if the coord is not length 2 or if values are not `str`.
 - `__setitem__`: to set values via `table['f','s'] = 't'`.
    - Raises: `ValueError` if the coord is not length 2 or if values are not `str`.
 - `__delitem__`: to delete values via `del table['f','s']`.
    - Raises: `ValueError` if the coord is not length 2 or if values are not `str`.