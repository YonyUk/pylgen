from common.types import Symbol
from common.enums import TokenType
from lexer.lexer import Lexer
from automaton import DFA

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    KEYWORD = 'KEYWORD'
    VARIABLE = 'VARIABLE'

class TestLexer:
    
    def test_lexer_tokens_adding(self):

        def valid_get_symbol(t:TokenTypeEnum,tx:str) -> Symbol:
            return Symbol('$',True)
        
        lexer = Lexer(valid_get_symbol,DFA('0','0',{''}))

        lexer[0,TokenTypeEnum.NUMBER] = 'hello'