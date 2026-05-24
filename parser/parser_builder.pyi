from typing import Set

from grammar.grammar import Grammar
from .lr0_parser import LR0Item

class ParserBuilder:

    @staticmethod
    def clear_cache() -> None: ...

    @staticmethod
    def clousure(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]: ...