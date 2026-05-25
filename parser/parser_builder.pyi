from typing import Set

from common.types import Symbol
from grammar.grammar import Grammar
from .lr0_parser import LR0Item,LR0State
from .lalr_parser import LALRItem

class ParserBuilder:

    @staticmethod
    def clear_cache() -> None: ...

    @staticmethod
    def clousure_lr0(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]: ...
    
    @staticmethod
    def clousure_lalr(items:Set[LALRItem],g:Grammar) -> Set[LALRItem]: ...

    @staticmethod
    def goto_lr0(items:Set[LR0Item],x:Symbol,g:Grammar) -> Set[LR0Item]: ...

    @staticmethod
    def goto_lalr(items:Set[LALRItem],x:Symbol,g:Grammar) -> Set[LALRItem]: ...

    @staticmethod
    def get_canonical_lr0_states(g:Grammar) -> Set[LR0State]: ...

    @staticmethod
    def get_kernel_items(state:LR0State, g:Grammar) -> Set[LR0Item]: ...