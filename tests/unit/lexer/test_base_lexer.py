import pytest

from lexer.lexer import BaseLexer,LexerNotInitializedException,LexerNotTokensProvidedException

class TestBaseLexer:

    def test_base_lexer_creation(self):
        lexer = BaseLexer(None) # type:ignore

        with pytest.raises(LexerNotTokensProvidedException):
            lexer.initialize()
        
        with pytest.raises(LexerNotTokensProvidedException):
            for _ in lexer.tokens:
                pass
        
        with pytest.raises(LexerNotInitializedException):
            dfa = lexer.dfa