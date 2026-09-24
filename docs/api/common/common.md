# `pylgen.common` Module (The Foundation of PyLGEN)

The `common` submodule is the bedrock upon which the entire PyLGEN ecosystem is built. It provides the fundamental data types, the core abstractions for the **Abstract Syntax Tree (AST)**, **grammar symbols**, **lexical tokens**, the **error hierarchy**, and **transition tables** that connect all the moving parts. Understanding this module is essential, because every other submodule ([`lexer`](../lexer/lexer.md), [`parser`](../parser/parser.md), [`analysis`](../analysis/analysis.md), [`automaton`](../automaton/intro.md), [`regex`](../regex/regex.md), and [`visual`](../visual/visual.md)) depends on it.

In this section, we will explore each class, its purpose, its API (both in pure Python and Cython), and recommended usage patterns. You'll find practical examples that will help you internalize how and when to use each component.

## Structure of the `common` Submodule

The submodule is organized into the following files (all located in `pylgen/common/`):

| **File** | **Purpose** |
| :---: | :---: |
| `enums.py` | Defines the `TokenType` base class (a `StrEnum`) for all token types. |
| `types.pxd` |	Cython declarations for `Symbol`, `AST`, the `Error` hierarchy (`Error`, `LexicalError`, `SyntaxError`, `SemanticError`, `RuntimeError`), `ErrorAST`, `ASTListView`, and `Token`. |
| `types.pyx` |	Cython implementation of those classes (with `cdef` and `cpdef` methods). |
| `types.pyi` |	Stubs for type checkers and IDE autocompletion in Python environments. |
| `table.pxd` |	Cython declarations for the `Table` class. |
| `table.pyx` |	Implementation of `Table`. |
| `table.pyi` |	Stubs for `Table`. |

!!! note "Python/Cython Duality"
    All classes are defined as `cdef class` in the `.pyx` files, allowing them to be used efficiently from Cython. However, they are also fully usable from standard Python, thanks to the `.pyi` stubs and the fact that Cython generates code that is compatible with the Python interpreter. This means you can prototype in pure Python and, when you need speed, compile with Cython without changing your business logic.

## `Symbol` (The Atom of the Grammar)

A `Symbol` represents a **grammar symbol**, which can be a **terminal** (a token from the lexer) or a **non-terminal** (an abstract category that expands into other symbols). There is also the special **epsilon (ε) symbol**, which represents the empty string.

> ### 1. Creation and Attributes

=== "Python"

    ```python
    from pylgen.common.types import Symbol

    # Non-terminal: 'E' (expression)
    E = Symbol('E')

    # Terminal: the '+' sign
    plus = Symbol('+', is_terminal=True)

    # Epsilon (always a terminal)
    eps = Symbol('ε', is_terminal=True, is_epsilon=True)
    ```

=== "Cython"
    ```cython
    from pylgen.common.types cimport Symbol

    # Non-terminal: 'E' (expression)
    cdef Symbol E = Symbol('E')

    # Terminal: the '+' sign
    cdef Symbol plus = Symbol('+', is_terminal=True)

    # Epsilon (always a terminal)
    cdef Symbol eps = Symbol('ε', is_terminal=True, is_epsilon=True)
    ```

| **Attribute** | **Type** | **Description** | **Default value** |
| :---: | :---: | :---: | :---: |
| `symbol` | `str` | The name of the symbol (e.g., `'E'`, `'+'`). | **required** |
| `is_terminal` | `bool` | `True` if it is a terminal (token), `False` if non-terminal. | `False` |
| `is_epsilon` | `bool` | `True` if it is the `ε` symbol (implies `is_terminal` is also `True`). | `False` |

!!! warning
    Only a **terminal symbol** can be **epsilon**, if you try `s = Symbol('epsilon',is_epsilon=True)` a `ValueError` will be raised.

> ### 2. Equality and Hashing Semantics

Two `Symbol` objects are considered **equal** if and only if **all three of their attributes** (`symbol`, `is_terminal`, and `is_epsilon`), are identical. This means that symbols with the same name but different terminal/epsilon flags are distinct and will not compare equal.

```python
from pylgen.common.types import Symbol

s1 = Symbol('+', is_terminal=True)
s2 = Symbol('+', is_terminal=True)
s3 = Symbol('+')                     # non-terminal (is_terminal=False)

assert s1 == s2      # True
assert s1 == s3      # False (different is_terminal)
```

This equality semantics is crucial for grammar definitions and parser table construction, where symbols are used as keys in dictionaries and sets.

#### Hash consistency across runs

The hash value of a `Symbol` is computed deterministically using the **SHA‑256 digest** of a canonical string representation: `f"{symbol}-{is_terminal}-{is_epsilon}"`. As a result, the hash is **stable across different Python processes and even across different machines**, provided the attributes are the same. This is especially useful for:

 - Caching generated parser tables to disk (you can safely reuse them across invocations).

 - Serializing grammars or ASTs without worrying about hash randomization.

 - Reproducible builds and testing.

The hash is calculated once in the constructor and stored in a private `_hash` field, making subsequent lookups in dictionaries and sets extremely fast.

!!! note
    The SHA‑256 digest is accumulated into a `long long` and then stored in a `cdef int _hash` field, so the final hash is a 32‑bit C integer.

## AST (The Root of Every Tree)

`AST` is the abstract base class for all **Abstract Syntax Tree** nodes. Every node you build must inherit from it and, at a minimum, implement the `children()` method, which returns the list of its child nodes (sub‑ASTs). The base implementation of `children()` raises `NotImplementedError`, so you are required to override it in concrete subclasses.

> ### 1. Attributes and Methods

| **Attribute/Method** | **Type/Return** | **Description** |
| :---: | :---: | :---: |
| **`symbol` (property)** |	`Symbol` | The grammar symbol associated with this node. |
| **`start_position` (property)** | `Tuple[int, int]` | `(start_line, start_column)` where the node starts. |
| **`end_position` (property)** | `Tuple[int, int]` | `(end_line, end_column)` where the node ends. |
| **`is_error` (property)** | `bool` | Indicates whether this node represents a semantic error. Always `False` for `AST`; overridden in `ErrorAST` | 
| `children()` (method) | `List[AST]` | Returns a list of child AST nodes. Must be overridden. |

!!! note
    Both, `start_position` and `end_position` are 1-indexed, this means that index 1 points to 0 real index in a list.

!!! warning "Validation"
    The constructor of AST raises a `ValueError` if `start_line` or `start_column` are negative, if `end_line < start_line`, or if `end_line == start_line` and `end_column <= start_column`. The setters for `start_position` and `end_position` perform similar checks.

!!! note "String Representation"
    Both `__str__` and `__repr__` return the string representation of the internal `Symbol` (i.e., the symbol’s name). This makes debugging and logging more convenient.

=== "Python"

    ```python
    from pylgen.common.types import AST, Symbol

    class BinaryOpAST(AST):
        def __init__(self, left: AST, right: AST, symbol: Symbol):
            (start_line,start_column),(end_line,end_column) = left.start_position,right.end_position
            super().__init__(symbol, start_line, start_column, end_line, end_column)
            self._left = left
            self._right = right

        def children(self) -> List[AST]:
            return [self._left, self._right]
    ```
=== "Cython"
    ```cython
    from pylgen.common.types cimport AST

    cdef class BinaryOpAST(AST):
        cdef AST _left
        cdef AST _right
        cdef list[AST] _childs

        cpdef list[AST] children(self):
            return self._childs
    ```

!!! tip "Best Practice"
    Always declare attributes as cdef with concrete types whenever possible. This speeds up access and assignment in reducers and visitors.

## Error Hierarchy

A robust error handling system is essential for any language implementation. PyLGEN provides a unified, hierarchical error model that spans all phases of the compilation pipeline, from lexing to runtime execution. Every error carries precise location information (start and end position) and a descriptive message, making it easy to report problems directly to the user.

The hierarchy is built around a common base class `Error`, with specialized subclasses for each stage of processing. All errors are collected in the `Context` (semantic and runtime) or in the lexer/parser themselves (lexical and syntax), allowing you to aggregate and report multiple issues in a single pass.

> ### `ErrorType` (Enumeration)

The `ErrorType` enum (`pylgen.common.enums`) categorises errors by their origin:

```python
from enum import StrEnum

class ErrorType(StrEnum):
    LEXICAL = 'LEXICAL'
    SYNTAX = 'SYNTAX'
    SEMANTIC = 'SEMANTIC'
    RUNTIME = 'RUNTIME'
```

These values are used internally to tag each error and to format user‑friendly messages.

> ### The `Error` Base Class

`Error` is the abstract base class for all compile‑time errors (lexical, syntax, semantic) and also for runtime errors. It provides the common attributes and formatting logic.

| **Attribute/Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`start_position` (property)** | `Tuple[int, int]` | `(start_line, start_column)` where the error starts. |
| **`end_position` (property)** | `Tuple[int, int]` | `(end_line, end_column)` where the error ends. |
| **`type`** | `ErrorType` | The category of the error. |
| **`message`** | `str` | A human‑readable error message, formatted as `"{type} ERROR at line {line}: {msg}"`. |

The constructor accepts the error type (either a member of `ErrorType` or a string that matches one of its values), the `start_line`/`start_column` number, the `end_line`/`end_column` number, and a custom message. If a string is given, it is internally converted to the corresponding `ErrorType` member; otherwise, a `TypeError` or `ValueError` is raised.

!!! note "Hash Consistency"
    Like `Symbol`, `Error` objects compute a deterministic 64‑bit hash based on a SHA‑256 digest of the string `f'{type_}-{start_line}-{start_column}-{end_line}-{end_column}-{msg}'`. This hash is stable across runs and is used for `set`/`dictionary` lookups (e.g., when collecting unique errors).

> ### Concrete Error Classes

| **Class** | **Description** |
| :---: | :---: |
| <span style="white-space: nowrap">**`LexicalError`**</span> | Raised during lexing when a token does not match any pattern or fails a lexical rule (e.g., malformed number, invalid character). |
| <span style="white-space: nowrap">**`SyntaxError`**</span> | Raised during parsing when the token stream does not conform to the grammar (e.g., unexpected token, missing semicolon). |
| <span style="white-space: nowrap">**`SemanticError`**</span> | Raised during semantic analysis for violations that cannot be detected by the grammar (e.g., undeclared variable, type mismatch, duplicate definition). |
| <span style="white-space: nowrap">**`RuntimeError`**</span> | Raised during evaluation or execution of the AST (e.g., division by zero, invalid operation, out‑of‑bounds access). Unlike the other errors, it includes a stack trace to help debug the execution context. |

All of these classes inherit directly from `Error` and simply forward their arguments to the base class constructor, providing a consistent interface.

> ### Runtime Errors and Stack Traces

`RuntimeError` adds a `stack_trace` property, which is a list of strings representing the call stack at the point where the error occurred. This is particularly useful for debugging interpreted languages, as it allows you to trace back through nested function calls or expression evaluations. The stack trace is maintained by the `Context` (via `push_trace` and `pop_trace`) and can be passed to the error when it is raised.

## `ErrorAST` (Handling Semantic Errors during Syntactic Analysis)

`ErrorAST` is a specialized subclass of `AST` that represents a node inserted into the syntax tree **exclusively during syntactic analysis** to report **semantic errors** (e.g., type mismatches or other contextual checks performed by reducers). It is **not** intended for syntactic errors (unexpected tokens, malformed productions, etc.); those are handled by the parser's error recovery mechanism without producing `ErrorAST` nodes.

By embedding `ErrorAST` nodes directly into the tree, the parser can continue processing and report multiple semantic errors in a single pass, and later stages can easily detect and handle problematic regions of the AST.

!!! note
    `ErrorAST` inherits all attributes of `AST`. Its `is_error` property is always `True`, and the `_errors` internal set stores the reported semantic errors. This allows downstream visitors to easily identify error nodes and skip or handle them appropriately.

> ### Usage

=== "Python"

    ```python
    from pylgen.common.types import ErrorAST, Symbol, SemanticError

    error = SemanticError("semantic error detected", 10, 5, 10, 6)
    sl, sc = error.start_position
    el, ec = error.end_position
    err_node = ErrorAST(Symbol('error'), sl, sc, el, ec, {error})
    ```

=== "Cython"

    ```cython
    from pylgen.common.types cimport ErrorAST, Symbol, SemanticError

    cdef SemanticError error = SemanticError("semantic error detected", 10, 5, 10, 6)
    cdef ErrorAST err_node = ErrorAST(Symbol('error'), 10, 5, 10, 6, {error})
    ```

## `Token` (The Node from the Lexer)

`Token` inherits from `AST` and represents a concrete **lexical token**: a specific piece of text identified by the lexer. In addition to its location and symbol (mapped from the token type), it stores the original text and its type.

> ### 1. Additional Attributes

| **Attribute** | **Type** | **Description** |
| :---: | :---: | :---: |
| `text` | `str` | The exact text that matched the pattern (e.g., `"123"`, `"+"`). |
| `type` | `TokenType` | The token type (a value from your enumeration that inherits from `TokenType`). |

#### Creation

The constructor requires the token text, its **type (must be an instance of a subclass of `TokenType`)**, the corresponding `Symbol`, and the location. It raises a `ValueError` if `type_` is not an instance of a `TokenType` subclass.

=== "Python"
    ```python
    from pylgen.common.types import Token,Symbol
    from your_tokens import TokenTypeEnum   # your enumeration

    symbol = Symbol

    token = Token("123", TokenTypeEnum.INTEGER, int_symbol, 1, 5)
    ```
=== "Cython"
    ```cython
    from pylgen.common.types cimport Token
    from your_tokens import TokenTypeEnum   # your enumeration

    cdef Token token = Token("123", TokenTypeEnum.INTEGER, int_symbol, 1, 5)
    ```

!!! note
     - Since a `Token` is a leaf node, its `children()` method returns an empty list. This is consistent with the fact that tokens do not have sub‑ASTs.

     - Like all `AST` nodes, `Token` has an `is_error` property; for tokens it is always `False` because they represent valid lexical input.

> ### 2. Usage in Reducers

In reducers, you often need to inspect the text or type of a token to build the correct AST. For example:

=== "Python"
    
    ```python
    def number_reductor(asts: ASTListView) -> AST:
        token:Token = asts[0] # this is a Token
        line, column = token.start_position
        if token.type == TokenTypeEnum.INTEGER:
            return NumberAST(int(token.text),line,column)
        return NumberAST(float(token.text),line,column)
    ```

=== "Cython"
    ```cython
    cdef AST number_reductor(ASTListView asts):
        cdef Token token = asts[0]
        if token._type == TokenTypeEnum.INTEGER:
            return NumberAST(int(token._text),token._start_line,token._start_column)
        return NumberAST(float(token._text),token._start_line,token._start_column)
    ```

## `ASTListView` (A Lightweight View for Reducers)

When the parser reduces a production, it passes an `ASTListView` object to the reducer function. This object contains the ASTs of the right-hand side symbols, in the exact order they appear in the production. This view is **inmutable and efficient**: it does not copy the underlying list, but rather provides indexed access and length via optimized internal methods. Indexing is 0‑based, and out‑of‑range access raises `IndexError`.

> ### 1. API

| **Method/Operator** | **Description** |
| :---: | :---: |
| **`__getitem__(idx)`** | Gets the AST at position `idx` (0-based). |
| **`__len__()`** | Returns the number of elements |
| **`_get(idx)` (Cython only)** | Same as `__getitem__(idx)`, but a `cdef inline` method for maximum performance. |
| **`_size()` (Cython only)** | Same as `__len__()`, but `cdef inline`. |

> ### 2. Typical Usage

=== "Python"

    ```python
    # E -> E + T | T reductor
    def e_reductor(asts:ASTListView) -> AST:
        if len(asts) == 1:
            return asts[0]
        left = asts[0]
        right = asts[2]
        op = asts[1]
        return BinaryOpAST(left,right,op.symbol)
    ```

