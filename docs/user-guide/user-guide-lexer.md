# The `lexer` Module

The PyLGEN `lexer` module brings together the tools needed for lexical analysis. Its main class, `Lexer`, converts regex patterns into a `DFA` that traverses the input text and produces tokens. `IndentedLexer` extends this functionality to indentation-sensitive languages ​​by generating `INDENT` and `DEDENT` tokens. Additionally, `LexicalRule` allows for the application of further validations to the tokens. Collectively, the module manages priorities, lexical errors, the end-of-file token, and the mapping of tokens to symbols.

## `Lexer`

`Lexer` is the general-purpose class. It converts regex patterns into a DFA that traverses the input linearly.

> ### Example

=== "Python"

    ```python
    from pylgen.lexer import Lexer
    from pylgen.common.types import Symbol

    def to_symbol(token_type:MyTokenType, text:str):
        if token_type == MyTokenType.NUMBER: return number
        return Symbol(text, True)

    lexer = Lexer(to_symbol, ignore_pattern=r"\s+")
    lexer.set_eof_token("$", MyTokenType.EOF)

    lexer[0, MyTokenType.NUMBER] = r"\d+(\.\d+)?"
    lexer[1, MyTokenType.OPERATOR] = r"\+|\-|\*|/"
    lexer[2, MyTokenType.LPAREN] = r"\("
    lexer[3, MyTokenType.RPAREN] = r"\)"
    ```

=== "Cython"

    ```cython
    from pylgen.lexer cimport Lexer
    from pylgen.common.types cimport Symbol

    cdef Symbol to_symbol(object token_type,str text):
        if token_type == MyTokenType.NUMBER:
            return number
        return Symbol(text,True)
    
    cdef Lexer lexer = Lexer(to_symbol,r'\s+')
    lexer._enum_type = MyTokenType
    lexer.set_eof_token('$',MyTokenType.EOF)

    lexer.add_token_regex(0,MyTokenType.NUMBER,r"\d+(\.\d+)?")
    lexer.add_token_regex(1,MyTokenType.OPERATOR,r"\+|\-|\*|/")
    lexer.add_token_regex(2,MyTokenType.LPAREN, r"\(")
    lexer.add_token_regex(3,MyTokenType.RPAREN, r"\)")
    ```

> ### Priorities

The first element of the index is the **priority**: lower numbers are attempted first. If two patterns match with the same length, the one with the lower priority value wins. This is the mechanism used to resolve `keyword` vs. `identifier` conflicts: keywords come first.

> ### The mapping function

It receives `(MyTokenType, str)` and returns a `Symbol`. PyLGEN validates its type annotations: the first argument must be a subclass of `TokenType`, the second a `str`, and the return type is a `Symbol`. If the annotations are missing, the lexer fails to initialize.

> ### Attributes and Methods

| **Attribute/Method** | **Type** | **Description** |
| :--- | :--- | :--- |
| `tokens` | generator | Iterates over the tokens of the loaded text. |
| `errors` | <span style="white-space: nowrap">`Set[LexicalError]`</span> | Accumulated lexical errors. |
| **`dfa`** | `DFA` | The combined, minimized DFA used for tokenization. Raises `LexerNotInitializedException` if not yet initialized. |
| **`tokens`** | `Iterable[Token]` | A generator that yields tokens from the loaded text. It automatically initializes the lexer and handles ignoring patterns. |
| `load_text(text)` | `None` | Loads text and resets counters. |
| `initialize()` | `None` | Builds the combined DFA. Called automatically. |
| `clear_errors()` | `None` | Clears accumulated errors. |
| `set_eof_token(symbol, type)` | `None` | Defines the end-of-file token. |
| `add_rule(type, rule)` | `None` | Adds a `LexicalRule`. |
| <span style="white-space: nowrap">`add_token_regex(self, priority:int,type_: Any, re:str)`</span> | `None` | Adds a token definition |
| <span style="white-space: nowrap">**`__setitem__(key:Tuple[int,object], re:str)`**</span> | `None` |Allows adding token patterns with `lexer[priority, type_] = r'regex'` syntax. |

## `IdentedLexer`

`IdentedLexer` extends `Lexer` for indentation-sensitive languages. It generates `INDENT` and `DEDENT` tokens by comparing indentation levels between lines.

> ### Example

=== "Python"

    ```python
    from pylgen.lexer import IdentedLexer

    lexer = IdentedLexer(to_symbol, ignore_pattern="#[^\n]*\n?")
    lexer.set_eof_token("$", MyTokenType.EOF)
    lexer.set_ident(MyTokenType.INDENTATION)
    lexer.set_indent_symbol(indent_sym)
    lexer.set_dedent_symbol(dedent_sym)
    lexer.set_text_sanitize_function(sanitize_function)

    # adds tokens
    ```

=== "Cython"

    ```cython
    from pylgen.lexer cimport IdentedLexer

    cdef IdentedLexer lexer = IdentedLexer(to_symbol, ignore_pattern="#[^\n]*\n?")
    lexer._enum_type = MyTokenType
    lexer.set_eof_token("$", MyTokenType.EOF)
    lexer.set_ident(MyTokenType.INDENTATION)
    lexer.set_indent_symbol(indent_sym)
    lexer.set_dedent_symbol(dedent_sym)
    lexer.set_text_sanitize_function(sanitize_function)

    ```

> ### Methods

| **Method** | **Description** |
| :--- | :--- |
| `set_ident(type)` | Token type that counts as indentation. |
| `set_indent_symbol(sym)` | `INDENT` symbol. |
| `set_dedent_symbol(sym)` | `DEDENT` symbol. |
| `set_text_sanitize_function(fn)` | Transforms text before tokenization. |

`set_text_sanitize_function` is useful for converting tabs to spaces or replacing empty lines with a marker that the lexer ignores. In indentation-sensitive languages, an empty line containing accidental spaces can confuse level calculations.

## Lexical Rules

A `LexicalRule` validates tokens beyond what a regex can express: numeric ranges, identifiers that do not start with a digit, etc.

> ### Example

=== "Python"

    ```python
    from pylgen.analysis.lexical import LexicalRule

    class NoLeadingZero(LexicalRule):
        def __init__(self):
            super().__init__("the number cannot start with zero")

            def _check(self, text: str) -> bool:
                return len(text) == 1 or text[0] != "0"


    lexer.add_rule(MyTokenType.NUMBER, NoLeadingZero())
    ```

=== "Cython"

    ```cython
    from pylgen.analysis.lexical cimport LexicalRule

    cdef class NoLeadingZero(LexicalRule):
        def __init__(self):
            super().__init__("the number cannot start with zero")

            cpdef bool _check(self, str text):
                return len(text) == 1 or text[0] != "0"


    lexer.add_rule(MyTokenType.NUMBER, NoLeadingZero())
    ```

If a rule returns `False`, a `LexicalError` is added to `lexer.errors`. Tokenization continues: you can accumulate multiple errors before stopping.