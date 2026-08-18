from pylgen.common.types import Symbol
from pylgen.common.enums import TokenType
from pylgen.lexer.lexer import IdentedLexer

from enum import StrEnum

import pytest

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'

class MyTokenTypeEnum(StrEnum):
    NUMBER = 'NUMBER'

class TestIdentedLexer:

    def test_set_ident(self):

        def valid_get_symbol(t:TokenTypeEnum,tx:str) -> Symbol:
            return Symbol('$',True)

        lexer = IdentedLexer(valid_get_symbol,'nada')

        lexer.set_ident(TokenTypeEnum.NUMBER)

        with pytest.raises(ValueError,match=f'ident_type must be a member of {TokenTypeEnum}'):
            lexer.set_ident(MyTokenTypeEnum)