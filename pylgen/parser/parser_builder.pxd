from ..grammar.grammar cimport Grammar,AttributedGrammar,Production
from ..common.types cimport Symbol
from .parser cimport BottomUpParser
from .lr0_parser cimport LR0Item,LR0State
from .lalr_parser cimport LALRState,LALRItem

cdef class ParserBuildingConflictException(Exception):
    pass

cdef class LALRParserBuildingConflictException(ParserBuildingConflictException):
    cdef LALRState _state
    cdef Symbol _symbol
    cdef LALRState _next
    cdef Production _production

cdef class LALRShiftReduceConflictException(LALRParserBuildingConflictException):
    pass

cdef class LALRReduceReduceConflictException(LALRParserBuildingConflictException):
    cdef Production _old
    cdef Production _new

cdef class ParserBuilder:
    pass

cdef set[LR0Item] _closure_lr0(set[LR0Item] items,Grammar g)
cdef set[LALRState] _closure_lalr(set[LALRItem] items,Grammar g)
cdef set[LR0Item] _goto_lr0(set[LR0Item] items,Symbol x,Grammar g)
cdef set[LALRItem] _goto_lalr(set[LALRItem] items,Symbol x,Grammar g)
cdef set[LR0State] _get_canonical_lr0_states(Grammar g)
cdef set[LR0Item] _get_kernel_items_lr0(LR0State state,Grammar g)
cdef set[LALRItem] _get_kernel_items_lalr(LALRState state,Grammar g)
cdef tuple[dict[LR0State,dict[tuple[LR0Item,Symbol],set[LR0Item]]],set[LR0State]] _build_lookaheads_propagation_edges(Grammar g)
cdef tuple[set[LALRState],dict[tuple[LR0State,LR0Item],set[Symbol]]] _get_canonical_lalr_states(Grammar g)
cdef tuple[dict[tuple[LALRState,Symbol],LALRState],dict[tuple[LALRState,Symbol],tuple]] _get_goto_action_tables_lalr(Grammar g)
cdef dict[tuple[str,Symbol],str] _plain_goto_table_lalr(dict[tuple[LALRState,Symbol],LALRState] table)
cdef dict[tuple[str,Symbol],tuple[str,object]] _plain_action_table_lalr(dict[tuple[LALRState,Symbol],tuple] table)
cdef BottomUpParser _build_lalr_parser(Grammar g)
cdef BottomUpParser _build_lalr_parser_from_attributed(AttributedGrammar g)