from pylgen.analisis.error import LexicError
from pylgen.analisis.error_type import ErrorType
from pylgen.analisis.lexical import LexicRule
from pylgen.common.types import Token,Symbol
from pylgen.common.enums import TokenType

import pytest

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'

class Rule(LexicRule):

    def __init__(self) -> None:
        super().__init__('numbers must star with only one 0')
    
    def _check(self, text: str):
        return str(int(text)) == text

class TestLexicRule:

    def test_rule_creation(self):

        rule = LexicRule('error')
        token = Token('10',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)

        with pytest.raises(NotImplementedError):
            rule.check(token)
    
    def test_rule(self):
        rule = Rule()
        token = Token('10',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)
        assert rule.check(token) is None
        token = Token('010',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)
        error = rule.check(token)
        assert isinstance(error,LexicError)
        assert error.type == ErrorType.LEXIC
        assert error.line == token.line
        assert error.column == token.column
        assert 'numbers must star with only one 0' in error.message