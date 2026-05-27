from typing import Dict, Set, Tuple

from common.types import Symbol
from common.table import Table
from grammar.grammar import Grammar
from .lr0_parser import LR0Item,LR0State
from .lalr_parser import LALRItem,LALRState

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
    def get_kernel_items_lr0(state:LR0State, g:Grammar) -> Set[LR0Item]: ...

    @staticmethod
    def get_kernel_items_lalr(state:LALRState, g:Grammar) -> Set[LALRItem]: ...

    @staticmethod
    def build_lookaheads_propagation_edges(initial_item:LALRItem,g:Grammar) -> Tuple[Dict[Tuple[Symbol,tuple,tuple],Dict[Symbol,Tuple[Symbol,tuple,tuple]]],Set[LALRItem]]: ...

    @staticmethod
    def get_canonical_lalr_states(g:Grammar) -> set[LALRState]: ...