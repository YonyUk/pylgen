from typing import List,Set
from string import ascii_letters,digits,printable,whitespace

from common.types cimport Symbol as cSymbol ,AST,Token
from common.types import Symbol
from common.table cimport Table
from automaton.automaton cimport (
    get_word_automaton,
    get_words_automaton,
    _automaton_concatenation,
    _automaton_complement,
    _automaton_union,
    _automaton_clousure,
    get_words_automaton_with_value,
    _copy_dfa,
    _copy_nfa,
    DFA,
    NFA,
    State
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
re_kleene_star = cSymbol('*',True) # type:ignore
re_positive_clousure = cSymbol('+',True) # type:ignore
re_or = cSymbol('|',True) # type:ignore
re_optional = cSymbol('?',True) # type:ignore
re_char = cSymbol('char',True) # type:ignore
re_accent = cSymbol('^',True) # type:ignore
re_minus = cSymbol('-',True) # type:ignore
re_escape_char = cSymbol('escape_char',True) # type:ignore
re_com = cSymbol(',',True) # type:ignore

##################################################################################################
#                         MAPPING OF TOKENS TO TERMINALS SYMBOLS
##################################################################################################
symbols_by_text:dict[str,cSymbol] = {
    '(':re_lp,
    ')':re_rp,
    '{':re_lb,
    '}':re_rb,
    '[':re_lc,
    ']':re_rc,
    '-':re_minus,
    ',':re_com
}
operatos_by_text:dict[str,cSymbol] = {
    '*':re_kleene_star,
    '+':re_positive_clousure,
    '|':re_or,
    '?':re_optional,
    '^':re_accent
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
    if t == ReTokenType.ESCAPE_CHAR:
        return re_escape_char # type:ignore
    raise NotImplementedError()

####################################################################################################
#                         NON-TERMINALS
####################################################################################################
REGEX = cSymbol('REGEX') # type:ignore
RE = cSymbol('RE') # type:ignore
ATOM = cSymbol('ATOM') # type:ignore
CHAR = cSymbol('CHAR') # type:ignore
RE_GROUP = cSymbol('RE_GROUP') # type:ignore
REPEAT = cSymbol('REPEAT') # type:ignore
CHAR_SET = cSymbol('CHAR_SET') # type:ignore
CHAR_SET_SEQUENCE = cSymbol('CHAR_SET_SEQUENCE') # type:ignore
CHAR_SET_SEQUENCE_ATOM = cSymbol('CHAR_SET_SEQUENCE_ATOM') # type:ignore
CHAR_RANGE = cSymbol('CHAR_RANGE') # type:ignore

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
        cdef set[str] char_set
        if self._re == '\\d':
            result = get_words_automaton(list(digits))
        elif self._re == '\\D':
            char_set = set(printable).difference(set(digits))
            result = get_words_automaton(list(char_set))
        elif self._re == '\\s':
            result = get_words_automaton(list(whitespace))
        elif self._re == '\\S':
            char_set = set(printable).difference(set(whitespace))
            result = get_words_automaton(list(char_set))
        elif self._re == '\\w':
            result = get_words_automaton(list(digits) + list(ascii_letters) + ['_'])
        elif self._re == '.':
            char_set = set(printable)
            char_set.discard('\n')
            result = get_words_automaton(list(char_set))
        else:
            char_set = set(printable).difference(set(ascii_letters+digits+'_'))
            result = get_words_automaton(list(char_set))
        return result

cdef class RegexUnaryAST(RegexAST):

    def __init__(self, RegexAST regex, cSymbol symbol, int line, int column):
        super().__init__(symbol, line, column)
        self._regex = regex # type:ignore
    
    @property
    def regex(self) -> RegexAST:
        return self._regex # type:ignore
    
cdef class KleeneStarAST(RegexUnaryAST):

    def __init__(self,RegexAST regex, int line, int column):
        super().__init__(regex, re_kleene_star, line, column)
        self._regex = regex # type:ignore

    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),0)

cdef class PositiveClousureAST(RegexUnaryAST):

    def __init__(self, RegexAST regex, int line, int column):
        super().__init__(regex, re_positive_clousure, line, column)
    
    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),1)

cdef class OptionalAST(RegexUnaryAST):

    def __init__(self, regex: RegexAST, line: int, column: int):
        super().__init__(regex, re_optional, line, column)
    
    cdef Automaton _get_automaton(self):
        return _automaton_clousure(self._regex._get_automaton(),2)

