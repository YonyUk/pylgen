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
    
    @pytest.fixture
    def nfa_0_1_terminated(self,alphabet:Set[str]) -> NFA:
        nfa = NFA('q0','q0',alphabet)

        q1 = State('q1','q1')
        q2 = State('q2','q2')
        q3 = State('q3','q3',True)

        nfa.add_transition(nfa.start_state,nfa.start_state,'0')
        nfa.add_transition(nfa.start_state,nfa.start_state,'1')

        nfa.add_epsilon_transition(nfa.start_state,q1)

        nfa.add_transition(q1,q2,'0')
        nfa.add_transition(q2,q3,'1')

        return nfa
    
    @pytest.fixture
    def nfa_zeros_or_ones(self,alphabet:Set[str]) -> NFA:
        nfa = NFA('q0','q0',alphabet)

        q1 = State('q1','q1')
        q2 = State('q2','q2',True)

        q3 = State('q3','q3')
        q4 = State('q4','q4',True)

        nfa.add_epsilon_transition(nfa.start_state,q1)
        nfa.add_epsilon_transition(nfa.start_state,q3)

        nfa.add_transition(q1,q2,'0')
        nfa.add_transition(q2,q2,'0')

        nfa.add_transition(q3,q4,'1')
        nfa.add_transition(q4,q4,'1')

        return nfa

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
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('1',False),
        ('0',False),
        ('10',False),
        ('01',True),
        ('101',True),
        ('010',False),
        ('101010',False),
        ('10101',True),
        ('000001',True),
        ('111110',False),
    ])
    def test_nfa_to_dfa_1(self,string:str,should_accept:bool,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        assert dfa.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '1'*3,
        '0'*3,
        '0101001001',
        '11010101',
        '111111110',
        '00000001'
    ])
    def test_nfa_to_dfa_2(self,string:str,nfa_zeros_or_ones:NFA):
        dfa = nfa_zeros_or_ones.to_deterministic()

        assert dfa.accept(list(string)) == (len(set(string)) == 1)