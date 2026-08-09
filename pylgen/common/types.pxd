from ..analysis.error cimport Error

cdef class Symbol:

    cdef int _hash
    cdef str _symbol
    cdef bint _is_terminal
    cdef bint _is_epsilon

cdef class AST:
    cdef Symbol _symbol
    cdef int _line
    cdef int _column
    cdef bint _is_error

    cpdef list[AST] children(self)

cdef class ErrorAST(AST):
    cdef Error _error

cdef class ASTListView:
    cdef list[AST] _data
    cdef int _start
    cdef int _end
    cdef AST _get(self,int idx)
    cdef int _size(self)

cdef class Token(AST):
    cdef str _text
    cdef object _type