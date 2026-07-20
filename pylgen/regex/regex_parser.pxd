from ..common.types cimport AST
from ..automaton.automaton cimport Automaton
from ..parser.parser cimport BottomUpParser
from ..lexer.base_lexer cimport BaseLexer
from ..analysis.context cimport Context
from ..analysis.visitor cimport ASTChildrenSelector,ASTVisitor,ASTWalker,TraversalStrategy
from ..analysis.error cimport RuntimeError

cdef class RegexAST(AST):
    cdef Automaton _get_automaton(self)

cdef class CharAST(RegexAST):
    cdef str _char

cdef class RegexBinaryAST(RegexAST):
    cdef RegexAST _left
    cdef RegexAST _right

cdef class ConcatenationAST(RegexAST):
    cdef list[RegexAST] _sequence

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
    cdef StringAST _min
    cdef StringAST _max
    cdef RegexAST _regex

cdef class StringAST(AST):
    cdef str _string

cdef class RegexContext(Context):

    cdef list[RuntimeError] _runtime_errors
    cdef dict[RegexAST,object] _values

cdef class RegexASTChildrenSelector(ASTChildrenSelector):
    pass

cdef class RepeatPatternASTVisitor(ASTVisitor):
    pass

cdef class PostOrderStrategy(TraversalStrategy):
    
    cdef list[RegexAST] _stack
    cdef list[RegexAST] _seen

cdef BottomUpParser _build_regex_parser()
cdef BaseLexer _build_regex_lexer()
cdef tuple[ASTWalker,RegexContext] _get_regex_ast_walker()