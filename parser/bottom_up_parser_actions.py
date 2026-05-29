from enum import StrEnum

class BottomUpParserAction(StrEnum):

    ACCEPT = 'ACCEPT'
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'