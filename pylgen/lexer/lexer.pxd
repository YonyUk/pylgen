from ..common.types cimport Token
from ..analysis.lexical cimport LexicRule
from ..analysis.error cimport LexicError
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    cdef dict[object,set[LexicRule]] _rules
    cdef set[LexicError] _errors
    cdef Token _eof
    cpdef void add_rule(self,object type_,LexicRule rule)
    cpdef void clear_errors(self)
    cpdef void add_token_regex(self,int priority,object type_,str re)
    cpdef void set_eof_token(self,str symbol,object type_)