from typing import Set
from common.types cimport Symbol
from parser.lr0_parser cimport LR0State,LR0Item

cdef class LALRState(LR0State):

    def __init__(self, items: Set[LR0Item], index: int = 0):
        super().__init__(items, index) # type:ignore
        self._lookaheads = set()
    
    @property
    def lookaheads(self) -> Set[Symbol]:
        return self._lookaheads