cdef class Error:
    cdef object _type
    cdef int _line
    cdef int _column
    cdef str _msg

cdef class LexicError(Error):
    pass

cdef class SintaxError(Error):
    pass

cdef class SemanticError(Error):
    pass