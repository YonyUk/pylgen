from typing import Dict, Set, Tuple

from ..common.types import Symbol
from ..grammar.grammar import Grammar,Production,AttributedGrammar
from .lr0_parser import LR0Item,LR0State
from .lalr_parser import LALRItem,LALRState
from .parser import Parser
from .parser_type import ParserType

class ParserBuildingConflictException(Exception):
    pass

class LALRParserBuildingConflictException(ParserBuildingConflictException):

    def __init__(self,state:LALRState,symbol:Symbol): ...
    
    @property
    def state(self) -> LALRState: ...
    
    @property
    def symbol(self) -> Symbol: ...

class LALRShiftReduceConflictException(LALRParserBuildingConflictException):
    
    def __init__(self, state: LALRState, symbol: Symbol,next_state:LALRState,production:Production): ...
    
    @property
    def next_state(self) -> LALRState: ...
    
    @property
    def production(self) -> Production: ...

class LALRReduceReduceConflictException(LALRParserBuildingConflictException):

    def __init__(self, state: LALRState, symbol: Symbol,old:Production,new_:Production): ...
    
    @property
    def old(self) -> Production: ...
    
    @property
    def new_(self) -> Production: ...

class ParserBuilder:

    @staticmethod
    def clear_cache() -> None: ...

    @staticmethod
    def closure_lr0(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]: ...
    
    @staticmethod
    def closure_lalr(items:Set[LALRItem],g:Grammar) -> Set[LALRItem]: ...

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
    def build_lookaheads_propagation_edges(g:Grammar) -> Tuple[Dict[LR0State,Dict[Tuple[LR0Item,Symbol],Tuple[LR0State,LR0Item]]],Set[LR0State]]: ...

    @staticmethod
    def get_canonical_lalr_states(g:Grammar) -> Set[LALRState]: ...

    @staticmethod
    def get_goto_action_tables_lalr(g:Grammar) -> Tuple[Dict[Tuple[LALRState,Symbol],LALRState],dict[Tuple[LALRState,Symbol],Tuple[str,LALRState | Production]]]: ...

    @staticmethod
    def build_parser(g:Grammar,type_:ParserType) -> Parser: ...

    @staticmethod
    def build_parser_from_attributed(g:AttributedGrammar,type_:ParserType) -> Parser: ...

    @staticmethod
    def get_propagated_lookaheads(g:Grammar) -> Dict[Tuple[LR0State,LR0Item],Set[Symbol]]: ...