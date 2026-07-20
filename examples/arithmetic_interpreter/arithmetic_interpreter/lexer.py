from typing import Iterable

from pylgen.automaton import DFA
from pylgen.lexer.lexer import Lexer
from pylgen.common.types import Symbol,Token
from pylgen.common.enums import TokenType
from pylgen.analysis.lexical import LexicalRule
from .grammar_symbols import (
    number,
    variable
)

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    VARIABLE = 'VARIABLE'
    KEYWORD = 'KEYWORD'

class NumberLexicRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')
    
    def _check(self, text: str):
        if '.' in text:
            return str(float(text)) == text
        return str(int(text)) == text

class VariableLexicRule(LexicalRule):

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

def get_tokens(end_symbol:Symbol,tokens:Iterable[Token]):
    line = 0
    column = 0
    for token in tokens:
        line = token.line
        column = token.column
        yield token
    yield Token(end_symbol.symbol,TokenTypeEnum.SYMBOL,end_symbol,line,column + 1)

ignore_dfa = DFA('start','start',{' ','\n','\t'},True)
ignore_dfa += ignore_dfa.start_state,' ',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\n',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\t',ignore_dfa.start_state

lexer = Lexer(get_symbol_function,ignore_dfa)
lexer[0,TokenTypeEnum.NUMBER] = '\\d+|\\d+\\.\\d+'
lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%|='
lexer[3,TokenTypeEnum.KEYWORD] = 'exit|clear'
lexer[4,TokenTypeEnum.VARIABLE] = '\\w+'

lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicRule())
lexer.add_rule(TokenTypeEnum.VARIABLE,VariableLexicRule())