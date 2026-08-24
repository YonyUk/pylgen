# `pylgen.lexer` Module (The Scanning Engine)

Welcome to the `lexer` module, the entry point of any language pipeline. If the [`regex`](../regex/regex.md) module is about **describing** patterns, the lexer module is about **applying** them to raw source code, transforming a character stream into a meaningful token stream. This module is where regular expressions meet practicality, where theory becomes execution.

Lexical analysis(or scanning) is the first phase of compilation. Its job is to read the source code character by character, group them into *lexemes*, and classify each lexeme as a *token* (e.g., `NUMBER`, `IDENTIFIER`, `PLUS`). This process is fundamentally driven by **regular languages**: the set of valid lexemes for each token type is a regular language, which can be described by a regular expression and recognized by a finite automaton.

PyLGEN's lexer module builds upon the `regex` engine to provide a flexible, high‑performance lexer that is both easy to configure and deeply integrated with the rest of the framework. It handles:

 - Token prioritization (e.g., keywords before identifiers).

 - Pattern matching using regular expressions (converted to DFAs).

 - Lexical validation (custom rules beyond regex, e.g., numeric bounds).

 - Error collection (lexical errors are reported with location).

 - Ignoring whitespace and comments.

 - End‑of‑file token handling.

In this section, we dissect the architecture of the `lexer`, starting from the foundational `BaseLexer` and then moving to the user‑friendly `Lexer` subclass that is typically used in practice.

## Formal Foundations: From Regular Expressions to Tokenization

A lexer is essentially a **deterministic finite automaton (DFA)** that operates over the input character stream. The set of tokens is defined by a finite set of regular expressions, each associated with a token type. The lexer's job is to find the **longest match** among all active patterns, given a prioritization rule.

The formal model is as follows:

 - Let $\Sigma$ be the input alphabet (e.g., ASCII characters).
 
 - Foreach token type $t$, we have a regular language $L_t \subseteq \Sigma^*$.
 
 - The lexer, given a position in the input, must find the longest prefix $w$ that belongs to some $L_t$ (respecting priority in case of ambiguity).

 - It returns a token $\lparen t,w \rparen$ and advances the position by $|w|$.

 - If no $L_t$ matches, a lexical error is reported.

