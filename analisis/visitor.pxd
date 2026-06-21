from common.types cimport AST
from .error cimport SemanticError
from .context cimport Context

cdef class ASTVisitor:

    cpdef void visit(self,AST ast,Context context)

cdef class ASTChildrenSelector:

    cpdef list[AST] select_children(self,AST ast, Context context)

cdef class ASTWalker:

    cdef Context _context
    cdef dict[type,ASTVisitor] _visitors
    cdef dict[type,ASTChildrenSelector] _selectors

    cpdef void walk(self,AST ast)
    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor)
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector)