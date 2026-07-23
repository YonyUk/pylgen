from pylgen.analysis.error import LexicalError
from pylgen.analysis.error_type import ErrorType
from pylgen.analysis.lexical import LexicalRule
from pylgen.common.types import Token,Symbol
from pylgen.common.enums import TokenType

import pytest

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'

class Rule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('numbers must star with only one 0')
    
    def _check(self, text: str):
        return str(int(text)) == text

class TestLexicalRule:

    def test_rule_creation(self):

        rule = LexicalRule('error')
        token = Token('10',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)

        with pytest.raises(NotImplementedError):
            rule.check(token)
    
    def test_rule(self):
        rule = Rule()
        token = Token('10',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)
        assert rule.check(token) is None
        token = Token('010',TokenTypeEnum.NUMBER,Symbol('n',True),1,1)
        error = rule.check(token)
        assert isinstance(error,LexicalError)
        assert error.type == ErrorType.LEXICAL
        assert error.line == token.line
        assert error.column == token.column
        assert 'numbers must star with only one 0' in error.message