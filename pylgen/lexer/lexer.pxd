from ..common.types cimport Token,Symbol
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

cdef class IdentedLexer(Lexer):
    cdef int _ident_counter
    cdef int _last_ident_value
    cdef object _ident_type
    cdef Symbol _indent_symbol
    cdef Symbol _dedent_symbol

    cpdef void set_ident(self,object ident_type)
    cpdef void set_indent_symbol(self,Symbol symbol)
    cpdef void set_dedent_symbol(self,Symbol symbol)