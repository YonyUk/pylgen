from typing import List
from string import ascii_letters,digits,printable,whitespace

from common.types cimport Symbol as cSymbol ,AST,Token
from common.types import Symbol
from automaton.automaton cimport (
    get_word_automaton,
    get_words_automaton,
    _automaton_concatenation,
    _automaton_complement,
    _automaton_union,
    _automaton_clousure,
    get_words_automaton_with_value,
    DFA
)
from grammar.grammar cimport AttributedGrammar
from parser.parser_builder cimport _build_lalr_parser_from_attributed
from lexer.lexer cimport BaseLexer

from .enums import ReTokenType

####################################################################################################
#                          TERMINALS
####################################################################################################
re_constant = cSymbol('re_constant',True) # type:ignore
re_lp = cSymbol('(',True) # type:ignore
re_rp = cSymbol(')',True) # type:ignore
re_lb = cSymbol('{',True) # type:ignore
re_rb = cSymbol('}',True) # type:ignore
re_lc = cSymbol('[',True) # type:ignore
re_rc = cSymbol(']',True) # type:ignore
re_klein_star = cSymbol('*',True) # type:ignore
re_positive_clousure = cSymbol('+',True) # type:ignore
re_or = cSymbol('|',True) # type:ignore
re_escape = cSymbol('\\',True) # type:ignore
re_optional = cSymbol('?',True) # type:ignore
re_char = cSymbol('char',True) # type:ignore

##################################################################################################
#                         MAPPING OF TOKENS TO TERMINALS SYMBOLS
##################################################################################################
symbols_by_text:dict[str,cSymbol] = {
    '(':re_lp,
    ')':re_rp,
    '{':re_lb,
    '}':re_rb,
    '[':re_lc,
    ']':re_rc
}
operatos_by_text:dict[str,cSymbol] = {
    '*':re_klein_star,
    '+':re_positive_clousure,
    '|':re_or,
    '?':re_optional
}
def get_symbol_function(t:ReTokenType,tx:str) -> Symbol:
    if t == ReTokenType.CHAR:
        return re_char # type:ignore
    if t == ReTokenType.SYMBOL:
        return symbols_by_text[tx] # type:ignore
    if t == ReTokenType.CONSTANT_RE:
        return re_constant # type:ignore
    if t == ReTokenType.OPERATOR:
        return operatos_by_text[tx] # type:ignore
    raise NotImplementedError()

####################################################################################################
#                         NON-TERMINALS
####################################################################################################
REGEX = cSymbol('REGEX') # type:ignore
RE = cSymbol('RE') # type:ignore
CHAR = cSymbol('CHAR') # type:ignore
RE_CONSTANT = cSymbol('RE_CONSTANT') # type:ignore
CHAR_SEQUENCE = cSymbol('CHAR_SEQUENCE') # type:ignore
KLEIN_STAR = cSymbol('KLEIN_STAR') # type:ignore
POSITIVE_CLOUSURE = cSymbol('POSITIVE_CLOUSURE') # type:ignore
OPTIONAL_CLOUSURE = cSymbol('OPTIONAL_CLOUSURE') # type:ignore
RE_GROUP = cSymbol('RE_GROUP') # type:ignore
RE_LP = Symbol('RE_LP') # type:ignore
RE_RP = Symbol('RE_RP') # type:ignore
# RE_LC = Symbol('RE_LC') # type:ignore
# RE_RC = Symbol('RE_RC') # type:ignore

####################################################################################################
#                               ASTs
####################################################################################################

cdef class RegexAST(AST):

    def __init__(self,cSymbol symbol, int line, int column):
        super().__init__(symbol, line, column) # type:ignore
    
    cdef Automaton _get_automaton(self):
        raise NotImplementedError()
    
    @property
    def automaton(self) -> Automaton:
        return self._get_automaton()

cdef class CharAST(RegexAST):

    def __init__(self,str char, int line,int column):
        super().__init__(re_char, line, column)
        self._char = char

    @property
    def char(self) -> str:
        return self._char

    cdef Automaton _get_automaton(self):
        return get_word_automaton(self._char)

cdef class RegexBinaryAST(RegexAST):

    def __init__(self,RegexAST left, RegexAST right,cSymbol symbol, int line, int column):
        super().__init__(symbol, line, column)
        self._right = right # type:ignore
        self._left = left # type:ignore
    
    @property
    def left(self) -> RegexAST:
        return self._left # type:ignore
    
    @property
    def right(self) -> RegexAST:
        return self._right # type:ignore

