from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production

cdef class ReductorWrapper:
    cdef object _func
    
cdef class Parser:
    cdef AST _ast

    cdef void _try_parse(self,Token token)

cdef class BottomUpParser(Parser):
    cdef dict[Production,ReductorWrapper] _reductor_by_production
    cdef dict[tuple[str,Symbol],str] _goto_table
    cdef dict[tuple[str,Symbol],tuple[str,object]] _action_table

    cdef void _set_reductor(self,Production production,object reductor)