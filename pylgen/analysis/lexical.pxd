from ..common.types cimport Token,LexicalError

cdef class LexicalRule:
    cdef str _msg
    cpdef bool _check(self,str text)
    cpdef LexicalError check(self,Token token)