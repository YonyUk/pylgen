import pytest
from typing import Iterable, List
from string import digits

from pylgen.common.types import Symbol,AST,Token
from pylgen.common.enums import TokenType
from pylgen.grammar.grammar import AttributedGrammar
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.parser.parser import BottomUpParser,ParsingException
from pylgen.lexer.base_lexer import BaseLexer
from pylgen.lexer.lexer import Lexer
from pylgen.analisis.lexical import LexicRule
from pylgen.automaton.automaton import NFA, State,DFA,get_words_automaton_with_value

END_SYMBOL = '$'

E = Symbol('E')
T = Symbol('T')
F = Symbol('F')
P = Symbol('P')

plus = Symbol('+',True)
minus = Symbol('-',True)
mod = Symbol('%',True)
mul = Symbol('*',True)
div = Symbol('/',True)
exp = Symbol('**',True)
n = Symbol('n',True)
lp = Symbol('(',True)
rp = Symbol(')',True)

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

class MinusAST(BinaryAST):
    
    def __init__(self,line: int, column: int):
        super().__init__(minus, line, column)

class ModAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(mod, line, column)

class MulAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(mul, line, column)

class DivAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(div, line, column)

class ExpAST(BinaryAST):

    def __init__(self,line: int, column: int):
        super().__init__(exp, line, column)

def reductor_E_plus_T(asts:List[AST]) -> AST:
    result = PlusAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result

def reductor_E_minus_T(asts:List[AST]) -> AST:
    result = MinusAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result

def reductor_E_mod_T(asts:List[AST]) -> AST:
    result = ModAST(asts[1].line,asts[1].column)
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

def reductor_T_div_F(asts:List[AST]) -> AST:
    result = DivAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result

def reductor_F_exp_P(asts:List[AST]) -> AST:
    result = ExpAST(asts[1].line,asts[1].column)
    result.left = asts[0]
    result.right = asts[2]
    return result

def reductor_F_lp_E_rp(asts:List[AST]) -> AST:
    return asts[1]

G1 = AttributedGrammar(E,END_SYMBOL)

G1[E] += (E,plus,T),reductor_E_plus_T
G1[E] += (T,),reductor_E_T
G1[T] += (T,mul,F),reductor_T_mul_F
G1[T] += (F,),reductor_E_T
G1[F] += (lp,E,rp),reductor_F_lp_E_rp
G1[F] += (n,),reductor_E_T

G2 = AttributedGrammar(E,END_SYMBOL)

G2[E] += (E,plus,T),reductor_E_plus_T
G2[E] += (E,minus,T),reductor_E_minus_T
G2[E] += (T,),reductor_E_T

G2[T] += (T,mul,F),reductor_T_mul_F
G2[T] += (T,div,F),reductor_T_div_F
G2[T] += (F,),reductor_E_T

G2[F] += (lp,E,rp),reductor_F_lp_E_rp
G2[F] += (n,),reductor_E_T

G3 = AttributedGrammar(E,END_SYMBOL)

G3[E] += (E,plus,T),reductor_E_plus_T
G3[E] += (E,minus,T),reductor_E_minus_T
G3[E] += (E,mod,T),reductor_E_mod_T
G3[E] += (T,),reductor_E_T

G3[T] += (T,mul,F),reductor_T_mul_F
G3[T] += (T,div,F),reductor_T_div_F
G3[T] += (F,),reductor_E_T

G3[F] += (F,exp,P),reductor_F_exp_P
G3[F] += (P,),reductor_E_T

G3[P] += (lp,E,rp),reductor_F_lp_E_rp
G3[P] += (n,),reductor_E_T

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'

