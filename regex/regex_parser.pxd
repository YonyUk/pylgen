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

cdef class OrAST(RegexBinaryAST):
    pass

cdef class ConstantRegexAST(RegexAST):
    cdef str _re

cdef class RegexUnaryAST(RegexAST):
    cdef RegexAST _regex

cdef class KleeneStarAST(RegexUnaryAST):
    pass

cdef class PositiveClousureAST(RegexUnaryAST):
    pass

cdef class OptionalAST(RegexUnaryAST):
    pass

cdef class CharSetAST(RegexAST):
    cdef CharSetAST _next
    cdef CharSetAST _preceding

cdef class CharSetExplicitAST(CharSetAST):
    cdef set[str] _char_set

    cdef void _add_char(self,str char)

cdef class CharRangeAST(CharSetAST):
    cdef CharAST _left
    cdef CharAST _right

cdef class ComplementCharSetAST(CharSetAST):
    cdef CharSetAST _char_set

cdef class RepeatPatternAST(RegexAST):
    cdef CharAST _min
    cdef CharAST _max
    cdef RegexAST _regex

cdef BottomUpParser _build_regex_parser()
cdef BaseLexer _build_regex_lexer()