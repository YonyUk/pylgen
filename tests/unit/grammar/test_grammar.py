from typing import Tuple

import pytest

from grammar.grammar import Grammar,SymbolNotPresentInGrammarException
from common.types import Symbol

class TestGrammar:

    @pytest.fixture
    def G1(self):
        '''
        E -> T X

        X -> + T X

        X -> ε

        T -> ( E )

        T -> n
        '''
        E = Symbol('E')
        X = Symbol('X')
        T = Symbol('T')
        plus = Symbol('+',True)
        n = Symbol('n',True)
        lparen = Symbol('(',True)
        rparen = Symbol(')',True)
        eps = Symbol(chr(949),True,True) # ε symbol

        g = Grammar(E,'$')
        g[E] += T,X

        g[X] += plus,T,X
        g[X] += eps,

        g[T] += lparen,E,rparen
        g[T] += n,

        return g,(E,T,X,plus,n,lparen,rparen,eps)
    
    def test_grammar_initialization(self):
        E = Symbol('E')
        G = Grammar(E)

        assert G.start_symbol == E
        assert isinstance(G.productions,set)
        assert isinstance(G.terminals,set)
        assert isinstance(G.non_terminals,set)
        assert isinstance(G.symbols,set)
        assert len(G.productions) == 0
        assert len(G.terminals) == 1
        assert len(G.symbols) == 2
        assert G.end_symbol in G.terminals
        assert G.end_symbol.symbol == '\x00'
        assert len(G.non_terminals) == 1
        assert E in G.non_terminals
        assert E in G.symbols
        assert G.end_symbol in G.symbols
    
    @pytest.mark.parametrize("symbol",[
        '$',
        '#',
        '@'
    ])
    def test_grammar_initialization_with_custom_end_symbol(self,symbol:str):
        E = Symbol('E')
        G = Grammar(E,symbol)

        assert G.end_symbol.symbol == symbol
        assert G.end_symbol in G.terminals
    
    def test_add_one_production(self):
        E = Symbol('E')
        T = Symbol('T')
        plus = Symbol('+',True)

        G = Grammar(E)

        G[E] += E,plus,T
        assert len(G.productions) == 1
        prod = next(iter(G.productions))
        assert prod.head == E
        assert prod.production == [E,plus,T]
        assert len(G.terminals) == 2
        assert plus in G.terminals
        assert len(G.non_terminals) == 2
        assert T in G.non_terminals
        assert len(G.symbols) == 4
        assert plus in G.symbols
        assert G.end_symbol in G.symbols
        assert E in G.symbols
        assert T in G.symbols
    
    def test_add_many_productions_same_head(self):
        E = Symbol('E')
        T = Symbol('T')
        plus = Symbol('+',True)

        G = Grammar(E)

        G[E] += E,plus,T
        G[E] += T,

        assert len(G.productions) == 2
        prods = list(G.productions)
        for p in prods:
            assert p.head == E
            if len(p.production) == 1:
                assert p.production == [T]
            else:
                assert p.production == [E,plus,T]
        assert len(G.terminals) == 2
        assert plus in G.terminals
        assert len(G.non_terminals) == 2
        assert T in G.non_terminals
        assert len(G.symbols) == 4
        assert plus in G.symbols
        assert G.end_symbol in G.symbols
        assert E in G.symbols
        assert T in G.symbols
    
    def test_add_epsilon_production(self):
        E = Symbol('E')
        eps = Symbol('eps',True,True)

        G = Grammar(E)
        G[E] += eps,

        assert len(G.productions) == 1
        prod = next(iter(G.productions))
        assert prod.head == E
        assert prod.production == [eps]
        assert eps in G.terminals
        assert eps in G.symbols
    
    def test_grammar_terminals_and_non_terminals(self):
        E = Symbol('E')
        T = Symbol('T')
        plus = Symbol('+',True)
        n = Symbol('n',True)

        G = Grammar(E)
        G[E] += E,plus,T
        G[T] += n,

        assert E in G.non_terminals
        assert T in G.non_terminals
        assert plus in G.terminals
        assert n in G.terminals
        assert E in G.symbols
        assert T in G.symbols
        assert plus in G.symbols
        assert n in G.symbols
    
    def test_grammar_raises_head_terminal_not_allowed(self):
        E = Symbol('E')
        end = Symbol('end',True)

        G = Grammar(E)

        with pytest.raises(ValueError,match="head can't be a terminal symbol"):
            G[end] += E,end
    
    def test_grammar_bad_initialization(self):
        end = Symbol('end',True)

        with pytest.raises(ValueError,match="start_symbol can't be terminal"):
            G = Grammar(end)
    
    def test_grammar_unique_epsilon_symbol(self):
        E = Symbol('E')
        T = Symbol('T')
        eps1 = Symbol('eps1',True,True)
        eps2 = Symbol('eps2',True,True)

        G = Grammar(E)
        G[E] += T,eps1

        with pytest.raises(ValueError,match='Only can exists one epsilon symbol'):
            G[E] += T,eps2
    
    def test_grammar_first_1(self,G1:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(E,T,X,plus,n,lparen,rparen,eps) = G1

        # terminals
        assert G.first([plus]) == { plus }
        assert G.first([n]) == { n }
        assert G.first([lparen]) == { lparen }
        assert G.first([rparen]) == { rparen }

        # non-terminals
        assert G.first([E]) == { n, lparen }
        assert G.first([T]) == { n, lparen }
        assert G.first([X]) == { plus, eps }

        # symbols sequence
        assert G.first([T,X]) == { n, lparen }
        assert G.first([X,T]) == { plus, n, lparen }
    
        # symbol not present in grammar
        with pytest.raises(SymbolNotPresentInGrammarException):
            G.first([Symbol('Unknown')])