class NumberLexicRule(LexicRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')
    
    def _check(self, text: str):
        return str(int(text)) == text

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return n
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    return Symbol(tx,True)

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
            '*',
            '-',
            '/',
            '**',
            '%'
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
    def lexer1(self,ignore_dfa:DFA):
        lexer = Lexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
        lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%'
        return lexer
    
    @pytest.fixture
    def parser1(self) -> BottomUpParser:
        parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G1,ParserType.LALR1) # type: ignore
        return parser
    
    @pytest.fixture
    def parser2(self) -> BottomUpParser:
        parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G2,ParserType.LALR1) # type: ignore
        return parser
    
    @pytest.fixture
    def parser3(self) -> BottomUpParser:
        parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1) # type: ignore
        return parser

    @pytest.mark.parametrize("text",[
        "12 + 4",
        "9 *3",
        "(8*5)",
        "7 +5",
        "9+ 2",
        "9+4*5",
        "(1 + 3)* (5+7) *(2 +10 * 15)"
    ])
    def test_simple_arithmetic_parser_1(self,text:str,lexer:BaseLexer,parser1:BottomUpParser):
        lexer.load_text(text)
        ast = parser1.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
    
    @pytest.mark.parametrize("text",[
        "12 + 4",
        "9 *3",
        "(8*5)",
        "7 +5",
        "9+ 2",
        "9+4*5",
        "(1 + 3)* (5+7) *(2 +10 * 15)"
    ])
    def test_simple_arithmetic_parser_2(self,text:str,lexer1:Lexer,parser1:BottomUpParser):
        lexer1.load_text(text)
        ast = parser1.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
    
    @pytest.mark.parametrize("text",[
        "1-2",
        "4 / 2",
        "1 -2/4",
        "(1 - 5) / 10",
        "1 + 4 * (3/2) - 9"
    ])
    def test_normal_arithmetic_parser_1(self,text:str,lexer:BaseLexer,parser2:BottomUpParser):
        lexer.load_text(text)
        ast = parser2.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
    
    @pytest.mark.parametrize("text",[
        "1-2",
        "4 / 2",
        "1 -2/4",
        "(1 - 5) / 10",
        "1 + 4 * (3/2) - 9"
    ])
    def test_normal_arithmetic_parser_2(self,text:str,lexer1:Lexer,parser2:BottomUpParser):
        lexer1.load_text(text)
        ast = parser2.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
    
    @pytest.mark.parametrize("text",[
        " 2 % 1",
        " 3 ** 2",
        " 23+342 / (4**9 + 10) -235/4 + 20**3%3"
    ])
    def test_extended_arithmetic_parser_1(self,text:str,lexer:BaseLexer,parser3:BottomUpParser):
        lexer.load_text(text)
        ast = parser3.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
    
    @pytest.mark.parametrize("text",[
        " 2 % 1",
        " 3 ** 2",
        " 23+342 / (4**9 + 10) -235/4 + 20**3%3"
    ])
    def test_extended_arithmetic_parser_2(self,text:str,lexer1:Lexer,parser3:BottomUpParser):
        lexer1.load_text(text)
        ast = parser3.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
    
    def test_error_detecting_1(self,lexer1:Lexer,parser1:BottomUpParser):
        text = "(01 + 3)* (5+7) *(2 +010 * 15)"
        lexer1.add_rule(TokenTypeEnum.NUMBER,NumberLexicRule())
        
        lexer1.load_text(text)
        try:
            ast = parser1.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
        except ParsingException:
            pass

        errors = [(1,2),(1,22)]
        assert len(lexer1.errors) == 2
        for error in lexer1.errors:
            assert (error.line,error.column) in errors
        parser1.reset()
        text = "(1 + 3) * (5++7) *(2 + 10 * * 15)"
        lexer1.load_text(text)
        try:
            ast = parser1.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
        except ParsingException:
            pass
        assert len(parser1.errors) == 2
    
    def test_error_detecting_2(self,lexer1:Lexer,parser3:BottomUpParser):
        lexer1.add_rule(TokenTypeEnum.NUMBER,NumberLexicRule())
        text = '23+0342 / (4**9 + + 10) -0235//4 9 + 20**3%3'

        lexer1.load_text(text)
        try:
            ast = parser3.parse(get_tokens(Symbol(END_SYMBOL,True),lexer1.tokens))
        except ParsingException:
            pass
        
        assert len(lexer1.errors) == 2
        assert len(parser3.errors) == 3