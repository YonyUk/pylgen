from ..common.types cimport Token,LexicalError

cdef class LexicalRule:
    
    def __init__(self,str msg) -> None:
        self._msg = msg
    
    cpdef bool _check(self,str text):
        raise NotImplementedError()

    cpdef LexicalError check(self,Token token):
        if not self._check(token._text):
            return LexicalError(self._msg,token._start_line,token._start_column,token._end_line,token._end_column) # type:ignore