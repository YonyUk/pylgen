cdef class Error:
    cdef object _type
    cdef int _line
    cdef int _column
    cdef str _msg

cdef class LexicalError(Error):
    pass

cdef class SyntaxError(Error):
    pass

cdef class SemanticError(Error):
    pass

cdef class RuntimeError:
    cdef list[str] _stack_trace
    cdef int _line
    cdef int _column
    cdef str _msg