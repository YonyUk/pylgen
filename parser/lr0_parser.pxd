from common.types cimport Symbol

cdef class LR0Item:
    cdef Symbol _head
    cdef list[Symbol] _left
    cdef list[Symbol] _right