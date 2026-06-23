from .error cimport LexicError
from ..common.types cimport Token

cdef class LexicRule:
    cdef str _msg
    cpdef bool _check(self,str text)
    cpdef LexicError check(self,Token token)