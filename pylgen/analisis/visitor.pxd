# cython language_level:3
from ..common.types cimport AST
from .context cimport Context

cdef class ASTVisitor:

    cdef type _context_type # type:ignore

    cpdef void visit(self,AST ast,Context context)
    cpdef void _check_context_type(self,Context context)

cdef class ASTChildrenSelector:

    cdef type _context_type # type:ignore

    cpdef void _check_context_type(self,Context context)
    cpdef list[AST] select_children(self,AST ast, Context context)

cdef class TraversalStrategy:
    cdef type _context_type # type:ignore
    cdef AST _root
    cdef dict[type,ASTChildrenSelector] _selectors
    cdef ASTChildrenSelector _default_selector

    cpdef void _check_context_type(self,Context context)
    cpdef void init(self,AST root)
    cpdef bint has_next(self)
    cpdef AST current(self,Context context)
    cpdef void reset(self)
    cpdef ASTChildrenSelector _get_selector(self,AST ast)
    cdef void add_selector_without_signature_checking(self,type ast_type,ASTChildrenSelector selector)
    cpdef void add_selector(self,type ast_type,ASTChildrenSelector selector)
    cpdef void set_default_selector(self,ASTChildrenSelector selector)
    cdef void set_default_selector_without_signatur_checking(self,ASTChildrenSelector selector)

cdef class ASTWalker:

    cdef Context _context
    cdef dict[type,ASTVisitor] _visitors
    cdef TraversalStrategy _strategy
    cdef ASTVisitor _default_visitor

    cpdef void walk(self,AST ast)
    cdef void add_visitor_without_signature_checking(self,type ast_type,ASTVisitor visitor)
    cpdef void add_visitor(self,type ast_type,ASTVisitor visitor)
    cpdef void set_default_visitor(self,ASTVisitor visitor)
    cdef void set_default_visitor_without_signature_checking(self,ASTVisitor visitor)