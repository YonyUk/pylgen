from common.types cimport Symbol

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