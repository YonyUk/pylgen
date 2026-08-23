from enum import StrEnum

class ParserType(StrEnum):
    LL1 = 'LL1'
    SLR = 'SLR'
    LR1 = 'LR1'
    LALR1 = 'LALR1'