cdef class CharSetAST(RegexAST):

    def __init__(self, cSymbol symbol, int line, int column):
        super().__init__(symbol, line, column)
        self._next = None # type:ignore
        self._preceding = None # type:ignore

    @property
    def next_re(self) -> CharSetAST:
        return self._next # type:ignore
    
    @property
    def preceding_re(self) -> CharSetAST:
        return self._preceding # type:ignore
    
    cdef Automaton _get_automaton(self):
        return _automaton_union({self._preceding._get_automaton(),self._next._get_automaton()})

cdef class CharSetExplicitAST(CharSetAST):

    def __init__(self, line: int, column: int):
        super().__init__(CHAR_SET,line, column)
        self._char_set = set()
    
    @property
    def char_set(self) -> Set[str]:
        return self._char_set
    
    cdef void _add_char(self,str char):
        self._char_set.add(char)

    cdef Automaton _get_automaton(self):
        return get_words_automaton(list(self._char_set))

cdef class CharRangeAST(CharSetAST):

    def __init__(self, CharAST left, CharAST right, int line, int column):
        super().__init__(CHAR_RANGE, line, column)
        self._left = left # type:ignore
        self._right = right # type:ignore
    
    @property
    def left(self) -> CharAST:
        return self._left # type:ignore
    
    @property
    def right(self) -> CharAST:
        return self._right # type:ignore
    
    cdef Automaton _get_automaton(self):
        cdef int i
        cdef set[str] _char_set = { chr(i) for i in range(ord(self._left._char),ord(self._right._char) + 1)}
        return get_words_automaton(list(_char_set))

cdef class ComplementCharSetAST(CharSetAST):

    def __init__(self, CharSetAST char_set,int line, int column):
        super().__init__(CHAR_SET, line, column)
        self._char_set = char_set # type:ignore
    
    @property
    def char_set(self) -> CharSetAST:
        return self._char_set # type:ignore
    
    cdef Automaton _get_automaton(self):
        cdef Automaton aut = self._char_set._get_automaton()
        cdef set[str] _char_set = set(printable).difference(aut._alphabet)
        return get_words_automaton(list(_char_set))

cdef class RepeatPatternAST(RegexAST):

    def __init__(self, RegexAST regex, CharAST min_, CharAST max_, int line, int column):
        super().__init__(REPEAT, line, column)
        self._min = min_ # type:ignore
        self._min._symbol = cSymbol('min') # type:ignore
        self._max = max_ # type:ignore
        self._max._symbol = cSymbol('max') # type:ignore
        self._regex = regex # type:ignore
    
    @property
    def min(self) -> CharAST:
        return self._min # type:ignore
    
    @property
    def max(self) -> CharAST:
        return self._max # type:ignore
    
    @property
    def regex(self) -> RegexAST:
        return self._regex # type:ignore
    
    cdef Automaton _get_automaton(self):
        cdef Automaton aut = self._regex._get_automaton()
        cdef NFA result
        cdef dict[str,State] states_by_id_mapping = {}
        cdef int iteration
        cdef str state_id,n_state_id,f_id,t_id,symbol
        cdef State state,f_state,t_state,n_f_state,n_t_state
        cdef tuple[str,str] transition
        cdef int max_,min_

        max_ = int(self._max._char)
        min_ = int(self._min._char)

        # maps the states by iteration
        for iteration in range(max_):
            for state_id,state in aut._states_by_id.items():
                n_state_id = f'{iteration}-{state_id}'
                if min_ - 1 <= iteration <= max_ - 1:
                    states_by_id_mapping[n_state_id] = State(n_state_id,state._value,state._is_accept) # type:ignore
                else:
                    states_by_id_mapping[n_state_id] = State(n_state_id,state._value) # type:ignore
        result = NFA('start','start',aut._alphabet) # type:ignore
        result._start_state = states_by_id_mapping[f'0-{aut._start_state._id}']
        result._states_by_id[f'0-{aut._start_state._id}'] = result._start_state

        if self._min == 0:
            result._start_state._is_accept = True # type:ignore

        for iteration in range(max_):
            for transition in aut._trans_func._table:
                f_id = <str>transition[0]
                symbol = <str>transition[1]
                t_id = aut._trans_func._table[transition]
                f_state = aut._states_by_id[f_id]
                t_state = aut._states_by_id[t_id]
                n_f_state = states_by_id_mapping[f'{iteration}-{f_id}']
                n_t_state = states_by_id_mapping[f'{iteration}-{t_id}']

                result.add_transition(n_f_state,n_t_state,symbol)
                if iteration < max_ - 1:
                    n_t_state = states_by_id_mapping[f'{iteration + 1}-{aut._start_state._id}']
                    if f_state._is_accept:
                        result.add_epsilon_transition(n_f_state,n_t_state)
                    if t_state._is_accept:
                        n_f_state = states_by_id_mapping[f'{iteration}-{t_id}']
                        result.add_epsilon_transition(n_f_state,n_t_state)
            
            for f_id in aut._epsilons:
                for t_id in aut._epsilons[f_id]:
                    f_state = aut._states_by_id[f_id]
                    t_state = aut._states_by_id[t_id]
                    n_f_state = states_by_id_mapping[f'{iteration}-{f_id}']
                    n_t_state = states_by_id_mapping[f'{iteration}-{t_id}']
                    result.add_epsilon_transition(n_f_state,n_t_state)
                    if iteration < max_ - 1:
                        n_t_state = states_by_id_mapping[f'{iteration + 1}-{aut._start_state._id}']
                        if f_state._is_accept:
                            result.add_epsilon_transition(n_f_state,n_t_state)
                        if t_state._is_accept:
                            n_f_state = states_by_id_mapping[f'{iteration}-{t_id}']
                            result.add_epsilon_transition(n_f_state,n_t_state)
        return result

