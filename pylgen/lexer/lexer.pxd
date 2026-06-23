from ..analisis.lexical cimport LexicRule
from ..analisis.error cimport LexicError
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    cdef dict[object,set[LexicRule]] _rules
    cdef set[LexicError] _errors
    cpdef void add_rule(self,object type_,LexicRule rule)
    cpdef void clear_errors(self)