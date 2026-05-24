from common.types import Symbol,Token
from common.enums import TokenType

class TestToken:

    def test_token_creation(self):

        n = Symbol('n',True)
        t = Token('12',TokenType.GARBAGE,n,1,0)

        assert t.text == '12'
        assert t.symbol == n
        assert t.type == TokenType.GARBAGE
        assert t.line == 1
        assert t.column == 0