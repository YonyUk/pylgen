from common.types import Symbol,Token
from common.enums import TokenType

class TokenTypeEnumForTest(TokenType):
    GARBAGE = 'GARBAGE'

class TestToken:

    def test_token_creation(self):

        n = Symbol('n',True)
        t = Token('12',f'{TokenTypeEnumForTest.GARBAGE}',n,1,0)

        assert t.text == '12'
        assert t.symbol == n
        assert t.type == TokenTypeEnumForTest.GARBAGE
        assert t.line == 1
        assert t.column == 0