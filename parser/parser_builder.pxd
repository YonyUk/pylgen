from grammar.grammar cimport Grammar
from common.types cimport Symbol
from .lr0_parser cimport LR0Item,LR0State

cdef class ParserBuilder:
    pass

cdef set[LR0Item] _clousure(set[LR0Item] items,Grammar g)
cdef set[LR0Item] _goto(set[LR0Item] items,Symbol x,Grammar g)
cdef set[LR0State] _get_canonical_lr0_states(Grammar g)