###################################################################################################
#                                  REDUCTORS
###################################################################################################

def single_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return asts[0]

def concatenation_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST left,right
    left = asts[0]
    right = asts[1]
    return ConcatenationAST(left,right,cSymbol('CONCATENATION'),left._line,left._column) # type:ignore

def char_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[0] # type:ignore
    if token._type == ReTokenType.ESCAPE_CHAR:
        return CharAST(token._text[1],token._line,token._column)
    return CharAST(token._text,token._line,token._column)

def re_constant_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token = asts[0] # type:ignore
    return ConstantRegexAST(token._text,token._line,token._column)

def kleene_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST regex = asts[0]
    return KleeneStarAST(regex,regex._line,regex._column)

def positive_clousure_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST regex = asts[0]
    return PositiveClousureAST(regex,regex._line,regex._column)

def optional_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST regex = asts[0]
    return OptionalAST(regex,regex._line,regex._column)

def union_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST left,right
    cdef Token token = asts[1] # type:ignore

    left = asts[0]
    right = asts[2]

    return OrAST(left,right,token._line,token._column)

def group_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    return asts[1]

def repeat_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST regex = asts[0]
    cdef CharAST min_,max_

    min_ = asts[2] # type:ignore
    max_ = asts[4] # type:ignore

    return RepeatPatternAST(regex,min_,max_,regex._line,regex._column)

def repeat_re_constant_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token constant = asts[0] # type:ignore
    cdef CharAST min_,max_
    cdef RegexAST regex = ConstantRegexAST(constant._text,constant._line,constant._column)

    min_ = asts[2] # type:ignore
    max_ = asts[4] # type:ignore

    return RepeatPatternAST(regex,min_,max_,constant._line,constant._column)

def char_set_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef RegexAST regex
    cdef Token token = asts[0] # type:ignore

    if len(asts) == 3:
        return asts[1]

    regex = asts[2]
    return ComplementCharSetAST(regex,token._line,token._column) # type:ignore

def char_set_sequence_atom_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef Token token
    cdef CharSetExplicitAST explicit
    cdef CharRangeAST char_range
    cdef CharAST char_ast,char_ast1

    if len(asts) == 1:
        if isinstance(asts[0],Token):
            token = asts[0]
            explicit = CharSetExplicitAST(token._line,token._column)
            explicit._char_set = set(token._text)
            return explicit
        char_ast = asts[0] # type:ignore
        explicit = CharSetExplicitAST(char_ast._line,char_ast._column)
        explicit._add_char(char_ast._char)
        return explicit
    
    token = asts[1] # type:ignore
    char_ast = asts[0] # type:ignore
    char_ast1 = asts[2] # type:ignore
    char_range = CharRangeAST(char_ast,char_ast1,token._line,token._column)
    return char_range

