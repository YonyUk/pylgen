import pytest
from typing import Set

from pylgen.automaton import State,DFA,NFA

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

        closure = nfa.closure(nfa.start_state)

        assert len(closure) == 3
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure

        closure = nfa.closure(q0)
        assert len(closure) == 1
        assert q0 in closure
    
        closure = nfa.closure(q1)
        assert len(closure) == 1
        assert q1 in closure

    def test_nfa_add_epsilon_transition_2(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)

        closure = nfa.closure(nfa.start_state)

        assert len(closure) == 3
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure
        assert q1 in nfa.finals

        closure = nfa.closure(q0)

        assert len(closure) == 2
        assert q0 in closure
        assert q1 in closure

        closure = nfa.closure(q1)

        assert len(closure) == 1
        assert q1 in closure
    
    def test_nfa_add_epsilon_transition_3(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)
        nfa.add_epsilon_transition(q1,nfa.start_state)

        closure = nfa.closure(nfa.start_state)

        assert len(closure) == 3
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure
        assert q1 in nfa.finals

        closure = nfa.closure(q0)

        assert len(closure) == 3
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure

        closure = nfa.closure(q1)

        assert len(closure) == 3
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure
    
    def test_nfa_add_epsilon_transition_4(self,nfa:NFA):

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)
        q2 = State('q2','q2')

        nfa.add_epsilon_transition(nfa.start_state,q0)
        nfa.add_epsilon_transition(q0,q1)
        nfa.add_epsilon_transition(q1,q2)
        nfa.add_epsilon_transition(q2,q0)
        
        closure = nfa.closure(nfa.start_state)

        assert len(closure) == 4
        assert nfa.start_state in closure
        assert q0 in closure
        assert q1 in closure
        assert q2 in closure
        assert q1 in nfa.finals

        closure = nfa.closure(q0)

        assert len(closure) == 3
        assert q0 in closure
        assert q1 in closure
        assert q2 in closure

        closure = nfa.closure(q1)

        assert len(closure) == 3
        assert q0 in closure
        assert q1 in closure
        assert q2 in closure

        closure = nfa.closure(q2)

        assert len(closure) == 3
        assert q0 in closure
        assert q1 in closure
        assert q2 in closure
    
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
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01'
        '101'
        '010',
        '101010',
        '10101'
        '000001'
        '111110',
    ])
    def test_nfa_to_dfa_minimize_1(self,string:str,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()
        minimized = dfa.minimize()
        was_completed = False

        if not dfa.is_complete:
            was_completed = True
            dfa.make_complete()
        
        assert len(minimized.states) <= len(dfa.states)
        
        if was_completed:
            dfa.restore_to_before_complete()
        
        assert minimized.accept(list(string)) == dfa.accept(list(string))

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
    def test_nfa_to_dfa_minimize_2(self,string:str,nfa_zeros_or_ones:NFA):
        dfa = nfa_zeros_or_ones.to_deterministic()
        minimized = dfa.minimize()
        was_completed = False

        if not dfa.is_complete:
            was_completed = True
            dfa.make_complete()
        
        assert len(minimized.states) <= len(dfa.states)
        
        if was_completed:
            dfa.restore_to_before_complete()
        
        assert minimized.accept(list(string)) == dfa.accept(list(string))
    
    @pytest.mark.parametrize("is_accept,symbol",[
        (True,'1'),
        (True,'0'),
        (False,'0'),
        (False,'1')
    ])
    def test_nfa_add_transition_operator(self,is_accept:bool,symbol:str,nfa:NFA):
        q0 = State('q0','q0',is_accept)

        nfa += nfa.start_state,symbol,q0

        assert q0 in nfa.states
        if is_accept:
            assert q0 in nfa.finals
        assert nfa.has_transition(nfa.start_state,symbol)
        assert nfa.next(nfa.start_state,symbol) == q0
        assert (nfa.start_state.id,symbol) in nfa.transition_function
        assert nfa.transition_function[(nfa.start_state.id,symbol)] == q0.id