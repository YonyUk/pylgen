import pytest

from grammar.grammar import Grammar
from common.types import Symbol

class TestGrammar:

    @pytest.fixture
    def S(self) -> Symbol: return Symbol('S')

    @pytest.fixture
    def E(self) -> Symbol: return Symbol('E')

    @pytest.fixture
    def T(self) -> Symbol: return Symbol('T')

    @pytest.fixture
    def F(self) -> Symbol: return Symbol('F')

    @pytest.fixture
    def X(self) -> Symbol: return Symbol('X')

    @pytest.fixture
    def Y(self) -> Symbol: return Symbol('X')

    @pytest.fixture
    def Plus(self) -> Symbol: return Symbol('+',True)

    @pytest.fixture
    def Minus(self) -> Symbol: return Symbol('-',True)

    @pytest.fixture
    def Mul(self) -> Symbol: return Symbol('*',True)

    @pytest.fixture
    def n(self) -> Symbol: return Symbol('n',True)

    @pytest.fixture
    def epsilon(self) -> Symbol: return Symbol('e',True,True)

    def test_create_grammar(self,E:Symbol):
        G = Grammar(E)

        assert len(G.productions) == 0
        assert E in G.non_terminals
        assert len(G.non_terminals) == 1
        assert len(G.terminals) == 0
        assert G.start_symbol == E
    
    def test_creation_failed(self,Plus:Symbol):
        
        with pytest.raises(ValueError):
            G = Grammar(Plus)
    
    def test_add_productions(self,E:Symbol,T:Symbol,F:Symbol,Plus:Symbol,Minus:Symbol,Mul:Symbol):

        G = Grammar(E)

        G[E] += E,Plus,T

        assert len(G.non_terminals) == 2
        assert T in G.non_terminals
        assert len(G.terminals) == 1
        assert Plus in G.terminals

        G[E] += E,Minus,T

        assert len(G.non_terminals) == 2
        assert len(G.terminals) == 2
        assert Plus in G.terminals and Minus in G.terminals

        G[T] += T,Mul,F

        assert len(G.non_terminals) == 3
        assert F in G.non_terminals
        assert len(G.terminals) == 3
        assert Mul in G.terminals
    
    def test_add_production_failed(self,E:Symbol,T:Symbol,Plus:Symbol):
        G = Grammar(E)

        with pytest.raises(ValueError):
            G[Plus] += E,T