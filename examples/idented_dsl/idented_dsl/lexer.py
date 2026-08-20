from pylgen.common.enums import TokenType
from pylgen.common.types import Symbol
from pylgen.lexer.lexer import IdentedLexer

from .grammar_symbols import (
    newline,
    number,
    boolean,
    string,
    indent,
    dedent,
    variable
)

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