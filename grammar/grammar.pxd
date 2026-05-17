from common.types cimport Symbol

cdef class GrammarNotInitializedException(Exception):
    pass

cdef class SymbolNotPresentInGrammarException(Exception):
    cdef str _msg

cdef class Production:
    cdef Symbol _head
    cdef list[Symbol] _production
    cdef str _id

cdef class ProductionsSet:
    cdef set[Symbol] _non_terminals,_terminals
    cdef dict[str,list[Symbol]] _productions

cdef class Grammar:
    cdef Symbol _start_symbol
    cdef set[Symbol] _terminals,_non_terminals
    cdef dict[Symbol,set[Symbol]] _follows,_firsts
    cdef dict[Symbol,ProductionsSet] _productions
    cdef bint _initialized
    cdef Symbol _epsilon

    cdef bint _derives_in_epsilon(self,Symbol symbol)
    cdef void _make_firsts(self)

    cpdef void initialize(self,str end_symbol)
    cpdef set[Symbol] first(self,list[Symbol] production)