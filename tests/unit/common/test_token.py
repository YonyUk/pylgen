from pylgen.common.types import Symbol,Token
from pylgen.common.enums import TokenType

import pytest

class TokenTypeEnumForTest(TokenType):
    GARBAGE = 'GARBAGE'

class TestToken:

    def test_token_creation(self):

        n = Symbol('n',True)
        t = Token('12',TokenTypeEnumForTest.GARBAGE,n,1,0)

        assert t.text == '12'
        assert t.symbol == n
        assert t.type == TokenTypeEnumForTest.GARBAGE
        assert t.start_position == (1,0)
        assert t.end_position == (1,2)
    
    def test_token_creation_fail(self):
        n = Symbol('n',True)
        with pytest.raises(ValueError,match='type_ parameter must be a subclass of TokenType'):
            t = Token('12','GARBAGE',n,1,0) # type:ignore