This is exactly the behavior of a [**maximal munch**](https://en.wikipedia.org/wiki/Maximal_munch) lexer. To implement this efficiently, we combine all patterns into a single DFA where each accepting state is annotated with the token type(s) it matches. The DFA is then run over the input, and we keep track of the last accepting state encountered; when the DFA gets stuck, we backtrack to that last accepting state to emit the token.

## The Role of `BaseLexer`

The `BaseLexer` class is the pure scanning engine. It expects to receive a set of **pre‑built automata** ([DFAs or NFAs](../automaton/automaton.md#the-base-class-automaton)) for each token type, along with a priority order. It then:

 - Combines all automata into a single NFA using union, then determinizes and minimizes the result.

 - Performs a **minimization with an initial partition** based on token types, ensuring that states with different token type sets are not merged (this preserves the ability to distinguish tokens).

 - Provides the scanning loop that implements the maximal munch algorithm.

 - Supports an **ignore pattern** (e.g., whitespace) that is skipped during tokenization.

The `Lexer` subclass builds on top of this by allowing the user to specify regular expressions as strings (rather than automata) and adds support for lexical validation rules and error handling.

## Core Classes

> ### `BaseLexer` (The Scanning Engine)

`BaseLexer` is an abstract‑like class that provides the core scanning functionality. It is not meant to be instantiated directly by end users; instead, it is the foundation for Lexer. However, it can be subclassed for advanced use cases.

#### Constructor

```python
BaseLexer(get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA, check_annotation: bool = True)
```

 - `get_symbol_function`: A function that maps a token type (the enumeration value) and its lexeme (string) to a [`Symbol`](../common/common.md#symbol-the-atom-of-the-grammar) (terminal) for the parser. This bridges the lexer and the grammar.

!!! important
    The lexer validates that `get_symbol_function` has the correct annotations:

    - First parameter: must be a subclass of `TokenType`.

    - Second parameter: must be `str`.

    - Return: must be `Symbol`.

 - `ignore_pattern`: A DFA that recognizes characters to ignore (e.g., whitespace). The lexer will skip matches of this DFA during tokenization.

 - `check_annotation`: If True, the constructor validates that `get_symbol_function` has the correct annotations (first arg is a subclass of `TokenType`, second is `str`, return is `Symbol`). This catches configuration errors early.

#### Attributes

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`dfa`** | `DFA` | The combined, minimized DFA used for tokenization. Raises `LexerNotInitializedException` if not yet initialized. |
| **`tokens`** | `Iterable[Token]` | A generator that yields tokens from the loaded text. It automatically initializes the lexer and handles ignoring patterns. |

#### Method

| **Method** | **Description** |
| :---: | :---: |
| **`load_text(text:str)`** | Loads a new input string for tokenization. Resets line/column counters. |
| **`initialize()`** | Builds the combined DFA from the provided automata and minimizes it. Called automatically when `tokens` is accessed, but can be called manually to force early initialization. |
| **`__setitem__(key: Tuple[int, object], automaton: Automaton)`** | Allows adding an automaton (DFA or NFA) directly using the syntax `lexer[priority, type_] = automaton`. The priority (integer, lower value = higher priority) and token type are specified in the key.

> ### `Lexer` (The User‑Facing Lexer)

`Lexer` extends `BaseLexer` and adds the convenience of specifying token patterns as regular expression strings, as well as support for lexical rules and error handling.

#### Constructor

```python
Lexer(get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: str, check_annotation: bool = True)
```

 - `ignore_pattern`: A regular expression string (not a DFA) that defines the characters to ignore (e.g., `\n|\t|`).

#### Attributes

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`errors`** | `Set[LexicalError]` | A set of lexical errors collected during tokenization. Cleared with `clear_errors()`. |

#### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`add_token_regex(priority:int, type_:Any, re:str)`** | Adds a token pattern using a regex string. The regex is parsed into a DFA, and each accepting state is annotated with the token type. |
| **`set_eof_token(symbol:str, type_:Any)`** | Sets the end‑of‑file token. The symbol is the terminal symbol (string) and `type_` is the token type enumeration value. |
| **`add_rule(type_:Any, rule:LexicalRule)`** | Adds a `LexicalRule` to perform additional validation on tokens of the given type. Rules are checked during tokenization; if a rule fails, a `LexicalError` is added to `errors`. |
| **`clear_errors()`** | Clears all collected lexical errors. |
| **`__setitem__(key:int, re:str)`** | Allows adding token patterns with `lexer[priority, type_] = r'regex'` syntax. |
| **`tokens` (property)** | Yields tokens, including the EOF token at the end. This overrides the base property to add EOF handling. |

> ### `IdentedLexer`

`IdentedLexer` extends `Lexer` to handle languages with significant indentation (like Python). It generates `INDENT` and `DEDENT` tokens based on the indentation level of each line, allowing block structure to be represented in the token stream.

#### Constructor

```python
IdentedLexer(get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: str, check_annotation: bool = True)
```

Parameters are the same as for `Lexer`.

#### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`set_ident(ident_type: object)`** | Sets the token type (An instance of a subclass of `TokenType` ) that represents indentation (e.g., `MyToken.INDENT`). |
| **`set_indent_symbol(symbol: Symbol)`** | Sets the symbol to be used for `INDENT` tokens. |
| **`set_dedent_symbol(symbol: Symbol)`** | Sets the symbol to be used for `DEDENT` tokens. |
| **`set_text_sanitize_function(sanitaze_function: Callable[[str], str])`** | Assigns a function that is applied to the full text before tokenisation (useful for converting tabs to spaces, normalising line breaks, etc.). |
| **`load_text(text: str)`** | Loads the text and, if a sanitisation function is defined, applies it before storing. |

!!! note
    Whitespace tokens that do not appear at the beginning of a line are automatically ignored.

## Lexical Rules and Error Handling

`Lexer` integrates with the [`analysis.lexical`](../analysis/analysis.md) module, which defines the [`LexicalRule`](../analysis/analysis.md#lexical-rules) abstract class. A lexical rule is a validation check that operates on a token's text. For example, you might have a rule that ensures a number does not have leading zeros, or that an identifier does not start with a digit.

When a rule fails, it returns a [`LexicalError`](../analysis/analysis.md#concrete-error-classes) object that is added to the lexer's errors set. The tokenization process does not stop on errors; it continues to collect all errors, allowing you to report them all at once.

## Building the Combined DFA

The `initialize()` method in `BaseLexer` performs the following steps:

 - **`1` Union all automata**: All token automata (DFAs or NFAs) are combined into a single NFA using the union operation from the `automaton` module. The resulting NFA recognizes the union of all token languages, but does not yet encode priority.

 - **`2` Determinize**: The NFA is determinized to obtain a DFA.

 - **`3` Complete**: The DFA is made complete (by adding a fault state) so that it never gets stuck.

 - **`4` Minimize with initial partition**: Instead of a standard minimization, we provide a custom initial partition that groups states by the set of token types they accept. This ensures that states that accept different token types are never merged, preserving the ability to disambiguate tokens after minimization.

 - **`5` Store mappings**: After minimization, we build a map from state ID to the set of token types accepted by that state. This is used during scanning to determine the token type of a matched lexeme.

This minimization step is crucial for performance: it reduces the DFA to its smallest equivalent form while preserving token discrimination.

## Code Examples

> ### Minimal Lexer Configuration

=== "Python"

    ```python
    from pylgen.lexer.lexer import Lexer
    from pylgen.common.types import Symbol
    from pylgen.common.enums import TokenType

    class TokenTypeEnum(TokenType):
        NUMBER = 'NUMBER'
        SYMBOL = 'SYMBOL'
        OPERATOR = 'OPERATOR'
        VARIABLE = 'VARIABLE'
        KEYWORD = 'KEYWORD'

    def get_symbol_function(t: TokenTypeEnum, tx: str) -> Symbol:
        if t == TokenTypeEnum.NUMBER:
            return number  # pre‑defined Symbol
        if t == TokenTypeEnum.SYMBOL:
            return Symbol(tx, True)
        if t == TokenTypeEnum.VARIABLE:
            return variable
        if t == TokenTypeEnum.KEYWORD:
            return Symbol(tx, True)
        return Symbol(tx, True)

    lexer = Lexer(get_symbol_function, '\n|\t| ')
    lexer.set_eof_token(END_SYMBOL, TokenTypeEnum.SYMBOL)

    # Add patterns with priority (lower = higher)
    lexer[0, TokenTypeEnum.NUMBER] = r'\d+|\d+\.\d+'
    lexer[1, TokenTypeEnum.SYMBOL] = r'\(|\)'
    lexer[2, TokenTypeEnum.OPERATOR] = r'\+|\*\*?|\-|/|%|='
    lexer[3, TokenTypeEnum.KEYWORD] = r'exit|clear'
    lexer[4, TokenTypeEnum.VARIABLE] = r'\w+'

    # Add lexical rules (optional)
    from pylgen.analysis.lexical import LexicalRule

    class NumberLexicalRule(LexicalRule):
        def _check(self, text: str) -> bool:
            return str(float(text)) == text or str(int(text)) == text

    lexer.add_rule(TokenTypeEnum.NUMBER, NumberLexicalRule('message'))
    ```
=== "Cython"

    ```cython
    from pylgen.lexer.lexer cimport Lexer
    from pylgen.common.types cimport Symbol
    from pylgen.common.enums import TokenType

    class TokenTypeEnum(TokenType):
        NUMBER = 'NUMBER'
        SYMBOL = 'SYMBOL'
        OPERATOR = 'OPERATOR'
        VARIABLE = 'VARIABLE'
        KEYWORD = 'KEYWORD'

    cdef Symbol get_symbol_function(object t, str tx):
        if t == TokenTypeEnum.NUMBER:
            return number  # pre‑defined Symbol
        if t == TokenTypeEnum.SYMBOL:
            return Symbol(tx, True)
        if t == TokenTypeEnum.VARIABLE:
            return variable
        if t == TokenTypeEnum.KEYWORD:
            return Symbol(tx, True)
        return Symbol(tx, True)

    cdef Lexer lexer = Lexer(get_symbol_function, r'\n|\t| ')
    lexer._enum_type = TokenTypeEnum
    lexer.set_eof_token(END_SYMBOL, TokenTypeEnum.SYMBOL)

    # Add patterns with priority (lower = higher)
    lexer.add_token_regex(0, TokenTypeEnum.NUMBER, r'\d+|\d+\.\d+')
    lexer.add_token_regex(1, TokenTypeEnum.SYMBOL, r'\(|\)')
    lexer.add_token_regex(2, TokenTypeEnum.OPERATOR, r'\+|\*\*?|\-|/|%|=')
    lexer.add_token_regex(3, TokenTypeEnum.KEYWORD, r'exit|clear')
    lexer.add_token_regex(4, TokenTypeEnum.VARIABLE, r'\w+')

    # Add lexical rules (optional)
    from pylgen.analysis.lexical cimport LexicalRule

    cdef class NumberLexicalRule(LexicalRule):
        cpdef bool _check(self, str text):
            return str(float(text)) == text or str(int(text)) == text

    lexer.add_rule(TokenTypeEnum.NUMBER, NumberLexicalRule('message'))
    ```

> ### Minimal `IdentedLexer` configuration

=== "Python"

    ```python
    from pylgen.common.enums import TokenType
    from pylgen.common.types import Symbol
    from pylgen.lexer.lexer import IdentedLexer

    # ...

    class TokenTypeEnum(TokenType):
        NUMBER = 'NUMBER'
        STRING = 'STRING'
        BOOLEAN = 'BOOLEAN'
        NEWLINE = 'NEWLINE'
        SYMBOL = 'SYMBOL'
        EOF = 'EOF'
        VARIABLE = 'VARIABLE'
        IDENTATION = 'IDENTATION'
        WHITESPACEMARKER = 'WHITESPACEMARKER'
        SINGLEWHITESPACE = 'SINGLEWHITESPACE'

    def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
        if t == TokenTypeEnum.NEWLINE:
            return newline
        if t == TokenTypeEnum.NUMBER:
            return number
        if t == TokenTypeEnum.BOOLEAN:
            return boolean
        if t == TokenTypeEnum.STRING:
            return string
        if t == TokenTypeEnum.IDENTATION:
            return indent
        if t == TokenTypeEnum.VARIABLE:
            return variable
        if t == TokenTypeEnum.SYMBOL:
            return Symbol(tx,True)
        return Symbol(tx,True)

    def sanitaze_text(text:str) -> str:
        lines = text.split('\n')
        lines = list(map(lambda line:line if not line.strip() == '' else '#ignore#', lines))
        return '\n'.join(lines)

    lexer = IdentedLexer(get_symbol_function,'#ignore#\n?')
    lexer.set_text_sanitize_function(sanitaze_text)
    lexer[0,TokenTypeEnum.NUMBER] = r'\d+(\.\d+)?'
    lexer[1,TokenTypeEnum.BOOLEAN] = 'true|false'
    lexer[2,TokenTypeEnum.VARIABLE] = r'[a-zA-Z_]\w*'
    lexer[3,TokenTypeEnum.IDENTATION] = '    |\t'
    lexer[4,TokenTypeEnum.NEWLINE] = '\n'
    lexer[5,TokenTypeEnum.SYMBOL] = r'\-|:|\[|\]'
    lexer[6,TokenTypeEnum.STRING] = '".*"'
    lexer[7,TokenTypeEnum.WHITESPACEMARKER] = '#ignore#\n'
    lexer[8,TokenTypeEnum.SINGLEWHITESPACE] = ' '

    lexer.set_ident(TokenTypeEnum.IDENTATION)
    lexer.set_indent_symbol(indent)
    lexer.set_dedent_symbol(dedent)
    lexer.set_eof_token('$',TokenTypeEnum.SYMBOL)
    ```

=== "Cython"

    ```cython
    from pylgen.common.enums cimport TokenType
    from pylgen.common.types cimport Symbol
    from pylgen.lexer.lexer cimport IdentedLexer

    # ...

    class TokenTypeEnum(TokenType):
        NUMBER = 'NUMBER'
        STRING = 'STRING'
        BOOLEAN = 'BOOLEAN'
        NEWLINE = 'NEWLINE'
        SYMBOL = 'SYMBOL'
        EOF = 'EOF'
        VARIABLE = 'VARIABLE'
        IDENTATION = 'IDENTATION'
        WHITESPACEMARKER = 'WHITESPACEMARKER'
        SINGLEWHITESPACE = 'SINGLEWHITESPACE'

    cdef Symbol get_symbol_function(object t,str tx):
        if t == TokenTypeEnum.NEWLINE:
            return newline
        if t == TokenTypeEnum.NUMBER:
            return number
        if t == TokenTypeEnum.BOOLEAN:
            return boolean
        if t == TokenTypeEnum.STRING:
            return string
        if t == TokenTypeEnum.IDENTATION:
            return indent
        if t == TokenTypeEnum.VARIABLE:
            return variable
        if t == TokenTypeEnum.SYMBOL:
            return Symbol(tx,True)
        return Symbol(tx,True)

    cdef str sanitaze_text(str text):
        lines = text.split('\n')
        lines = list(map(lambda line:line if not line.strip() == '' else '#ignore#', lines))
        return '\n'.join(lines)

    cdef IdentedLexer lexer = IdentedLexer(get_symbol_function,'#ignore#\n?')
    lexer.set_text_sanitize_function(sanitaze_text)
    lexer._enum_type = TokenTypeEnum

    lexer.add_token_regex(0,TokenTypeEnum.NUMBER, r'\d+(\.\d+)?')
    lexer.add_token_regex(1,TokenTypeEnum.BOOLEAN, 'true|false')
    lexer.add_token_regex(2,TokenTypeEnum.VARIABLE, r'[a-zA-Z_]\w*')
    lexer.add_token_regex(3,TokenTypeEnum.IDENTATION, '    |\t')
    lexer.add_token_regex(4,TokenTypeEnum.NEWLINE, '\n')
    lexer.add_token_regex(5,TokenTypeEnum.SYMBOL, r'\-|:|\[|\]')
    lexer.add_token_regex(6,TokenTypeEnum.STRING, '".*"')
    lexer.add_token_regex(7,TokenTypeEnum.WHITESPACEMARKER, '#ignore#\n')
    lexer.add_token_regex(8,TokenTypeEnum.SINGLEWHITESPACE, ' ')

    lexer.set_ident(TokenTypeEnum.IDENTATION)
    lexer.set_indent_symbol(indent)
    lexer.set_dedent_symbol(dedent)
    lexer.set_eof_token('$',TokenTypeEnum.SYMBOL)
    ```

> ### Using the Lexer

```python
lexer.load_text("x = 10 + 2")
for token in lexer.tokens:
    print(token.type, token.text, token.symbol)
# Output:
# VARIABLE x variable
# OPERATOR = eq
# NUMBER 10 number
# OPERATOR + plus
# NUMBER 2 number
# SYMBOL $ END_SYMBOL
```

## Summary

The `lexer` module is the workhorse of tokenization in PyLGEN. It combines the power of the [`regex`](../regex/regex.md) engine and the [`automaton`](../automaton/intro.md) module to provide a robust, flexible, and efficient scanner. The separation between `BaseLexer` (scanning engine) and `Lexer` (user interface) allows for both low‑level control and high‑level convenience. With this module, you can define the lexical structure of any language in just a few lines of code, and the generated scanner will be both correct and fast. The next step is to combine it with the parser to build a complete language processor.