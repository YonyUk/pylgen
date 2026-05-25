from common.types cimport Symbol

cdef class LR0Item:
    cdef Symbol _head
    cdef list[Symbol] _left
    cdef list[Symbol] _right

cdef class LR0State:
    cdef set[LR0Item] _items
    cdef str _id
    cdef int _index