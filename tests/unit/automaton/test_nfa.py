import pytest
from typing import Set

from automaton import State,DFA,NFA

class TestNFA:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'0','1'}
    
    @pytest.fixture
    def nfa(self,alphabet:Set[str]) -> NFA:
        return NFA('start','start',alphabet)
    
    def test_nfa_add_epsilon_transition_1(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(nfa.start_state,q1)

        clousure = nfa.clousure(nfa.start_state)

        assert len(clousure) == 3
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure

        clousure = nfa.clousure(q0)
        assert len(clousure) == 1
        assert q0 in clousure
    
        clousure = nfa.clousure(q1)
        assert len(clousure) == 1
        assert q1 in clousure

    def test_nfa_add_epsilon_transition_2(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)

        clousure = nfa.clousure(nfa.start_state)

        assert len(clousure) == 3
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure
        assert q1 in nfa.finals

        clousure = nfa.clousure(q0)

        assert len(clousure) == 2
        assert q0 in clousure
        assert q1 in clousure

        clousure = nfa.clousure(q1)

        assert len(clousure) == 1
        assert q1 in clousure
    
    def test_nfa_add_epsilon_transition_3(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)
        nfa.add_epsilon_transition(q1,nfa.start_state)

        clousure = nfa.clousure(nfa.start_state)

        assert len(clousure) == 3
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure
        assert q1 in nfa.finals

        clousure = nfa.clousure(q0)

        assert len(clousure) == 3
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure

        clousure = nfa.clousure(q1)

        assert len(clousure) == 3
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure
    
    def test_nfa_add_epsilon_transition_4(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)
        q2 = State('q2','q2')

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)
        nfa.add_epsilon_transition(q1,q2)
        nfa.add_epsilon_transition(q2,q0)
        
        clousure = nfa.clousure(nfa.start_state)

        assert len(clousure) == 4
        assert nfa.start_state in clousure
        assert q0 in clousure
        assert q1 in clousure
        assert q2 in clousure
        assert q1 in nfa.finals

        clousure = nfa.clousure(q0)

        assert len(clousure) == 3
        assert q0 in clousure
        assert q1 in clousure
        assert q2 in clousure

        clousure = nfa.clousure(q1)

        assert len(clousure) == 3
        assert q0 in clousure
        assert q1 in clousure
        assert q2 in clousure

        clousure = nfa.clousure(q2)

        assert len(clousure) == 3
        assert q0 in clousure
        assert q1 in clousure
        assert q2 in clousure