=== "Cython"

    ```cython
    # E -> E + T | T reductor
    cdef AST e_reductor(ASTListView asts):
        cdef AST left,right,op
        if asts._size() == 1:
            return asts._get(0)
        left = asts._get(0)
        right = asts._get(2)
        op = asts._get(1)
        return BinaryOpAST(left,right,op._symbol)
    ```

!!! tip "Pro Tip"
    In Cython, prefer `_get(idx)` and `_size()` over `__getitem__(idx)` and `__len__()` to avoid the overhead of type checking and conversion to Python that occurs in the dunder methods. This is especially critical in parsing loops over millions of lines.

## `Table` (Transition Tables for Automata and Parsers)

`Table` is a specialized container that acts like a dictionary with two-element keys `(str,str)` and `str` values. It is used internally in the `automaton` module to store transitions for automata.

> ### 1. API

| **Method/Property** | **Description** |
| :---: | :---: |
| **`entries` (property)** | List of all keys `(row,column)`. |
| **`values` (property)** | List of all stored values. |
| **`items` (property)** | List of tuples `(row,column,value)`. |
| **`to_dict()`** | Converts the table to a dictionary `{(row,column): value }`. |
| **`from_dict(data)`** | Loads the data from a dictionary. |
| **`__getitem__((row,column))`** | Gets the value. |
| **`__setitem__((row,column),value)`** | Inserts or updates an entry. |
| **`__delitem__((row,column))`** | Deletes an entry. |

> ### 2. Example Usage

```python
from pylgen.common import Table

table = Table()
table['q0','a'] = 'q1'
table['q1','b'] = 'q2'

print(table['q0','a'])      # 'q1'
print(table.items)        # [('q0','a','q1'),('q1','b','q2')]
```

!!! note "In Cython"
    The Cython implementation is virtually identical, but operations are faster because `__getitem__`,`__setitem__`, and `__delitem__` are optimized and avoid type-checking overhead on each access (though they still perform checks in error cases).

## `TokenType` (The Base for Your Token Enumerations)

`TokenType` is a class tha inherits from `StrEnum` (available in Python 3.11+). Its purpose is to provide a type-safe way to define all possible token types your lexer can generate. You must create a subclass with the names you need:

```python
from pylgen.common.enums import TokenType

class MyTokenType(TokenType):
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    IDENTIFIER = 'IDENTIFIER'
    PLUS = 'PLUS'
    # ...
```

Later, when configuring your lexer, you will use this enumeration to associate each regex pattern with a token type.

!!! important "The automatic member `INVALID_TOKEN`"
    The base class `TokenType`, through its custom metaclass `TokenTypeMeta`, automatically injects an `INVALID_TOKEN` member into each subclass. This member is used internally to represent invalid tokens.

## Integration with the Rest of PyLGEN

The `common` module is never used in isolation. Here is a quick map of how it relates to other modules:

 - [**Lexer**](../lexer/lexer.md): Tokens are created as instances of `Token`, and the mapping function (which you provide), takes the token type (`TokenType`) and text to return a `Symbol`.
 - [**Grammar**](../grammar/grammar.md#usage-example): Symbols (`Symbol`) are used in productions, and reducers receive `ASTListView`.
 - [**Parser**](../parser/parser.md#parser-abstract-base-class): The parser returns an `AST` (the root of the tree), and the parsing tables are built with `Table` objects.
 - [**Analysis**](../analysis/analysis.md#the-visitor-framework): `ASTWalker` and `ASTVisitor` operate on `AST` nodes.

## Best Practices for Maximum Performance

 - `1`. **Predefine symbols and tables** outside of loops (at the module level) to avoid repeated object creation.
 - `2`. **Use `cdef` for all attributes** of your AST and visitor classes. This turns attribute access into C struct member access, eliminating dictionary lookups.
 - `3`. **In reducers, use `_get(idx)` and `_size()` instead of `__getitem__(idx)` and `__len__()`** when writing Cython code.
 - `4`. **Prefer `start_position` / `end_position`** (o sus campos Cython `_start_line`, `_start_column`, etc.) over separate `line`/`column` properties, the latter do not exist in the current implementation.
 - `5`. **Leverage Cython compilation**: your code can run at speeds very close to C if you follow these guidelines, especially in the critical parsing and evaluation paths.