from typing import Iterable, List

import pytest
import networkx as nx

from pylgen.visual import _ast_to_graph,_get_graph_from_parse_tree
from pylgen.grammar import AttributedGrammar
from pylgen.common.types import Symbol,AST,ASTListView, Token
from pylgen.common.enums import TokenType
from pylgen.lexer import Lexer
from pylgen.parser import Parser,ParserBuilder,ParserType,ParseTreeNode

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

    def __init__(self, symbol: Symbol,left:AST,right:AST):
        (s_l,s_c),(e_l,e_c) = left.start_position,right.end_position
        super().__init__(symbol, s_l,s_c,e_l,e_c)
        self._left = left
        self._right = right
        self._children = [left,right]

    @property
    def left(self) -> AST:
        return self._left # type:ignore
    
    @property
    def right(self) -> AST:
        return self._right # type: ignore

    def children(self) -> List[AST]:
        return self._children

class PlusAST(BinaryAST):

    def __init__(self,left:AST,right:AST):
        super().__init__(plus, left,right)

class MinusAST(BinaryAST):
    
    def __init__(self,left:AST,right:AST):
        super().__init__(minus, left,right)

class ModAST(BinaryAST):

    def __init__(self,left:AST,right:AST):
        super().__init__(mod, left,right)

class MulAST(BinaryAST):

    def __init__(self,left:AST,right:AST):
        super().__init__(mul, left,right)

class DivAST(BinaryAST):

    def __init__(self,left:AST,right:AST):
        super().__init__(div, left,right)

class ExpAST(BinaryAST):

    def __init__(self,left:AST,right:AST):
        super().__init__(exp,left,right)

def reductor_E_plus_T(asts:ASTListView) -> AST:
    result = PlusAST(asts[0],asts[2])
    return result

def reductor_E_minus_T(asts:ASTListView) -> AST:
    result = MinusAST(asts[0],asts[2])
    return result

def reductor_E_mod_T(asts:ASTListView) -> AST:
    result = ModAST(asts[0],asts[2])
    return result

def reductor_E_T(asts:ASTListView) -> AST:
    return asts[0]
        
def reductor_T_mul_F(asts:ASTListView) -> AST:
    result = MulAST(asts[0],asts[2])
    return result

def reductor_T_div_F(asts:ASTListView) -> AST:
    result = DivAST(asts[0],asts[2])
    return result

def reductor_F_exp_P(asts:ASTListView) -> AST:
    result = ExpAST(asts[0],asts[2])
    return result

def reductor_F_lp_E_rp(asts:ASTListView) -> AST:
    return asts[1]

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
        line,column = token.start_position
        yield token
    yield Token(end_symbol.symbol,TokenTypeEnum.SYMBOL,end_symbol,line,column + 1)

def is_cyclic(graph:nx.DiGraph,root:AST|ParseTreeNode,parse_tree:bool=False) -> bool:
    (sl,sc),(el,ec) = root.start_position,root.end_position
    if parse_tree:
        node_id = f'{root.symbol.symbol}-{sl}-{sc}-{el}-{ec}-0'
    else:
        node_id = f'{sl}-{sc}-{el}-{ec}-0'
    node = graph.nodes[node_id]

    seens = []
    work_list = [node]

    while work_list:
        current = work_list[-1]
        change = False
        for u,child in graph.edges:
            if u == current:
                if child in seens:
                    continue
                if child in work_list:
                    return True
                change = True
                work_list.append(child)
        if not change:
            seens.append(work_list.pop())

    return False

class TestGraphDrawing:

    @pytest.fixture
    def ignore_pattern(self) -> str:
        return '\n|\t| '

    @pytest.fixture
    def lexer(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
        lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%'
        lexer.set_eof_token(END_SYMBOL,TokenTypeEnum.SYMBOL)
        return lexer

    @pytest.fixture
    def parser(self) -> Parser:
        parser = ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1)
        return parser

    @pytest.mark.parametrize("sample",[
        '1 + 2',
        '1 - 3',
        '1 + 2 * 4',
        '(1 + 2) * 4',
        "4 / 2",
        "1 -2/4",
        "(1 - 5) / 10",
        "1 + 4 * (3/2) - 9",
        " 2 % 1",
        " 3 ** 2",
        " 23+342 / (4**9 + 10) -235/4 + 20**3%3"
    ])
    def test_ast_to_graph(self,sample:str,lexer:Lexer,parser:Parser):
        lexer.load_text(sample)
        ast = parser.parse(lexer.tokens)
        graph = _ast_to_graph(ast)
        assert not is_cyclic(graph,ast)

    @pytest.mark.parametrize("sample",[
        '1 + 2',
        '1 - 3',
        '1 + 2 * 4',
        '(1 + 2) * 4',
        "4 / 2",
        "1 -2/4",
        "(1 - 5) / 10",
        "1 + 4 * (3/2) - 9",
        " 2 % 1",
        " 3 ** 2",
        " 23+342 / (4**9 + 10) -235/4 + 20**3%3"
    ])
    def test_get_graph_from_parse_tree(self,sample:str,lexer:Lexer,parser:Parser):
        lexer.load_text(sample)
        parser.set_draw_parse_tree_flag(True)
        _ = parser.parse(lexer.tokens)
        tree = parser.parse_tree
        graph = _get_graph_from_parse_tree(tree)
        assert not is_cyclic(graph,tree,True)
        