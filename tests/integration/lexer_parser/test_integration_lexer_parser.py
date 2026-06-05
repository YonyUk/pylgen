import pytest
from typing import Iterable, List
from string import digits

from common.types import Symbol,AST,Token
from common.enums import TokenType
from grammar.grammar import Grammar,Production
from parser.parser_builder import ParserBuilder
from parser.parser_type import ParserType
from parser.parser import BottomUpParser
from lexer.lexer import BaseLexer
from automaton.automaton import NFA, State,DFA,get_words_automaton_with_value

END_SYMBOL = '$'

E = Symbol('E')
T = Symbol('T')
F = Symbol('F')

plus = Symbol('+',True)
mul = Symbol('*',True)
n = Symbol('n',True)
lp = Symbol('(',True)
rp = Symbol(')',True)

G1 = Grammar(E,END_SYMBOL)

G1[E] += E,plus,T
G1[E] += T,
G1[T] += T,mul,F
G1[T] += F,
G1[F] += lp,E,rp
G1[F] += n,

class BinaryAST(AST):

    def __init__(self, symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
        self._left = None
        self._right = None

    @property
    def left(self) -> AST:
        return self._left # type:ignore
    
    @property
    def right(self) -> AST:
        return self._right # type: ignore

    @left.setter
    def left(self,value:AST) -> None:
        self._left = value
    
    @right.setter
    def right(self,value:AST) -> None:
        self._right = value

class PlusAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(plus, line, column)

class MulAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(mul, line, column)

def reductor_E_plus_T(asts:List[AST]) -> AST:
    result = PlusAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result
        
def reductor_E_T(asts:List[AST]) -> AST:
    return asts[0]
        
def reductor_T_mul_F(asts:List[AST]) -> AST:
    result = MulAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result
        
def reductor_T_F(asts:List[AST]) -> AST:
    return asts[0]
        
def reductor_F_lp_E_rp(asts:List[AST]) -> AST:
    return asts[1]
        
def reductor_F_n(asts:List[AST]) -> AST:
    return asts[0]

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return n
    if t == TokenTypeEnum.SYMBOL:
        if tx == '(':
            return lp
        if tx == ')':
            return rp
        return Symbol(END_SYMBOL,True)
    if tx == '+':
        return plus
    return mul

def get_tokens(end_symbol:Symbol,tokens:Iterable[Token]):
    line = 0
    column = 0
    for token in tokens:
        line = token.line
        column = token.column
        yield token
    yield Token(end_symbol.symbol,TokenTypeEnum.SYMBOL,end_symbol,line,column + 1)

class TestIntegrationLexerParser:

    @pytest.fixture
    def symbols(self) -> List[str]:
        return [
            '(',
            ')'
        ]
    
    @pytest.fixture
    def operators(self) -> List[str]:
        return [
            '+',
            '*'
        ]

    @pytest.fixture
    def ignore_dfa(self) -> DFA:
        ignore_dfa = DFA('start','start',{' ','\n','\t'},True)
        ignore_dfa += ignore_dfa.start_state,' ',ignore_dfa.start_state
        ignore_dfa += ignore_dfa.start_state,'\n',ignore_dfa.start_state
        ignore_dfa += ignore_dfa.start_state,'\t',ignore_dfa.start_state
        return ignore_dfa
    
    @pytest.fixture
    def numbers_dfa(self) -> DFA:
        number_dfa = DFA('start','start',set(digits))
        number = State('number',TokenTypeEnum.NUMBER,True)

        for digit in digits:
            number_dfa += number_dfa.start_state,digit,number
            number_dfa += number,digit,number
        
        return number_dfa
    
    @pytest.fixture
    def symbols_dfa(self,symbols:List[str]) -> NFA:
        return get_words_automaton_with_value(symbols,TokenTypeEnum.SYMBOL,True)
    
    @pytest.fixture
    def operators_dfa(self,operators:List[str]) -> NFA:
        return get_words_automaton_with_value(operators,TokenTypeEnum.OPERATOR,True)
    
    @pytest.fixture
    def lexer(self,ignore_dfa:DFA,numbers_dfa:DFA,symbols_dfa:NFA,operators_dfa:NFA) -> BaseLexer:
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeEnum.NUMBER] = numbers_dfa
        lexer[1,TokenTypeEnum.SYMBOL] = symbols_dfa
        lexer[2,TokenTypeEnum.OPERATOR] = operators_dfa
        return lexer
    
    @pytest.fixture
    def parser1(self) -> BottomUpParser:
        parser:BottomUpParser = ParserBuilder.build_parser(G1,ParserType.LALR1) # type: ignore
        parser[Production(E,[E,plus,T])] = reductor_E_plus_T
        parser[Production(E,[T])] = reductor_E_T
        parser[Production(T,[T,mul,F])] = reductor_T_mul_F
        parser[Production(T,[F])] = reductor_T_F
        parser[Production(F,[lp,E,rp])] = reductor_F_lp_E_rp
        parser[Production(F,[n])] = reductor_F_n
        return parser
    
    @pytest.mark.parametrize("text",[
        "12 + 4",
        "9 *3",
        "(8*5)",
        "7 +5",
        "9+ 2"
    ])
    def test_simple_arithmetic_parser(self,text:str,lexer:BaseLexer,parser1:BottomUpParser):
        lexer.load_text(text)
        tokens = list(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
        input(tokens)
        ast = parser1.parse(tokens)