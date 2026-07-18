from pylgen.lexer.lexer cimport Lexer
from pylgen.common.types cimport Symbol

cpdef Lexer build_lexer()

cdef Symbol get_symbol_function(object t,str tx)