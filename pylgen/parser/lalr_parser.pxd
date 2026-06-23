from ..common.types cimport Symbol
from .lr0_parser cimport LR0Item

cdef class LALRItem(LR0Item):
    cdef set[Symbol] _lookaheads

cdef class LALRState:
    cdef set[LALRItem] _items
    cdef str _id
    cdef int _index