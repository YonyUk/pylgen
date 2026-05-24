from typing import Set
from common.types import Symbol
from parser.lr0_parser import LR0Item,LR0State

class LALRState(LR0State):

    def __init__(self, items: Set[LR0Item], index: int = 0): ...    
    
    @property
    def lookaheads(self) -> Set[Symbol]: ...