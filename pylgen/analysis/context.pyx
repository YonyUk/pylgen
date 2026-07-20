from .error cimport SemanticError,RuntimeError
from ..common.types cimport AST

cdef class Context:
    '''
    base Context class

    methods that must be implemented

    get_runtime_errors(self) -> List[RuntimeError]
    push_new_scope(self) -> None
    pop_scope(self) -> None
    clear_runtime_errors(self) -> None
    add_runtime_error(self,ast:AST,error:RuntimeError)
    '''

    def __init__(self) -> None:
        self._stack = []
        self._errors = []

    @property
    def errors(self) -> list[SemanticError | RuntimeError]:
        return self._errors.copy() + self.get_runtime_errors().copy() # type:ignore

    @property
    def stack_trace(self) -> list[str]:
        return self._stack.copy()

    cpdef void push_trace(self,str trace):
        self._stack.append(trace)
    
    cpdef void pop_trace(self):
        self._stack.pop()
    
    cpdef void push_new_scope(self):
        '''
        Description:
            Push a new scope into the context. This can overwrite the current scope, but doesn't hide it
        '''
        raise NotImplementedError()
    
    cpdef void pop_scope(self):
        '''
        Descriptiom:
            Pops the current scope
        '''
        raise NotImplementedError()

    cpdef void clear_runtime_errors(self):
        '''
        Description:
            Clear all the runtime errors
        '''
        raise NotImplementedError()

    cpdef list[RuntimeError] get_runtime_errors(self):
        '''
        Returns:
            List[RuntimeError]: All the runtime errors detected
        '''
        raise NotImplementedError()

    cpdef void clear_semantic_errors(self):
        '''
        Description:
            Clear all the semantic errors
        '''
        self._errors.clear()
    
    cpdef void reset(self):
        '''
        Description:
            Reset the context
        '''
        self._stack.clear()
        self.clear_semantic_errors()
        self.clear_runtime_errors()

    cpdef void clear_errors(self):
        '''
        Description:
            Clear all errors
        '''
        self._stack.clear()
        self.clear_semantic_errors()
        self.clear_runtime_errors()

    cpdef void add_semantic_error(self,SemanticError error):
        '''
        Args:
            error (SemanticError)
        
        Description:
            Adds a new semantic error
        '''
        self._errors.append(error)
    
    cpdef void add_runtime_error(self,AST ast,RuntimeError error):
        '''
        Args:
            ast (AST)
            error (RuntimeError)
        
        Description:
            Adds a new RuntimeError from the given ast
        '''
        raise NotImplementedError()