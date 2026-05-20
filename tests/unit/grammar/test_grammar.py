import pytest

from grammar.grammar import Grammar
from common.types import Symbol

class TestGrammar:

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