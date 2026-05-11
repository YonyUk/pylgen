import pytest
from typing import Set

from automaton import Automaton,NFA,DFA,State

class TestAutomatonOperations:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'0','1'}
    
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
    
    @pytest.fixture
    def zero_terminated_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q1,'0')
        aut.add_transition(aut.start_state,q0,'1')
        aut.add_transition(q0,q1,'0')
        aut.add_transition(q0,q0,'1')
        aut.add_transition(q1,q0,'1')
        aut.add_transition(q1,q1,'0')

        return aut
    
    @pytest.fixture
    def one_terminated_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q1,'1')
        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(q0,q1,'1')
        aut.add_transition(q0,q0,'0')
        aut.add_transition(q1,q0,'0')
        aut.add_transition(q1,q1,'1')

        return aut
    
    @pytest.fixture
    def five_multiplo_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('q0','q0',alphabet,True)

        q1 = State('q1','q1')
        q2 = State('q2','q2')
        q3 = State('q3','q3')
        q4 = State('q4','q4')

        aut.add_transition(aut.start_state,aut.start_state,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_transition(q1,q2,'0')
        aut.add_transition(q1,q3,'1')

        aut.add_transition(q2,q4,'0')
        aut.add_transition(q2,aut.start_state,'1')

        aut.add_transition(q3,q1,'0')
        aut.add_transition(q3,q2,'1')

        aut.add_transition(q4,q3,'0')
        aut.add_transition(q4,q4,'1')

        return aut
    
    @pytest.fixture
    def alternate_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0',True)
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_transition(q0,q1,'1')
        aut.add_transition(q1,q0,'0')

        return aut
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '01010',
        '10101',
        '11111',
        '00000',
        '0101020',
        '1010201'
    ])
    def test_automaton_union_operation_1(self,string:str,zero_terminated_dfa:DFA,one_terminated_dfa:DFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,one_terminated_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or one_terminated_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1'
        '0',
        '00',
        '10',
        '01',
        '11',
        '0000',
        '1111',
        '101',
        '010',
        '1010',
        '010101',
        '11110',
        '110010'
    ])
    def test_automaton_union_operation_2(self,string:str,zero_terminated_dfa:DFA,five_multiplo_dfa:DFA):
        
        union_automaton = Automaton.Union({zero_terminated_dfa,five_multiplo_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or five_multiplo_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))