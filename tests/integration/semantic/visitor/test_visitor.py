from typing import Iterable, List

import pytest

from analisis.error import SemanticError
from common.types import Symbol,AST,Token
from common.enums import TokenType
from grammar.grammar import AttributedGrammar
from parser.parser_builder import ParserBuilder
from parser.parser_type import ParserType
from parser.parser import BottomUpParser,ParsingException
from lexer.lexer import Lexer
from analisis.lexical import LexicRule
from automaton.automaton import DFA
from analisis.visitor import ASTChildrenSelector,ASTVisitor,ASTWalker

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
        self._left:AST = None # type: ignore
        self._right:AST = None # type: ignore

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
    
    def children(self) -> List[AST]:
        return [self._left,self._right]

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

class BinaryASTVisitor(ASTVisitor):

    def visit(self, ast: AST) -> SemanticError | None:
        if isinstance(ast,DivAST) or isinstance(ast,ModAST):
            if isinstance(ast.right,Token):
                if int(ast.right.text) == 0:
                    return SemanticError('Division by zero',ast.line,ast.column)
        return None

class BinaryASTSelector(ASTChildrenSelector):

    def select_children(self, ast: AST) -> List[AST]:
        return ast.children()

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

error_collector_ast_walker = ASTWalker()

error_collector_ast_walker.add_visitor(PlusAST,BinaryASTVisitor())
error_collector_ast_walker.add_visitor(MinusAST,BinaryASTVisitor())
error_collector_ast_walker.add_visitor(MulAST,BinaryASTVisitor())
error_collector_ast_walker.add_visitor(DivAST,BinaryASTVisitor())
error_collector_ast_walker.add_visitor(ExpAST,BinaryASTVisitor())
error_collector_ast_walker.add_visitor(ModAST,BinaryASTVisitor())

error_collector_ast_walker.add_selector(PlusAST,BinaryASTSelector())
error_collector_ast_walker.add_selector(MinusAST,BinaryASTSelector())
error_collector_ast_walker.add_selector(MulAST,BinaryASTSelector())
error_collector_ast_walker.add_selector(DivAST,BinaryASTSelector())
error_collector_ast_walker.add_selector(ExpAST,BinaryASTSelector())
error_collector_ast_walker.add_selector(ModAST,BinaryASTSelector())

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

ignore_dfa = DFA('start','start',{' ','\n','\t'},True)
ignore_dfa += ignore_dfa.start_state,' ',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\n',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\t',ignore_dfa.start_state

class TestVisitor:

    @pytest.fixture
    def lexer(self) -> Lexer:
        lexer = Lexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
        lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%'

        lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicRule())
    
        return lexer

    @pytest.fixture
    def parser(self) -> BottomUpParser:
        return ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1) # type: ignore

    def test_errors_and_clean_errors(self,lexer:Lexer,parser:BottomUpParser):
        text = '23+0342 / (4**9 + 10) - 0235 / 0 + 20**3%0000'

        lexer.load_text(text)
        try:
            ast = parser.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
            error_collector_ast_walker.walk(ast)
        except ParsingException:
            pass
        
        assert len(error_collector_ast_walker.errors) == 2
        error_collector_ast_walker.reset()
        assert len(error_collector_ast_walker.errors) == 0
    
    def test_no_errors(self,lexer:Lexer,parser:BottomUpParser):
        text = '23+342 / (4**9 + 10) - 235 / 2 + 20**3%4'

        lexer.load_text(text)
        try:
            ast = parser.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
            error_collector_ast_walker.walk(ast)
        except ParsingException:
            pass
        
        assert len(error_collector_ast_walker.errors) == 0