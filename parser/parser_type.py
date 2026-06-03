from enum import StrEnum

class ParserType(StrEnum):
    LL1 = 'LL1'
    SLR = 'SLR'
    LALR1 = 'LALR1'