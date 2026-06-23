from .error cimport SemanticError,RuntimeError
from ..common.types cimport AST

cdef class Context:

    cdef list[str] _stack
    cdef list[SemanticError] _errors

    cpdef list[RuntimeError] get_runtime_errors(self)
    cpdef void push_trace(self,str trace)
    cpdef void pop_trace(self)
    cpdef void push_new_scope(self)
    cpdef void pop_scope(self)
    cpdef void reset(self)
    cpdef void clear_errors(self)
    cpdef void clear_semantic_errors(self)
    cpdef void clear_runtimes_errors(self)
    cpdef void add_semantic_error(self,SemanticError error)
    cpdef void add_runtime_error(self,AST ast,RuntimeError error)