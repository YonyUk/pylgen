from common.enums import TokenType

class ReTokenType(TokenType):
    CHAR = 'CHAR'
    SYMBOL = 'SYMBOL'
    CONSTANT_RE = 'CONSTANT_RE'
    ESCAPE_CHAR = 'ESCAPE_CHAR'
    OPERATOR = 'OPERATOR'
    NUMBER = 'NUMBER'