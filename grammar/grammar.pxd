from common.types cimport Symbol

cdef class SymbolNotPresentInGrammarException(Exception):
    cdef str _msg

cdef class Production:
    cdef Symbol _head
    cdef list[Symbol] _production
    cdef str _id

cdef class ProductionsSet:
    cdef dict[str,list[Symbol]] _productions
    cdef list[Symbol] _last_production_added

cdef class Grammar:
    cdef Symbol _start_symbol
    cdef Symbol _end_symbol
    cdef set[Symbol] _terminals,_non_terminals
    cdef dict[Symbol,set[Symbol]] _follows,_firsts
    cdef dict[Symbol,ProductionsSet] _productions
    cdef dict[Symbol,set[Production]] _productions_by_symbol
    cdef bint _initialized
    cdef Symbol _epsilon
    cdef set[Production] _productions_cache

    cdef bint _derives_in_epsilon(self,Symbol symbol)
    cdef void _make_firsts(self)
    # cdef void _make_follows(self,str end_symbol)

    cpdef set[Symbol] first(self,list[Symbol] production)