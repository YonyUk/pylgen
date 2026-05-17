from common.types cimport Symbol

cdef class AttributedProduction:
    cdef Symbol _head
    cdef list[Symbol] _production
    cdef object _reductor