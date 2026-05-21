from typing import Tuple

import pytest

from grammar.grammar import Grammar,SymbolNotPresentInGrammarException,Production
from common.types import Symbol

class TestGrammar:

    @pytest.fixture
    def G1(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
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
    
    # LR clasic grammar
    @pytest.fixture
    def G2(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        E -> E + T | T

        T -> n | ( E )
        '''
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        lparen = Symbol('(',True)
        rparen = Symbol(')',True)
        n = Symbol('n',True)

        g = Grammar(E,'$')

        g[E] += E,plus,T
        g[E] += T,
    
        g[T] += lparen,E,rparen
        g[T] += n,

        return g,(E,T,plus,lparen,rparen,n)

    # grammar with multiple ε-derivations in sequence
    @pytest.fixture
    def G3(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        S -> A B C

        A -> a | ε

        B -> b | ε

        C -> c | ε
        '''

        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')
        C = Symbol('C')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        eps = Symbol('ε',True,True)

        g = Grammar(S,'$')

        g[S] += A,B,C
        
        g[A] += a,
        g[A] += eps,

        g[B] += b,
        g[B] += eps,

        g[C] += c,
        g[C] += eps,

        return g,(S,A,B,C,a,b,c,eps)

    # grammar with n-direct ε-derivation
    @pytest.fixture
    def G4(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        S -> A

        A -> B

        B -> a | ε
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        eps = Symbol('ε',True,True)

        g = Grammar(S,'$')

        g[S] += A,

        g[A] += B,
    
        g[B] += a,
        g[B] += eps,

        return g,(S,A,B,a,eps)

    # grammar with a symbol repeated twice in the same derivation
    @pytest.fixture
    def G5(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        S -> A a A

        A -> b | c
        '''

        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        g = Grammar(S,'$')

        g[S] += A,a,A

        g[A] += b,
        g[A] += c,

        return g,(S,A,a,b,c)

    # ciclic grammar
    @pytest.fixture
    def G6(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        A -> B

        A -> a

        B -> A
        '''
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)

        g = Grammar(A,'$')

        g[A] += B,
        g[A] += a,

        g[B] += A,

        return g,(A,B,a)

    # simple terminal grammar
    @pytest.fixture
    def G7(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        S -> a
        '''
        S = Symbol('S')
        a = Symbol('a',True)

        g = Grammar(S,'$')

        g[S] += a,

        return g,(S,a)

    # left-regular grammar
    @pytest.fixture
    def G8(self) -> Tuple[Grammar,Tuple[Symbol,...]]:
        '''
        S -> A a | a
        
        S -> B b | b
        
        A -> A a | B | ε

        B -> B b | A | ε
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        g = Grammar(S)

        g[S] += A,a
        g[S] += B,b
        g[S] += a,
        g[S] += b,

        g[A] += A,a
        g[A] += B,
        g[A] += eps,

        g[B] += B,b
        g[B] += A,
        g[B] += eps,
    
        return g,(S,A,B,a,b,eps)

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
    
    def test_grammar_first(self,G1:Tuple[Grammar,Tuple[Symbol,...]]):
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
    
    def test_grammar_follow(self,G1:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(E,T,X,plus,n,lparen,rparen,eps) = G1

        # follow(E) = { $, ) }
        follow = G.follow(E)
        assert follow == { G.end_symbol, rparen }

        # follow(X) = { $, ) }
        follow = G.follow(X)
        assert follow == { G.end_symbol, rparen }

        # follow(T) = { $, ), + }
        follow = G.follow(T)
        assert follow == { G.end_symbol, rparen, plus }

        # symbol not present in grammar
        with pytest.raises(SymbolNotPresentInGrammarException):
            G.follow(Symbol('Unknown'))
    ################################################################
    # more tests for first and follow
    ################################################################
    def test_grammar_1(self,G2:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(E,T,plus,lparen,rparen,n) = G2

        # first(E) = first(T) = { n, ( }
        assert G.first([E]) == { n, lparen }
        assert G.first([T]) == { n, lparen }
        # first( + T ) = { + }
        assert G.first([plus,T]) == { plus }
        # follow(E) = follow(T) = { $, +, ) }
        assert G.follow(E) == { G.end_symbol, plus, rparen }
        assert G.follow(T) == { G.end_symbol, plus, rparen }
    
    def test_grammar_2(self,G3:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(S,A,B,C,a,b,c,eps) = G3

        # first(S) = { a, b, c, ε }
        assert G.first([S]) == { a, b, c, eps}
        # first(A) = { a, ε }
        assert G.first([A]) == { a, eps }
        # first(B) = { b, ε }
        assert G.first([B]) == { b, eps }
        # first(C) = { c, ε }
        assert G.first([C]) == { c, eps }
        # first( A B ) = { a, b, ε }
        assert G.first([A,B]) == { a, b, eps }
        # first( B C ) = { b, c, eps}

        # follow(A) = { b, c, $ }
        assert G.follow(A) == { b, c, G.end_symbol }
        # follow(B) = { c, $ }
        assert G.follow(B) == { c, G.end_symbol }
        # follow(C) = { $ }
        assert G.follow(C) == { G.end_symbol }
    
    def test_grammar_3(self,G4:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(S,A,B,a,eps) = G4

        # first(S) = first(A) = first(B) = { a, ε }
        assert G.first([S]) == { a, eps }
        assert G.first([A]) == { a, eps }
        assert G.first([B]) == { a, eps }

        # follow(S) = follow(A) = follow(B) = { $ }
        assert G.follow(S) == { G.end_symbol }
        assert G.follow(A) == { G.end_symbol }
        assert G.follow(B) == { G.end_symbol }
    
    def test_grammar_4(self,G5:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(S,A,a,b,c) = G5

        # first(S) = first(A) = { b, c }
        assert G.first([S]) == { b, c }
        assert G.first([A]) == { b, c }
        # follow(A) = { a, $ }
        assert G.follow(A) == { a, G.end_symbol }

    def test_grammar_5(self,G6:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(A,B,a) = G6

        # first(A) = first(B) = { a }
        assert G.first([A]) == { a }
        assert G.first([B]) == { a }

        # follow(A) = follow(B) = { $ }
        assert G.follow(A) == { G.end_symbol }
        assert G.follow(B) == { G.end_symbol }
    
    def test_grammar_6(self,G7:Tuple[Grammar,Tuple[Symbol,...]]):
        G,(S,a) = G7

        # first(S) = { a }
        assert G.first([S]) == { a }
        # follow(S) = { $ }
        assert G.follow(S) == { G.end_symbol }
        # follow(a) = ∅
        assert len(G.follow(a)) == 0
    
    @pytest.mark.parametrize("g",[
        G1,
        G2,
        G3,
        G4,
        G5,
        G6,
        G7,
        G8
    ])
    def test_augment_grammar(self,g):
        G,_ = g._get_wrapped_function()(self)

        A = Grammar.AugmentGrammar(G)

        g_prods = G.productions
        a_prods = A.productions
        assert g_prods.issubset(a_prods)
        prod = Production(A.start_symbol,[G.start_symbol])
        assert prod in a_prods

    @pytest.mark.parametrize("g",[
        G1,
        G2,
        G3,
        G4,
        G5,
        G6,
        G7,
        G8
    ])
    def test_reverse_grammar(self,g):
        G,_ = g._get_wrapped_function()(self)

        R = Grammar.Reverse(G)

        R_prods = R.productions

        for p in G.productions:
            np = p.production
            np.reverse()
            pr = Production(p.head,np)
            assert pr in R_prods

    def test_grammar_regularity_1(self,G8:Tuple[Grammar,Tuple[Symbol,...]]):
        GL,_ = G8

        GR = Grammar.Reverse(GL)
        
        assert Grammar.IsRegular(GL)
        assert Grammar.IsLeftRegular(GL)
        assert not Grammar.IsRightRegular(GL)

        assert Grammar.IsRegular(GR)
        assert Grammar.IsRightRegular(GR)
        assert not Grammar.IsLeftRegular(GR)
    
    def test_grammar_regularity_2(self,G4:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G4

        assert Grammar.IsLeftRegular(G)
        assert Grammar.IsRightRegular(G)
        assert Grammar.IsRegular(G)
    
    def test_grammar_regularity_3(self,G6:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G6

        assert Grammar.IsLeftRegular(G)
        assert Grammar.IsRightRegular(G)
        assert Grammar.IsRegular(G)
    
    def test_grammar_regularity_4(self,G7:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G7

        assert Grammar.IsLeftRegular(G)
        assert Grammar.IsRightRegular(G)
        assert Grammar.IsRegular(G)
    
    def test_grammar_irregularity_1(self,G1:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G1
        
        assert not Grammar.IsRegular(G)
    
    def test_grammar_irregularity_2(self,G2:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G2

        assert not Grammar.IsRegular(G)
    
    def test_grammar_irregularity_3(self,G3:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G3

        assert not Grammar.IsRegular(G)
    
    def test_grammar_irregularity_4(self,G5:Tuple[Grammar,Tuple[Symbol,...]]):
        G,_ = G5

        assert not Grammar.IsRegular(G)