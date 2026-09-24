from pylgen.common.enums import TokenType

class TokenTypeEnum(TokenType):

    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    KEYWORD = 'KEYWORD'
    VARIABLE = 'VARIABLE'
    JUMPLINE = 'JUMPLINE'
    COMMENT = 'COMMENT'
    EOF = 'EOF'