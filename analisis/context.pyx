cdef class Context:

    def __init__(self,dict[str,object] global_scope = {},dict[str,object] local_scope = {}) -> None:
        self._global_scope = global_scope
        self._local_scope = local_scope
        self._stack = []

    cpdef void add_to_scope(self,str address,object value):
        self._local_scope[address] = value
    
    cpdef bint check_scope(self,str address):
        return address in self._local_scope or address in self._global_scope # type:ignore
    
    cpdef object get_value(self,str address):
        if not address in self._local_scope:
            return self._global_scope[address]
        return self._local_scope[address]
    
    cpdef void clear(self):
        self._stack.clear()
        self._global_scope.clear()
        self._local_scope.clear()