def char_set_sequence_ast_reductor(asts:List[RegexAST]) -> RegexAST:
    cdef CharSetExplicitAST explicit1,explicit2
    cdef CharRangeAST char_range1
    cdef CharSetAST result,new_result

    if isinstance(asts[0],CharSetExplicitAST):
        explicit1 = asts[0]

        if isinstance(asts[1],CharSetExplicitAST):
            explicit2 = asts[1]
            explicit1._char_set.update(explicit2._char_set)
            return explicit1
        
        char_range1 = asts[1] # type:ignore
        result = CharSetAST(CHAR_SET_SEQUENCE,explicit1._line,explicit1._column)
        result._preceding = explicit1 # type:ignore
        result._next = char_range1 # type:ignore
        return result
    
    if isinstance(asts[0],CharRangeAST):
        char_range1 = asts[0]
        result = CharSetAST(CHAR_SET_SEQUENCE,char_range1._left._line,char_range1._left._column)
        result._preceding = char_range1 # type:ignore
        result._next = asts[1] # type:ignore
        return result
    
    result = asts[0] # type:ignore
    if isinstance(result._next,CharSetExplicitAST):
        explicit1 = result._next
        if isinstance(asts[1],CharSetExplicitAST):
            explicit2 = asts[1]
            explicit1._char_set.update(explicit2._char_set)
            return result
        char_range1 = asts[1] # type:ignore
        new_result = CharSetAST(CHAR_SET_SEQUENCE,result._line,result._column)
        new_result._preceding = result # type:ignore
        new_result._next = char_range1 # type:ignore
        return new_result
    
    if isinstance(asts[1],CharSetExplicitAST):
        explicit1 = asts[1]
        new_result = CharSetAST(CHAR_SET_SEQUENCE,result._line,result._column)
        new_result._preceding = result # type:ignore
        new_result._next = explicit1 # type:ignore
        return new_result

    char_range1 = asts[1] # type:ignore
    new_result = CharSetAST(CHAR_SET_SEQUENCE,result._line,result._column)
    new_result._preceding = result # type:ignore
    new_result._next = char_range1 # type:ignore
    return new_result

cdef BottomUpParser _build_regex_parser():
    '''
    REGEX -> RE

    REGEX -> REGEX | RE

    RE -> ATOM | RE ATOM

    ATOM -> CHAR | re_constant | RE_GROUP | REPEAT | CHAR_SET | ATOM * | ATOM + | ATOM ?

    CHAR -> re_char | re_escape_char

    RE_GROUP -> ( REGEX )

    REPEAT -> CHAR { CHAR , CHAR } | re_constant { CHAR , CHAR } | RE_GROUP { CHAR , CHAR } | CHAR_SET { CHAR , CHAR }

    CHAR_SET -> [ CHAR_SET_SEQUENCE ] | [ ^ CHAR_SET_SEQUENCE ]

    CHAR_SET_SEQUENCE -> CHAR_SET_SEQUENCE_ATOM | CHAR_SET_SEQUENCE CHAR_SET_SEQUENCE_ATOM

    CHAR_SET_SEQUENCE_ATOM -> CHAR | CHAR - CHAR
    '''
    cdef AttributedGrammar ReGrammar = AttributedGrammar(REGEX) # type:ignore

    # REGEX -> RE
    ReGrammar._add_attributed_production(REGEX,[RE],single_ast_reductor)
    # REGEX -> REGEX | RE
    ReGrammar._add_attributed_production(REGEX,[REGEX,re_or,RE],union_ast_reductor)
    
    # RE -> ATOM
    ReGrammar._add_attributed_production(RE,[ATOM],single_ast_reductor)
    # RE -> RE ATOM
    ReGrammar._add_attributed_production(RE,[RE,ATOM],concatenation_ast_reductor)

    # ATOM -> CHAR
    ReGrammar._add_attributed_production(ATOM,[CHAR],single_ast_reductor)
    # ATOM -> re_constant
    ReGrammar._add_attributed_production(ATOM,[re_constant],re_constant_ast_reductor)
    # ATOM -> RE_GROUP
    ReGrammar._add_attributed_production(ATOM,[RE_GROUP],single_ast_reductor)
    # ATOM -> REPEAT
    ReGrammar._add_attributed_production(ATOM,[REPEAT],single_ast_reductor)
    # ATOM -> CHAR_SET
    ReGrammar._add_attributed_production(ATOM,[CHAR_SET],single_ast_reductor)
    # ATOM -> ATOM *
    ReGrammar._add_attributed_production(ATOM,[ATOM,re_kleene_star],kleene_ast_reductor)
    # ATOM -> ATOM +
    ReGrammar._add_attributed_production(ATOM,[ATOM,re_positive_clousure],positive_clousure_ast_reductor)
    # ATOM -> ATOM ?
    ReGrammar._add_attributed_production(ATOM,[ATOM,re_optional],optional_ast_reductor)

    # CHAR -> re_char
    ReGrammar._add_attributed_production(CHAR,[re_char],char_ast_reductor)
    # CHAR -> re_escape_char
    ReGrammar._add_attributed_production(CHAR,[re_escape_char],char_ast_reductor)

    # RE_GROUP -> ( REGEX )
    ReGrammar._add_attributed_production(RE_GROUP,[re_lp,REGEX,re_rp],group_ast_reductor)

    # REPEAT -> CHAR { CHAR , CHAR }
    ReGrammar._add_attributed_production(REPEAT,[CHAR,re_lb,CHAR,re_com,CHAR,re_rb],repeat_ast_reductor)
    # REPEAT -> RE_GROUP { CHAR , CHAR }
    ReGrammar._add_attributed_production(REPEAT,[RE_GROUP,re_lb,CHAR,re_com,CHAR,re_rb],repeat_ast_reductor)
    # REPEAT -> re_constant { CHAR , CHAR }
    ReGrammar._add_attributed_production(REPEAT,[re_constant,re_lb,CHAR,re_com,CHAR,re_rb],repeat_re_constant_ast_reductor)
    # REPEAT -> CHAR_SET { CHAR , CHAR }
    ReGrammar._add_attributed_production(REPEAT,[CHAR_SET,re_lb,CHAR,re_com,CHAR,re_rb],repeat_ast_reductor)

    # CHAR_SET -> [ CHAR_SET_SEQUENCE ]
    ReGrammar._add_attributed_production(CHAR_SET,[re_lc,CHAR_SET_SEQUENCE,re_rc],char_set_ast_reductor)
    # CHAR_SET -> [ ^ CHAR_SET_SEQUENCE ]
    ReGrammar._add_attributed_production(CHAR_SET,[re_lc,re_accent,CHAR_SET_SEQUENCE,re_rc],char_set_ast_reductor)

    # CHAR_SET_SEQUENCE -> CHAR_SET_SEQUENCE_ATOM
    ReGrammar._add_attributed_production(CHAR_SET_SEQUENCE,[CHAR_SET_SEQUENCE_ATOM],single_ast_reductor)
    # CHAR_SET_SEQUENCE -> CHARSET_SEQUENCE CHAR_SET_SEQUENCE_ATOM
    ReGrammar._add_attributed_production(CHAR_SET_SEQUENCE,[CHAR_SET_SEQUENCE,CHAR_SET_SEQUENCE_ATOM],char_set_sequence_ast_reductor)

    # CHAR_SET_SEQUENCE_ATOM -> CHAR
    ReGrammar._add_attributed_production(CHAR_SET_SEQUENCE_ATOM,[CHAR],char_set_sequence_atom_ast_reductor)
    # CHAR_SET_SEQUENCE_ATOM -> CHAR - CHAR
    ReGrammar._add_attributed_production(CHAR_SET_SEQUENCE_ATOM,[CHAR,re_minus,CHAR],char_set_sequence_atom_ast_reductor)
   
    return _build_lalr_parser_from_attributed(ReGrammar)

