cdef class Symbol:

    cdef int _hash
    cdef str _symbol
    cdef bint _is_terminal
    cdef bint _is_epsilon

cdef class AST:
    cdef Symbol _symbol
    cdef int _line
    cdef int _column

    cpdef list[AST] children(self)

cdef class ASTListView:
    cdef list[AST] _data
    cdef int _start
    cdef int _end

cdef class Token(AST):
    cdef str _text
    cdef object _type