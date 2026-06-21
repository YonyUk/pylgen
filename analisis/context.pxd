from .error cimport SemanticError,RuntimeError

cdef class Context:

    cdef list[str] _stack
    cdef dict[str,object] _local_scope
    cdef dict[str,object] _global_scope
    cdef list[SemanticError] _errors
    cdef list[RuntimeError] _runtime_errors

    cpdef void add_to_scope(self,str address,object value)
    cpdef bint check_scope(self,str address)
    cpdef object get_value(self,str address)
    cpdef void clear(self)
    cpdef void add_error(self,SemanticError error)
    cpdef void add_runtime_error(self,RuntimeError error)