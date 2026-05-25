from typing import Set

from common.types import Symbol
from grammar.grammar import Grammar
from .lr0_parser import LR0Item,LR0State

class ParserBuilder:

    @staticmethod
    def clear_cache() -> None: ...

    @staticmethod
    def clousure(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]: ...

    @staticmethod
    def goto(items:Set[LR0Item],x:Symbol,g:Grammar) -> Set[LR0Item]: ...

    @staticmethod
    def get_canonical_lr0_states(g:Grammar) -> Set[LR0State]: ...

    @staticmethod
    def get_kernel_items(state:LR0State, start:Symbol) -> Set[LR0Item]: ...