cdef BaseLexer _build_regex_lexer():
    cdef BaseLexer RE_LEXER = BaseLexer(get_symbol_function,DFA('EMPTY','EMPTY',set())) # type:ignore
    cdef set[str] char_set = set(printable).difference(set(symbols_by_text.keys()).union(set(operatos_by_text)))
    
    char_set.discard('.')

    RE_LEXER._add_token(
        1,
        ReTokenType.CHAR,
        get_words_automaton_with_value(
            list(char_set),
            ReTokenType.CHAR,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        2,
        ReTokenType.CONSTANT_RE,
        get_words_automaton_with_value(
            [
                '\\d',
                '\\D',
                '\\s',
                '\\S',
                '\\w',
                '\\W',
                '.'
            ],
            ReTokenType.CONSTANT_RE,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        3,
        ReTokenType.OPERATOR,
        get_words_automaton_with_value(
            [
                '*',
                '+',
                '|',
                '?',
                '^'
            ],
            ReTokenType.OPERATOR,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        4,
        ReTokenType.SYMBOL,
        get_words_automaton_with_value(
            [
                '(',
                ')',
                '[',
                ']',
                '-',
                '{',
                '}',
                ','
            ],
            ReTokenType.SYMBOL,
            True # type:ignore
        )
    )
    RE_LEXER._add_token(
        5,
        ReTokenType.ESCAPE_CHAR,
        get_words_automaton_with_value(
            [
                '\\(',
                '\\)',
                '\\[',
                '\\]',
                '\\{',
                '\\}',
                '\\-',
                '\\*',
                '\\+',
                '\\?',
                '\\^',
                '\\|',
                '\\.',
                '\\,'
            ],
            ReTokenType.ESCAPE_CHAR,
            True # type:ignore
        )
    )
    RE_LEXER.initialize()
    return RE_LEXER