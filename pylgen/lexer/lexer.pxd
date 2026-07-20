from ..common.types cimport Token
from ..analysis.lexical cimport LexicalRule
from ..analysis.error cimport LexicalError
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    cdef dict[object,set[LexicalRule]] _rules
    cdef set[LexicalError] _errors
    cdef Token _eof
    cpdef void add_rule(self,object type_,LexicalRule rule)
    cpdef void clear_errors(self)
    cpdef void add_token_regex(self,int priority,object type_,str re)
    cpdef void set_eof_token(self,str symbol,object type_)