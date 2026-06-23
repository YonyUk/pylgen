# cython language_level:3
from common.types cimport AST
from .context cimport Context

cdef class ASTVisitor:

    cdef type _context_type # type:ignore

    cpdef void visit(self,AST ast,Context context)

cdef class ASTChildrenSelector:

    cdef type _context_type # type:ignore

    cpdef list[AST] select_children(self,AST ast, Context context)

cdef class TraversalStrategy:
    cdef type _context_type # type:ignore
    cdef AST _root
    cdef dict[type,ASTChildrenSelector] _selectors

    cpdef void init(self,AST root)
    cpdef bint has_next(self)
    cpdef AST current(self,Context context)
    cpdef void reset(self)
    cpdef ASTChildrenSelector _get_selector(self,AST ast)
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector)

cdef class ASTWalker:

    cdef Context _context
    cdef dict[type,ASTVisitor] _visitors
    cdef TraversalStrategy _strategy

    cpdef void walk(self,AST ast)
    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor)