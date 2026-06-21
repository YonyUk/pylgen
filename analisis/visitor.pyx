from common.types cimport AST
from .error cimport SemanticError

cdef class ASTVisitor:
    
    cpdef SemanticError visit(self,AST ast):
        '''
        Args: ast (AST)

        Returns:
            SemanticError | None 
        '''
        raise NotImplementedError()

cdef class ASTChildrenSelector:

    cpdef list[AST] select_children(self,AST ast):
        '''
        Args:
            ast (AST)
        
        Returns:
            List[AST]: a list of childrens (self-included if needed) with the nodes in the orden in which
            the nodes will be visited
        '''
        raise NotImplementedError()


cdef class ASTWalker:

    def __init__(self,) -> None:
        self._errors = []
        self._visitors = {}
        self._selectors = {}
    
    @property
    def errors(self) -> list[SemanticError]:
        return self._errors
    
    cpdef void reset(self):
        self._errors.clear()
    
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector):
        self._selectors[ast_type] = selector

    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor):
        self._visitors[ast_type] = visitor
    
    cpdef void walk(self,AST ast):
        cdef list[AST] stack = [ast]
        cdef AST current
        cdef type ast_type # type:ignore
        cdef ASTVisitor visitor
        cdef ASTChildrenSelector selector
        cdef SemanticError error

        while stack:
            current = stack.pop()
            ast_type = type(current)
            if ast_type in self._visitors:
                visitor = self._visitors[ast_type]
                error = visitor.visit(current)
                if not error is None:
                    self._errors.append(error)
            if ast_type in self._selectors:
                selector = self._selectors[ast_type]
                stack += selector.select_children(current)