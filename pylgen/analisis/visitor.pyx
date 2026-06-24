# cython language_level:3
from typing import get_type_hints
import inspect

from ..common.types cimport AST
from .error cimport SemanticError
from .context cimport Context

cdef class ASTVisitor:
    '''
    Base clas for Visitor pattern

    methods that must be implemented

    def visit(self,ast:AST,context:Context)
    WARNING: self._check_context_type must be called at first of visit method
    '''

    def __init__(self,type context_type) -> None:
        if not issubclass(context_type,Context):
            raise ValueError(f'context_type must be a subclass of {Context}')
        self._context_type = context_type

    cpdef void _check_context_type(self,Context context):
        if not isinstance(context,self._context_type):
            raise TypeError(f'context must be an instance of {self._context_type}')

    cpdef void visit(self,AST ast,Context context):
        '''
        Args:
            ast (AST)
            context (Context)
        '''
        raise NotImplementedError()

cdef class ASTChildrenSelector:
    '''
    Base class for AST children selectors

    methods that must be implemented
    select_children(self,ast:AST,context:Context)
    WARNING: self._check_context_type must be called at first of select_children method
    '''

    def __init__(self,type context_type) -> None:
        if not issubclass(context_type,Context):
            raise ValueError(f'context_type must be a subclass of {Context}')
        self._context_type = context_type

    cpdef void _check_context_type(self,Context context):
        if not isinstance(context,self._context_type):
            raise TypeError(f'context must be an instance of {self._context_type}')


    cpdef list[AST] select_children(self,AST ast, Context context):
        '''
        Args:
            ast (AST)
        
        Returns:
            List[AST]: a list of childrens (self-included if needed) with the nodes in the orden in which
            the nodes will be visited
        '''
        raise NotImplementedError()

cdef class TraversalStrategy:
    '''
    Base class for traversals strategies for walk over asts
    
    methods that must be implemented
    has_next(self)
    reset(self)
    current(self)
    WARNING: self._check_context_type must be called at first of current method
    '''

    def __init__(self,type context_type) -> None:
        if not issubclass(context_type,Context):
            raise ValueError(f'context_type must be a subclass of {Context}')
        self._context_type = context_type
        self._selectors = {}
        self._default_selector = None # type:ignore
    
    cpdef void _check_context_type(self,Context context):
        if not isinstance(context,self._context_type):
            raise TypeError(f'context must be an instance of {self._context_type}')

    cpdef void init(self,AST root):
        self._root = root

    cpdef bint has_next(self):
        raise NotImplementedError()
    
    cpdef AST current(self,Context context):
        raise NotImplementedError()

    cpdef void reset(self):
        raise NotImplementedError()
    
    cpdef ASTChildrenSelector _get_selector(self,AST ast):
        cdef type ast_type = type(ast) # type:ignore
        if not ast_type in self._selectors and self._default_selector is not None: # type:ignore
            return self._default_selector # type:ignore
        return self._selectors[ast_type] # type:ignore

    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector):
        signature = inspect.signature(selector.select_children)
        params = list(signature.parameters.values())
        if params[1].annotation is inspect.Signature.empty:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {self._context_type}')
        if params[1].annotation != self._context_type:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {self._context_type}')
        self._selectors[ast_type] = selector # type:ignore
    
    cpdef void set_default_selector(self,ASTChildrenSelector selector):
        signature = inspect.signature(selector.select_children)
        params = list(signature.parameters.values())
        if params[1].annotation is inspect.Signature.empty:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {self._context_type}')
        if params[1].annotation != self._context_type:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {self._context_type}')
        self._default_selector = selector # type:ignore

cdef class ASTWalker:

    def __init__(self,Context context,TraversalStrategy strategy) -> None:
        self._visitors = {}
        self._context = context
        self._strategy = strategy # type:ignore
        self._default_visitor = None # type:ignore

    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor):
        signature = inspect.signature(visitor.visit)
        params = list(signature.parameters.values())
        if params[1].annotation is inspect.Signature.empty:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {type(self._context)}')
        if params[1].annotation != type(self._context):
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {type(self._context)}')
        self._visitors[ast_type] = visitor # type:ignore
    
    cpdef void set_default_visitor(self,ASTVisitor visitor):
        signature = inspect.signature(visitor.visit)
        params = list(signature.parameters.values())
        if params[1].annotation is inspect.Signature.empty:
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {type(self._context)}')
        if params[1].annotation != type(self._context):
            raise TypeError(f'selector.select_children incorrect signature, second param must be of type {type(self._context)}')
        self._default_visitor = visitor # type:ignore

    cpdef void walk(self,AST ast):
        cdef AST current
        cdef type ast_type # type:ignore
        cdef ASTVisitor visitor
        cdef ASTChildrenSelector selector
        cdef SemanticError error

        self._strategy.init(ast)

        while self._strategy.has_next():
            current = self._strategy.current(self._context) # type:ignore
            ast_type = type(current)
            if ast_type in self._visitors:
                if not ast_type in self._visitors and self._default_visitor is not None:
                    visitor = self._default_visitor # type:ignore
                else:
                    visitor = self._visitors[ast_type] # type:ignore
                visitor.visit(current,self._context)
        
        self._strategy.reset()