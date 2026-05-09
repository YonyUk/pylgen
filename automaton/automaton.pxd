cdef class State:
    cdef bint _is_accept
    cdef object _value
    cdef str _id