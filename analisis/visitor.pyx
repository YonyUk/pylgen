from common.types cimport AST
from .error cimport SemanticError
from .context cimport Context

cdef class ASTVisitor:
    
    cpdef void visit(self,AST ast,Context context):
        '''
        Args: ast (AST)

        Returns:
            SemanticError | None 
        '''
        raise NotImplementedError()

cdef class ASTChildrenSelector:

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

    def __init__(self) -> None:
        self._selectors = {}
        pass
    
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
        return self._selectors[ast_type] # type:ignore

    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector):
        self._selectors[ast_type] = selector # type:ignore

cdef class ASTWalker:

    def __init__(self,Context context,TraversalStrategy strategy) -> None:
        self._visitors = {}
        self._context = context
        self._strategy = strategy # type:ignore

    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor):
        self._visitors[ast_type] = visitor # type:ignore
    
    cpdef void walk(self,AST ast):
        cdef AST current
        cdef type ast_type # type:ignore
        cdef ASTVisitor visitor
        cdef ASTChildrenSelector selector
        cdef SemanticError error

        self._strategy.init(ast)

        while self._strategy.has_next():
            current = self._strategy.current(self._context)
            ast_type = type(current)
            if ast_type in self._visitors:
                visitor = self._visitors[ast_type] # type:ignore
                visitor.visit(current,self._context)
        
        self._strategy.reset()