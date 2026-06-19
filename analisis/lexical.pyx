from .error cimport LexicError
from common.types cimport Token

cdef class LexicRule:
    
    def __init__(self,str msg) -> None:
        self._msg = msg
    
    cpdef bool _check(self,str text):
        raise NotImplementedError()

    cpdef LexicError check(self,Token token):
        if not self._check(token._text):
            return LexicError(self._msg,token._line,token._column) # type:ignore