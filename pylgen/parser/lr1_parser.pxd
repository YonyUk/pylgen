from ..common.types cimport Symbol
from .lr0_parser cimport LR0Item

cdef class LR1Item(LR0Item):
    cdef Symbol _lookahead

cdef class LR1State:
    cdef set[LR1Item] _items
    cdef str _id
    cdef int _index
    cdef int _hash