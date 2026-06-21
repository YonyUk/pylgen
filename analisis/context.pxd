cdef class Context:

    cdef list[str] _stack
    cdef dict[str,object] _local_scope
    cdef dict[str,object] _global_scope

    cpdef void add_to_scope(self,str address,object value)
    cpdef bint check_scope(self,str address)
    cpdef object get_value(self,str address)
    cpdef void clear(self)