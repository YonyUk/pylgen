cdef class Symbol:

    cdef str _symbol
    cdef bint _is_terminal
    cdef bint _is_epsilon