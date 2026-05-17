from common.types cimport Symbol

cdef class Production:
    cdef Symbol _head
    cdef list[Symbol] _production
    cdef str _id

cdef class ProductionsSet:
    cdef dict[str,list[Symbol]] _productions