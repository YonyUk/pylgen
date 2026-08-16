# Step 1: Build the lexer

The lexer converts source code into a stream of tokens. We define token types, regular expressions, and optional validation rules.

## Define token types

First, we declare the token types that our language will use:

```python
from pylgen.common.enums import TokenType

# Enumeration of token types of our language
class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    VARIABLE = 'VARIABLE'
    KEYWORD = 'KEYWORD'

```

## Define the mapping function

To connect the lexer's output with the grammar rules, we need a mapping function that translates each token (type + lexeme) into a grammar symbol. This function bridges the gap between the lexer's raw token patterns and the grammar's terminal symbols, allowing the lexer to remain generic while precisely mapping each recognized token to the specific symbol the parser expects.

!!! note
    A detailed explanation of context‑free grammars, terminals, non‑terminals, and the parsing process will be provided in the [grammar](../api/grammar/intro.md) and [parser](../api/parser/parser.md) sections later. For now, we’ll focus on the implementation.

```python
from pylgen.common.types import Symbol
# this will be defined later
from .grammar_symbols import (
    END_SYMBOL,
    number,
    variable
)

# ...

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.KEYWORD:
        return Symbol(tx,True)
    return Symbol(tx,True)
```

!!! important
    It is important that the mapping function is fully annotated so that the lexer can infer the enum type; otherwise, the lexer may fail.

Here, we receive a token type and its lexeme (tx), and return the corresponding grammar symbol.

## Creating the lexer

Now we can instantiate the lexer. It takes our mapping function and a regular expression that defines which tokens (e.g., whitespace, new lines, comments) should be discarded. We also explicitly define the end‑of‑file token to mark the end of the input stream.

```python
from pylgen.lexer.lexer import Lexer

# ...

lexer = Lexer(get_symbol_function,'\n|\t| ')
lexer.set_eof_token(END_SYMBOL,TokenTypeEnum.SYMBOL)
```

## Defining tokens

Next, we associate regular expression patterns with their corresponding token types, ordered by priority.

!!! info
    Lower numbers indicate higher priority.

```python
# ...

lexer[0,TokenTypeEnum.NUMBER] = '\\d+(\\.\\d+)?'
lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%|='
lexer[3,TokenTypeEnum.KEYWORD] = 'exit|clear'
lexer[4,TokenTypeEnum.VARIABLE] = '\\w+'
```

## Lexical rules

Optionally, we can add validation rules to enforce lexical constraints beyond simple pattern matching. For example, we can ensure numbers are properly formatted and variable names do not start with a digit.

```python
from pylgen.analysis.lexical import LexicalRule

# ...

class NumberLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')
    
    def _check(self, text: str):
        if '.' in text:
            return str(float(text)) == text
        return str(int(text)) == text

class VariableLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('variables names can\'t star with a number')
    
    def _check(self, text: str):
        return not text[0].isdigit()

# ...

lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicalRule())
lexer.add_rule(TokenTypeEnum.VARIABLE,VariableLexicalRule())
```

## Recap

Putting it all together, here is the complete `lexer.py` module:

File: `lexer.py`
```python
from pylgen.lexer.lexer import Lexer
from pylgen.common.types import Symbol
from pylgen.common.enums import TokenType
from pylgen.analysis.lexical import LexicalRule
from .grammar_symbols import END_SYMBOL
from .grammar_symbols import (
    END_SYMBOL,
    number,
    variable
)

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    VARIABLE = 'VARIABLE'
    KEYWORD = 'KEYWORD'

class NumberLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')
    
    def _check(self, text: str):
        if '.' in text:
            return str(float(text)) == text
        return str(int(text)) == text

class VariableLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('variables names can\'t star with a number')
    
    def _check(self, text: str):
        return not text[0].isdigit()

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.KEYWORD:
        return Symbol(tx,True)
    return Symbol(tx,True)

lexer = Lexer(get_symbol_function,'\n|\t| ')
lexer.set_eof_token(END_SYMBOL,TokenTypeEnum.SYMBOL)
lexer[0,TokenTypeEnum.NUMBER] = '\\d+(\\.\\d+)?'
lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%|='
lexer[3,TokenTypeEnum.KEYWORD] = 'exit|clear'
lexer[4,TokenTypeEnum.VARIABLE] = '\\w+'

lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicalRule())
lexer.add_rule(TokenTypeEnum.VARIABLE,VariableLexicalRule())
```

Our lexer is now ready to tokenize input. Next, we’ll move on to defining the grammar and building the parser.