cdef class ConcatenationAST(RegexBinaryAST):

    def __init__(self, RegexAST left, RegexAST right, cSymbol symbol, int line, int column):
        super().__init__(left, right, symbol, line, column)

    cdef Automaton _get_automaton(self):
        return _automaton_concatenation(self._left._get_automaton(),self._right._get_automaton())

cdef class OrAST(RegexBinaryAST):

    def __init__(self, RegexAST left, RegexAST right, int line, int column):
        super().__init__(left, right, re_or, line, column)
    
    cdef Automaton _get_automaton(self):
        return _automaton_union({self._left._get_automaton(),self._right._get_automaton()})

cdef class ConstantRegexAST(RegexAST):

    def __init__(self, str re,int line, int column):
        super().__init__(re_constant, line, column)
        self._re = re
    
    @property
    def re_constant(self) -> str:
        return self._re

    cdef Automaton _get_automaton(self):
        cdef Automaton result
        if self._re == '\\d':
            result = get_words_automaton(list(digits))
        elif self._re == '\\D':
            result = get_words_automaton(list(digits))
            result._alphabet = set(printable)
            result = _automaton_complement(result)
        elif self._re == '\\s':
            result = get_words_automaton(list(whitespace))
        elif self._re == '\\S':
            result = get_words_automaton(list(whitespace))
            result._alphabet = set(printable)
            result = _automaton_complement(result)
        elif self._re == '\\w':
            result = get_words_automaton(list(digits) + list(ascii_letters) + ['_'])
        else:
            result = get_words_automaton(list(digits) + list(ascii_letters) + ['_'])
            result._alphabet = set(printable)
            result = _automaton_complement(result)
        return result

cdef class RegexUnaryAST(RegexAST):

    def __init__(self, RegexAST regex, cSymbol symbol, int line, int column):
        super().__init__(symbol, line, column)
        self._regex = regex # type:ignore
    
    @property
    def regex(self) -> RegexAST:
        return self._regex # type:ignore
    
cdef class KleinStarAST(RegexUnaryAST):

    def __init__(self,RegexAST regex, int line, int column):
        super().__init__(regex, re_klein_star, line, column)
        self._regex = regex # type:ignore

    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),0)

cdef class PositiveClousureAST(RegexUnaryAST):

    def __init__(self, regex: RegexAST, line: int, column: int):
        super().__init__(regex, re_positive_clousure, line, column)
    
    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),1)

cdef class OptionalAST(RegexUnaryAST):

    def __init__(self, regex: RegexAST, line: int, column: int):
        super().__init__(regex, re_optional, line, column)
    
    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),2)

###################################################################################################
#                                  REDUCTORS
###################################################################################################

def single_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return asts[0]

def char_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[0] # type:ignore
    return CharAST(token._text,token._line,token._column)

def concatenation_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST left = asts[0]
    cdef RegexAST right = asts[1]
    return ConcatenationAST(left,right,cSymbol('CONCATENATION'),left._line,left._column) # type:ignore

def union_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST left = asts[0]
    cdef RegexAST right = asts[2]
    cdef Token _or = asts[1] # type:ignore
    return OrAST(left,right,_or._line,_or._column)

def constant_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[0] # type:ignore
    return ConstantRegexAST(token._text,token._line,token._column)

def klein_star_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[1] # type:ignore
    return KleinStarAST(asts[0],token._line,token._column)

def positive_clousure_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[1] # type:ignore
    return PositiveClousureAST(asts[0],token._line,token._column)

def optional_clousure_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[1] # type:ignore
    return OptionalAST(asts[0],token._line,token._column)

def group_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return asts[1]

