import pytest

from automaton import DFA
from common.types import Symbol
from lexer.lexer import BaseLexer,LexerNotInitializedException,LexerNotTokensProvidedException

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