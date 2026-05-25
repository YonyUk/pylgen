from grammar.grammar cimport Grammar
from common.types cimport Symbol
from .lr0_parser cimport LR0Item,LR0State
from .lalr_parser cimport LALRState,LALRItem

cdef class ParserBuilder:
    pass

cdef set[LR0Item] _clousure_lr0(set[LR0Item] items,Grammar g)
cdef set[LALRState] _clousure_lalr(set[LALRItem] items,Grammar g)
cdef set[LR0Item] _goto_lr0(set[LR0Item] items,Symbol x,Grammar g)
# cdef set[LALRItem] _goto_lalr(set[LALRItem] items,Symbol x,Grammar g)
cdef set[LR0State] _get_canonical_lr0_states(Grammar g)
cdef set[LR0Item] _get_kernel_items(LR0State state,Grammar g)
cdef set[LALRState] _get_lalr_states(Grammar g)