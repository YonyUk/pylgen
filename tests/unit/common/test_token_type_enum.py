from pylgen.common.enums import TokenType

class TokenTypeEnum(TokenType):
    TOKEN = 'TOKEN'

class TestTokenTypeEnum:

    def test_token_type_enum_members(self):

        assert hasattr(TokenTypeEnum,'INVALID_TOKEN')