from pylgen.common.enums import TokenType
from pylgen.common.types import Symbol
from pylgen.lexer.lexer import Lexer
from pylgen.analysis.lexical import LexicalRule
from .grammar_symbols import (
    END_SYMBOL,
    number,
    variable
)

# Enumeration of token types of our language
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