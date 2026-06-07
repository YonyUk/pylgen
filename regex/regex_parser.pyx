from typing import List
from string import ascii_letters,digits

from common.types cimport Symbol as cSymbol ,AST,Token
from common.types import Symbol
from automaton.automaton cimport get_word_automaton,_automaton_concatenation,DFA,get_words_automaton_with_value
from grammar.grammar cimport AttributedGrammar
from parser.parser_builder cimport _build_lalr_parser_from_attributed
from lexer.lexer cimport BaseLexer

from .enums import ReTokenType

def get_symbol_function(t:ReTokenType,tx:str) -> Symbol:
    raise NotImplementedError()

RE_LEXER = BaseLexer(get_symbol_function,DFA('EMPTY','EMPTY',set())) # type:ignore
(<BaseLexer>RE_LEXER)._add_token(0,ReTokenType.CHAR,get_words_automaton_with_value(list(ascii_letters) + list(digits),ReTokenType.CHAR,True)) # type:ignore

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
re_klein_start = cSymbol('*',True) # type:ignore
re_positive_clousure = cSymbol('+',True) # type:ignore
re_or = cSymbol('|',True) # type:ignore
re_escape = cSymbol('\\',True) # type:ignore
re_optional = cSymbol('?',True) # type:ignore
re_char = cSymbol('char',True) # type:ignore

####################################################################################################
#                         NON-TERMINALS
####################################################################################################
REGEX = cSymbol('REGEX') # type:ignore
RE = cSymbol('RE') # type:ignore
CHAR = cSymbol('CHAR') # type:ignore
CHAR_SEQUENCE = cSymbol('CHAR_SEQUENCE') # type:ignore
PRECEDING_RE = cSymbol('PRECEDING_RE') # type:ignore
# RE_SEQUENCE = Symbol('RE_SEQUENCE') # type:ignore
# RE_LP = Symbol('RE_LP') # type:ignore
# RE_RP = Symbol('RE_RP') # type:ignore
# RE_LB = Symbol('RE_LB') # type:ignore
# RE_RB = Symbol('RE_RB') # type:ignore
# RE_LC = Symbol('RE_LC') # type:ignore
# RE_RC = Symbol('RE_RC') # type:ignore

####################################################################################################
#                               ASTs
####################################################################################################
cdef class RegexAST(AST):

    def __init__(self,cSymbol symbol,int line,int column):
        super().__init__(symbol,line,column) # type:ignore

    @property
    def automaton(self) -> Automaton:
        return self._automaton

cdef class CharAST(RegexAST):

    def __init__(self,str char,int line,int column):
        super().__init__(re_char,line,column) # type:ignore
        self._automaton = get_word_automaton(char) # type:ignore
        
cdef class ConcatenationAST(RegexAST):

    def __init__(self,list[RegexAST] sequence,cSymbol symbol,int line,int column):
        cdef Automaton aut,aut1
        cdef int idx

        super().__init__(symbol,line,column) # type:ignore
        if len(sequence) > 0:
            aut = (<RegexAST>sequence[0])._automaton
        
        for idx in range(1,len(sequence)):
            aut1 = (<RegexAST>sequence[idx])._automaton
            aut = _automaton_concatenation(aut,aut1)
        
        self._automaton = aut # type:ignore
    
    cdef void _add_re(self,RegexAST ast):
        cdef Automaton aut = ast._automaton
        self._automaton = _automaton_concatenation(self._automaton,aut) # type:ignore

def single_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return asts[0]

def CHAR_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return CharAST((<Token>asts[0])._text,asts[0]._line,asts[0]._column)

def RE_concatenation_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    if isinstance(asts[0],ConcatenationAST):
        asts[0]._add_re(asts[1])
        return asts[0]
    return ConcatenationAST(asts,RE,asts[0]._line,asts[0]._column)

def CHAR_SEQUENCE_concatenation_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    if isinstance(asts[0],ConcatenationAST):
        asts[0]._add_re(asts[1])
        return asts[0]
    return ConcatenationAST(asts,CHAR_SEQUENCE,asts[0]._line,asts[0]._column)

ReGrammar = AttributedGrammar(REGEX) # type:ignore
# REGEX -> RE
ReGrammar._add_attributed_production(REGEX,[RE],single_ast_reductor)
# RE -> PRECEDING_RE
ReGrammar._add_attributed_production(RE,[PRECEDING_RE],single_ast_reductor)
# RE -> RE PRECEDING_RE
ReGrammar._add_attributed_production(RE,[RE,PRECEDING_RE],RE_concatenation_ast_reductor)
# PRECEDING_RE -> CHAR_SEQUENCE
ReGrammar._add_attributed_production(PRECEDING_RE,[CHAR_SEQUENCE],single_ast_reductor)
# CHAR_SEQUENCE -> CHAR
ReGrammar._add_attributed_production(CHAR_SEQUENCE,[CHAR],single_ast_reductor)
# CHAR_SEQUENCE -> CHAR_SEQUENCE CHAR
ReGrammar._add_attributed_production(CHAR_SEQUENCE,[CHAR_SEQUENCE,CHAR],CHAR_SEQUENCE_concatenation_ast_reductor)
# CHAR -> re_char
ReGrammar._add_attributed_production(CHAR,[re_char],CHAR_ast_reductor)

cdef BottomUpParser _build_regex_parser():
    return _build_lalr_parser_from_attributed(ReGrammar)

cdef BaseLexer _build_regex_lexer():
    return RE_LEXER