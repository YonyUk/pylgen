# Step 1: Project Structure and Lexer

Create a new project folder `veclang/` with the following files:

    veclang/
        asts.pxd
        asts.pyx
        errors.pxd
        errors.pyx
        lexer.pxd
        lexer.pyi
        lexer.pyx
        parser.pxd
        parser.pyi
        parser.pyx
        setup.py
        tokens_enum.py
        visitors.pxd
        visitors.pyi
        visitors.pyx

We'll write each file step by step.

!!! note "Source code"

    The source code of the test language **VecLang** can be found on the [github repository](https://github.com/YonyUk/pylgen/tree/master/examples/veclang)

    [download source code<br>(veclang)](https://download-directory.github.io/?url=https://github.com/YonyUk/pylgen/tree/master/examples/veclang){ .md-button .md-button--primary style="text-align: center;" }

## 1.1 Token Types (`tokens_enum.py`)

We define our token types using PyLGEN's `TokenType` base class:

File: `tokens_enum.py`
```python
from pylgen.common.enums import TokenType

class TokenTypeEnum(TokenType):

    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    KEYWORD = 'KEYWORD'
    VARIABLE = 'VARIABLE'
    JUMPLINE = 'JUMPLINE'
    COMMENT = 'COMMENT'
    EOF = 'EOF'
```

## 1.2 The Lexer (`lexer.pxd`,`lexer.pyx`,`lexer.pyi`)

Now we build the lexer. It's similar to the arithmetic example, but we add more token patterns.

!!! tip "Good practices"
    This structure is typical for projects that leverage **Cython** to compile the interpreter into a high-performance extension:

    - **`.pxd` files**: contain **C-level** declarations that expose functions and variables to other Cython modules.
    - **`.pyx` files**: hold the actual implementation (the code that gets compiled).
    - **`.pyi` files**: provide Python type stubs for static type checkers (e.g., mypy) and better IDE support.

    Separating interface from implementation like this keeps the codebase modular and makes compilation faster, both critical when scaling to production workloads. 

> ### Declaration (`lexer.pxd`)

This file tells Cython what functions are available to other modules.

File: `lexer.pxd`
```cython
from pylgen.lexer.lexer cimport Lexer
from pylgen.common.types cimport Symbol

cpdef Lexer build_lexer()

cdef Symbol get_symbol_function(object t,str tx)
```

> ### Implementation (`lexer.pyx`)

Here we define the actual logic. One key design choice for performance is to **predefine every grammar symbol** as a `cdef` variable, rather than creating them on the fly. This eliminates object allocation overhead in the tokenisation hot path, a crucial optimization when processing millions of lines.

File: `lexer.pyx`
```cython
from pylgen.lexer.lexer cimport Lexer
from pylgen.common.types cimport Symbol
from .tokens_enum import TokenTypeEnum

cdef Symbol new_line = Symbol('new_line',True) # type:ignore
cdef Symbol int_number = Symbol('integer',True) # type:ignore
cdef Symbol float_number = Symbol('float',True) # type:ignore
cdef Symbol variable = Symbol('variable',True) # type:ignore
cdef Symbol plus = Symbol('+',True) # type:ignore
cdef Symbol minus = Symbol('-',True) # type:ignore
cdef Symbol mod = Symbol('%',True) # type:ignore
cdef Symbol div = Symbol('/',True) # type:ignore
cdef Symbol mul = Symbol('*',True) # type:ignore
cdef Symbol exp = Symbol('**',True) # type:ignore
cdef Symbol eq = Symbol('=',True) # type:ignore
cdef Symbol lp = Symbol('(',True) # type:ignore
cdef Symbol rp = Symbol(')',True) # type:ignore
cdef Symbol lc = Symbol('[',True) # type:ignore
cdef Symbol rc = Symbol(']',True) # type:ignore
cdef Symbol com = Symbol(',',True) # type:ignore
cdef Symbol double_dot = Symbol(':',True) # type:ignore
cdef Symbol sum_keyword = Symbol('sum_keyword',True) # type:ignore
cdef Symbol mean_keyword = Symbol('mean_keyword',True) # type:ignore
cdef Symbol dot_keyword = Symbol('dot_keyword',True) # type:ignore
cdef Symbol print_keyword = Symbol('print_keyword',True) # type:ignore
cdef Symbol type_int = Symbol('int_keyword',True) # type:ignore
cdef Symbol type_float = Symbol('float_keyword',True) # type:ignore
cdef Symbol type_complex = Symbol('complex_keyword',True) # type:ignore
cdef Symbol type_vector = Symbol('vector_keyword',True) # type:ignore
cdef Symbol invalid = Symbol('INVALID TOKEN',True) # type:ignore

cdef Symbol comment = Symbol('COMMENT',True) # type:ignore

cdef dict[str,Symbol] _symbols = {
    '[':lc,
    ']':rc,
    '(':lp,
    ')':rp,
    ',':com,
    ':':double_dot
}

cdef dict[str,Symbol] _operators = {
    '+':plus,
    '-':minus,
    '*':mul,
    '**':exp,
    '/':div,
    '%':mod,
    '=':eq
}

cdef dict[str,Symbol] _keywords = {
    'sum':sum_keyword,
    'mean':mean_keyword,
    'dot':dot_keyword,
    'print':print_keyword,
    'int':type_int,
    'float':type_float,
    'complex':type_complex,
    'vector':type_vector
}

cdef Symbol get_symbol_function(object t,str tx):
    if t == TokenTypeEnum.INTEGER:
        return int_number
    if t == TokenTypeEnum.FLOAT:
        return float_number
    if t == TokenTypeEnum.JUMPLINE:
        return new_line
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.OPERATOR:
        return _operators[tx]
    if t == TokenTypeEnum.SYMBOL:
        return _symbols[tx]
    if t == TokenTypeEnum.KEYWORD:
        return _keywords[tx]
    if t == TokenTypeEnum.COMMENT:
        return comment
    if t == TokenTypeEnum.INVALID_TOKEN:
        return invalid
    raise NotImplementedError()

cpdef Lexer build_lexer():
    lexer = Lexer(get_symbol_function,'\t| |//.*\n',False) # type:ignore
    lexer._enum_type = TokenTypeEnum
    lexer.set_eof_token('\x00',TokenTypeEnum.EOF)
    lexer.add_token_regex(0,TokenTypeEnum.INTEGER,'\\d+')
    lexer.add_token_regex(1,TokenTypeEnum.FLOAT,'\\d*\\.\\d+|\\d+e(\\+|\\-)\\d+')
    lexer.add_token_regex(2,TokenTypeEnum.JUMPLINE,'\n')
    lexer.add_token_regex(3,TokenTypeEnum.KEYWORD,'sum|mean|dot|print|int|float|complex|vector')
    lexer.add_token_regex(4,TokenTypeEnum.VARIABLE,'[a-zA-Z_]\\w*')
    lexer.add_token_regex(5,TokenTypeEnum.OPERATOR,'\\+|\\-|/|\\*\\*?|%|=')
    lexer.add_token_regex(6,TokenTypeEnum.SYMBOL,'\\[|\\]|:|\\(|\\)|\\,')
    lexer.add_token_regex(7,TokenTypeEnum.COMMENT,'//.*\n')
    return lexer
```

!!! note "The automatic member `INVALID_TOKEN`"
    The base class `TokenType`, through its custom metaclass `TokenTypeMeta`, automatically injects an `INVALID_TOKEN` member into each subclass. This member is used internally to represent tokens that don't match any defined pattern. In the `get_symbol_function`, we map `TokenTypeEnum.INVALID_TOKEN` to a dedicated invalid symbol, so that any malformed input produces a clear and identifiable token instead of causing a failure or silent corruption. This design acts as a proactive safety net, catching lexical errors in the early stages of the pipeline.

!!! warning
    In the previous tutorial, in the [step 1](../section-1/example-1-step-1.md), during the lexer definition, the mapping function was written in Python. This allowed the lexer to infer the type of the enum used for tokens from its typing. However, in this case, the mapping function is written in Cython, so the enum type cannot be inferred. This is the reason for the line `lexer._enum_type = TokenTypeEnum`.

!!! tip "The `COMMENT` safety net"
    You'll notice in the next section that the `comment` symbol is defined but never appears in the grammar. This is intentional. We already strip comments using the skip pattern `'\t| |//.*\n'`. However, if that pattern ever fails (e.g., due to a mistake or an edge case), the lexer will produce a COMMENT token. Since this symbol is absent from the grammar, the parser will raise a clear error immediately, alerting us to the issue before it silently corrupts the AST. It's a proactive debugging aid.

> ### Stubs for static typing (`lexer.pyi`)

This file provides type hints for Python consumers of the module.

File: `lexer.pyi`
```python
from pylgen.lexer.lexer import Lexer

def build_lexer() -> Lexer: ...
```