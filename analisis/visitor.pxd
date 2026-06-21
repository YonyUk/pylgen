from common.types cimport AST
from .error cimport SemanticError

cdef class ASTVisitor:

    cpdef SemanticError visit(self,AST ast)

cdef class ASTChildrenSelector:

    cpdef list[AST] select_children(self,AST ast)

cdef class ASTWalker:

    cdef list[SemanticError] _errors
    cdef dict[type,ASTVisitor] _visitors
    cdef dict[type,ASTChildrenSelector] _selectors

    cpdef void walk(self,AST ast)
    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor)
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector)
    cpdef void reset(self)