cdef BottomUpParser _build_regex_parser():
    cdef AttributedGrammar ReGrammar = AttributedGrammar(REGEX) # type:ignore
    # REGEX -> RE
    ReGrammar._add_attributed_production(REGEX,[RE],single_ast_reductor)
    # RE -> KLEIN_STAR
    ReGrammar._add_attributed_production(RE,[KLEIN_STAR],single_ast_reductor)
    # RE -> POSITIVE_CLOUSURE
    ReGrammar._add_attributed_production(RE,[POSITIVE_CLOUSURE],single_ast_reductor)
    # RE -> CHAR
    ReGrammar._add_attributed_production(RE,[CHAR],single_ast_reductor)
    # RE -> RE_CONSTANT
    ReGrammar._add_attributed_production(RE,[RE_CONSTANT],single_ast_reductor)
    # RE -> OPTIONAL_CLOUSURE
    ReGrammar._add_attributed_production(RE,[OPTIONAL_CLOUSURE],single_ast_reductor)
    # RE -> RE_GROUP
    ReGrammar._add_attributed_production(RE,[RE_GROUP],single_ast_reductor)

    # REGEX -> REGEX | RE
    ReGrammar._add_attributed_production(REGEX,[REGEX,re_or,RE],union_ast_reductor)
    
    # RE -> RE KLEIN_STAR
    ReGrammar._add_attributed_production(RE,[RE,KLEIN_STAR],concatenation_ast_reductor)
    # RE -> RE CHAR
    ReGrammar._add_attributed_production(RE,[RE,CHAR],concatenation_ast_reductor)
    # RE -> RE POSITIVE_CLOUSURE
    ReGrammar._add_attributed_production(RE,[RE,POSITIVE_CLOUSURE],concatenation_ast_reductor)
    # RE -> RE OPTIONAL_CLOUSURE
    ReGrammar._add_attributed_production(RE,[RE,OPTIONAL_CLOUSURE],concatenation_ast_reductor)
    # RE -> RE RE_GROUP
    ReGrammar._add_attributed_production(RE,[RE,RE_GROUP],concatenation_ast_reductor)

    # RE_CONSTANT -> re_constant
    ReGrammar._add_attributed_production(RE_CONSTANT,[re_constant],constant_ast_reductor)
    # CHAR -> re_char
    ReGrammar._add_attributed_production(CHAR,[re_char],char_ast_reductor)

    # KLEIN_STAR -> CHAR *
    ReGrammar._add_attributed_production(KLEIN_STAR,[CHAR,re_klein_star],klein_star_ast_reductor)
    # KLEIN_STAR -> RE_CONSTANT *
    ReGrammar._add_attributed_production(KLEIN_STAR,[RE_CONSTANT,re_klein_star],klein_star_ast_reductor)
    # KLEIN_STAR -> RE_GROUP *
    ReGrammar._add_attributed_production(KLEIN_STAR,[RE_GROUP,re_klein_star],klein_star_ast_reductor)
    
    # POSITIVE_CLOUSURE -> CHAR +
    ReGrammar._add_attributed_production(POSITIVE_CLOUSURE,[CHAR,re_positive_clousure],positive_clousure_ast_reductor)
    # POSITIVE_CLOUSURE -> RE_CONSTANT +
    ReGrammar._add_attributed_production(POSITIVE_CLOUSURE,[RE_CONSTANT,re_positive_clousure],positive_clousure_ast_reductor)
    # POSITIVE_CLOUSURE -> RE_GROUP +
    ReGrammar._add_attributed_production(POSITIVE_CLOUSURE,[RE_GROUP,re_positive_clousure],positive_clousure_ast_reductor)

    # OPTIONAL_CLOUSURE -> CHAR ?
    ReGrammar._add_attributed_production(OPTIONAL_CLOUSURE,[CHAR,re_optional],optional_clousure_ast_reductor)
    # OPTIONAL_CLOUSURE -> RE_CONSTANT ?
    ReGrammar._add_attributed_production(OPTIONAL_CLOUSURE,[RE_CONSTANT,re_optional],optional_clousure_ast_reductor)
    # OPTIONAL_CLOUSURE -> RE_GROUP ?
    ReGrammar._add_attributed_production(OPTIONAL_CLOUSURE,[RE_GROUP,re_optional],optional_clousure_ast_reductor)

    # RE_GROUP -> ( REGEX )
    ReGrammar._add_attributed_production(RE_GROUP,[re_lp,REGEX,re_rp],group_ast_reductor)

    return _build_lalr_parser_from_attributed(ReGrammar)

cdef BaseLexer _build_regex_lexer():
    cdef BaseLexer RE_LEXER = BaseLexer(get_symbol_function,DFA('EMPTY','EMPTY',set())) # type:ignore
    RE_LEXER._add_token(
        0,
        ReTokenType.CHAR,
        get_words_automaton_with_value(
            list(ascii_letters) + list(digits) + [' ','_'],
            ReTokenType.CHAR,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        1,
        ReTokenType.CONSTANT_RE,
        get_words_automaton_with_value(
            [
                '\\d',
                '\\D',
                '\\s',
                '\\S',
                '\\w',
                '\\W'
            ],
            ReTokenType.CONSTANT_RE,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        2,
        ReTokenType.OPERATOR,
        get_words_automaton_with_value(
            [
                '*',
                '+',
                '|',
                '?'
            ],
            ReTokenType.OPERATOR,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        3,
        ReTokenType.SYMBOL,
        get_words_automaton_with_value(
            [
                '(',
                ')'
            ],
            ReTokenType.SYMBOL,
            True # type:ignore
        )
    )
    return RE_LEXER