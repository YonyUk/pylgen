from typing import Set

import pytest

from pylgen.automaton import State,DFA

class TestDFA:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'0','1'}
    
    @pytest.fixture
    def dfa(self,alphabet:Set[str]) -> DFA:
        return DFA('start','start',alphabet)
    
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

    @pytest.mark.parametrize("is_accept,symbol",[
        (True,'0'),
        (True,'1'),
        (False,'0'),
        (False,'1')
    ])
    def test_dfa_add_transition_with_operator(self,is_accept:bool,symbol:str,dfa:DFA):
        s0 = State('s0','s0',is_accept)

        dfa += dfa.start_state,symbol,s0

        assert s0 in dfa.states
        if is_accept:
            assert s0 in dfa.finals
        assert dfa.has_transition(dfa.start_state,symbol)
        assert dfa.next(dfa.start_state,symbol) == s0
        assert (dfa.start_state.id,symbol) in dfa.transition_function
        assert dfa.transition_function[(dfa.start_state.id,symbol)] == s0.id
    
    @pytest.mark.parametrize("is_accept,symbol",[
        (True,'0'),
        (True,'1'),
        (False,'0'),
        (False,'1')
    ])
    def test_dfa_overwrite_transition_with_operator(self,is_accept:bool,symbol:str,dfa:DFA):
        s0 = State('s0','s0')
        s1 = State('s1','s1',is_accept)

        dfa.add_transition(dfa.start_state,s0,symbol)
        dfa.add_transition(dfa.start_state,s1,symbol)

        assert s0 in dfa.states
        assert s1 in dfa.states
        if is_accept:
            assert s1 in dfa.finals
        assert dfa.has_transition(dfa.start_state,symbol)
        assert dfa.next(dfa.start_state,symbol) == s1
        assert (dfa.start_state.id,symbol) in dfa.transition_function
        assert dfa.transition_function[(dfa.start_state.id,symbol)] == s1.id
    
    @pytest.mark.parametrize("string,should_accept",[
        ('00101010010',True),
        ('0',True),
        ('00',True),
        ('00000',True),
        ('1110',True),
        ('11101',False),
        ('',False),
        ('0010101',False),
        ('00001',False),
    ])
    def test_zero_terminated_dfa(self,string:str,should_accept:bool,zero_terminated_dfa:DFA):
        assert zero_terminated_dfa.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('0010101001',True),
        ('1',True),
        ('11',True),
        ('111111',True),
        ('0001',True),
        ('1110',False),
        ('',False),
        ('001010',False),
        ('0000',False),
    ])
    def test_one_terminated_dfa(self,string:str,should_accept:bool,one_terminated_dfa:DFA):
        assert one_terminated_dfa.accept(list(string)) == should_accept

    @pytest.mark.parametrize("value",[
        10,
        15,
        7,
        73,
        35,
        24,
        21,
        11,
        20,
        30,
        70
    ])
    def test_five_multiplo_dfa(self,value:int,five_multiplo_dfa:DFA):
        assert five_multiplo_dfa.accept(list(bin(value)[2:])) == (value % 5 == 0)
    
    @pytest.mark.parametrize("string,should_accept",[
        ('0101010',True),
        ('01010101',True),
        ('0',True),
        ('1',True),
        ('10',True),
        ('01',True),
        ('010',True),
        ('101',True),
        ('1011',False),
        ('1001',False),
        ('0001',False),
        ('1110',False),
        ('0101010101010101001',False),
        ('',False)
    ])
    def test_alternate_dfa(self,string:str,should_accept:bool,alternate_dfa:DFA):
        assert alternate_dfa.accept(list(string)) == should_accept