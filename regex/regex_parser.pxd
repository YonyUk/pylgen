from common.types cimport AST
from automaton.automaton cimport Automaton
from parser.parser cimport BottomUpParser
from lexer.lexer cimport BaseLexer

cdef class RegexAST(AST):
    cdef Automaton _get_automaton(self)

cdef class CharAST(RegexAST):
    cdef str _char

cdef class RegexBinaryAST(RegexAST):
    cdef RegexAST _left
    cdef RegexAST _right

cdef class ConcatenationAST(RegexBinaryAST):
    pass

cdef BottomUpParser _build_regex_parser()
cdef BaseLexer _build_regex_lexer()