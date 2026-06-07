from common.types cimport AST
from automaton.automaton cimport Automaton
from parser.parser cimport BottomUpParser
from lexer.lexer cimport BaseLexer

cdef class RegexAST(AST):
    cdef Automaton _automaton

cdef class CharAST(RegexAST):
    pass

cdef class ConcatenationAST(RegexAST):

    cdef void _add_re(self,RegexAST ast)

cdef BottomUpParser _build_regex_parser()
cdef BaseLexer _build_regex_lexer()