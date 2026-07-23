from pylgen.common.types import Symbol
from pylgen.common.enums import TokenType
from pylgen.lexer.lexer import Lexer

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    KEYWORD = 'KEYWORD'
    VARIABLE = 'VARIABLE'

class TestLexer:
    
    def test_lexer_tokens_adding(self):

        def valid_get_symbol(t:TokenTypeEnum,tx:str) -> Symbol:
            return Symbol('$',True)
        
        lexer = Lexer(valid_get_symbol,'nada')

        lexer[0,TokenTypeEnum.NUMBER] = 'hello'