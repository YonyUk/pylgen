from typing import Any
from enum import StrEnum
import pytest

from automaton import DFA
from common.types import Symbol
from common.enums import TokenType
from lexer.lexer import BaseLexer,LexerNotInitializedException,LexerNotTokensProvidedException

class MyInvalidTokenType(StrEnum):
    T1 = 'T1'

class MyValidTokenType(TokenType):
    T1 = 'T1'

class TestBaseLexer:

    def test_base_lexer_creation(self):
        lexer = BaseLexer(lambda t,tx:Symbol('$'),DFA('0','0',{''}))

        with pytest.raises(LexerNotTokensProvidedException):
            lexer.initialize()
        
        with pytest.raises(LexerNotTokensProvidedException):
            for _ in lexer.tokens:
                pass
        
        with pytest.raises(LexerNotInitializedException):
            dfa = lexer.dfa
        
        with pytest.raises(ValueError):
            lexer[0,'A'] = DFA('nada','nada',set())
    
    def test_base_lexer_creation_failed(self):
        
        def invalid_get_symbol_1(t:Any,tx:Any) -> Any:
            return Symbol('$',True)
        
        def invalid_get_symbol_2(t:MyInvalidTokenType,tx:Any):
            return Symbol('$',True)

        def invalid_get_symbol_3(t:MyValidTokenType,tx:Any):
            return Symbol('$',True)
        
        def invalid_get_symbol_4(t:MyInvalidTokenType,tx:str):
            return Symbol('$',True)

        def invalid_get_symbol_5(t:Any,tx:str):
            return Symbol('$',True)

        def valid_get_symbol(t:MyValidTokenType,tx:str):
            return Symbol('$',True)

        with pytest.raises(ValueError,match='get_symbol_function can not be None'):
            lexer = BaseLexer(None,DFA('0','0',{''})) # type:ignore
        
        with pytest.raises(ValueError,match='Invalid signature of function get_symbol_function'):
            lexer = BaseLexer(invalid_get_symbol_1,DFA('0','0',{''}))
        
        with pytest.raises(ValueError,match='Invalid signature of function get_symbol_function'):
            lexer = BaseLexer(invalid_get_symbol_2,DFA('0','0',{''}))

        with pytest.raises(ValueError,match='Invalid signature of function get_symbol_function'):
            lexer = BaseLexer(invalid_get_symbol_3,DFA('0','0',{''}))

        with pytest.raises(ValueError,match='Invalid signature of function get_symbol_function'):
            lexer = BaseLexer(invalid_get_symbol_4,DFA('0','0',{''}))

        with pytest.raises(ValueError,match='Invalid signature of function get_symbol_function'):
            lexer = BaseLexer(invalid_get_symbol_5,DFA('0','0',{''}))
        
        lexer = BaseLexer(valid_get_symbol,DFA('0','0',{''}))
    
    def test_base_lexer_tokens_adding(self):

        def valid_get_symbol(t:MyValidTokenType,tx:str):
            return Symbol('$',True)
        
        lexer = BaseLexer(valid_get_symbol,DFA('0','0',{''}))

        with pytest.raises(ValueError,match=f'type_ must be a member of {MyValidTokenType}'):
            lexer[0,MyInvalidTokenType.T1] = DFA('0','0',{''})
        
        lexer[0,MyValidTokenType.T1] = DFA('0','0',{''})