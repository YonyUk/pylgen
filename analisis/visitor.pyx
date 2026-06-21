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


cdef class ASTWalker:

    def __init__(self,Context context) -> None:
        self._visitors = {}
        self._selectors = {}
        self._context = context
    
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector):
        self._selectors[ast_type] = selector # type:ignore

    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor):
        self._visitors[ast_type] = visitor # type:ignore
    
    cpdef void walk(self,AST ast):
        cdef list[AST] stack = []
        cdef AST current
        cdef list[AST] seen = []
        cdef type ast_type # type:ignore
        cdef ASTVisitor visitor
        cdef ASTChildrenSelector selector
        cdef SemanticError error
        cdef AST child
        cdef bint asts_added = False # type:ignore

        ast_type = type(ast)
        if ast_type in self._selectors:
            selector = self._selectors[ast_type] # type:ignore
            stack += selector.select_children(ast,self._context)

        while stack:
            asts_added = False # type:ignore
            current = stack[-1]
            seen.append(current)
            ast_type = type(current)
            if ast_type in self._selectors:
                selector = self._selectors[ast_type] # type:ignore
                for child in selector.select_children(current,self._context):
                    if not child in stack and not child in seen:
                        stack.append(child)
                        asts_added = True # type:ignore
            if asts_added:
                continue
            if ast_type in self._visitors:
                visitor = self._visitors[ast_type] # type:ignore
                visitor.visit(current,self._context)
            stack.pop()