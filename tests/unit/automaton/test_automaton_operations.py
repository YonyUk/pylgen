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
    
    @pytest.fixture
    def alternate_a_b_dfa(self) -> DFA:
        aut = DFA('start','start',{'a','b'})

        q0 = State('q0','q0',True)
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q0,'a')
        aut.add_transition(aut.start_state,q1,'b')

        aut.add_transition(q0,q1,'b')
        aut.add_transition(q1,q0,'a')
    
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
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '000',
        '111',
        '101',
        '010',
        '000001',
        '111110',
        '010101',
        '101010'
    ])
    def test_automaton_union_operation_3(self,string:str,zero_terminated_dfa:DFA,alternate_dfa:DFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,alternate_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or alternate_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '00000001',
        '11111110',
        '10101010',
        '01010101',
        '1111111',
        '0000000'
    ])
    def test_automaton_union_operation_4_1(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '00000001',
        '11111110',
        '10101010',
        '01010101',
        '1111111',
        '0000000'
    ])
    def test_automaton_union_operation_4_2(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '00000001',
        '11111110',
        '10101010',
        '01010101',
        '1111111',
        '0000000'
    ])
    def test_automaton_union_operation_4_3(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({zero_terminated_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '00000001',
        '11111110',
        '10101010',
        '01010101',
        '1111111',
        '0000000'
    ])
    def test_automaton_union_operation_4_4(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()
        
        union_automaton = Automaton.Union({zero_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '000',
        '111',
        '101',
        '010',
        '110',
        '001',
        '010101',
        '101010',
        '00001',
        '11110',
        '111111',
        '000000'
    ])
    def test_automaton_union_operation_5_1(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '000',
        '111',
        '101',
        '010',
        '110',
        '001',
        '010101',
        '101010',
        '00001',
        '11110',
        '111111',
        '000000'
    ])
    def test_automaton_union_operation_5_2(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({zero_terminated_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '000',
        '111',
        '101',
        '010',
        '110',
        '001',
        '010101',
        '101010',
        '00001',
        '11110',
        '111111',
        '000000'
    ])
    def test_automaton_union_operation_5_3(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({zero_terminated_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '000',
        '111',
        '101',
        '010',
        '110',
        '001',
        '010101',
        '101010',
        '00001',
        '11110',
        '111111',
        '000000'
    ])
    def test_automaton_union_operation_5_4(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({zero_terminated_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '010',
        '101',
        '00001',
        '10000',
        '1010',
        '1111',
        '10100',
        '11001'
    ])
    def test_automaton_union_operation_6(self,string:str,one_terminated_dfa:DFA,five_multiplo_dfa:DFA):

        union_automaton = Automaton.Union({one_terminated_dfa,five_multiplo_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or five_multiplo_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '111',
        '000',
        '101',
        '010',
        '110',
        '001',
        '011',
        '100',
        '1010101001',
        '10101010101',
        '1010101010',
        '101010110',
        '10101011001'
    ])
    def test_automaton_union_operation_7(self,string:str,one_terminated_dfa:DFA,alternate_dfa:DFA):
        
        union_automaton = Automaton.Union({one_terminated_dfa,alternate_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or alternate_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '010101010',
        '01010101',
        '11111',
        '0000',
        '000001',
        '111110'
    ])
    def test_automaton_union_operation_8_1(self,string:str,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '010101010',
        '01010101',
        '11111',
        '0000',
        '000001',
        '111110'
    ])
    def test_automaton_union_operation_8_2(self,string:str,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '010101010',
        '01010101',
        '11111',
        '0000',
        '000001',
        '111110'
    ])
    def test_automaton_union_operation_8_3(self,string:str,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({one_terminated_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '010101010',
        '01010101',
        '11111',
        '0000',
        '000001',
        '111110'
    ])
    def test_automaton_union_operation_8_4(self,string:str,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '1111',
        '0000',
        '11110',
        '00001'
    ])
    def test_automaton_union_operation_9_1(self,string:str,one_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '1111',
        '0000',
        '11110',
        '00001'
    ])
    def test_automaton_union_operation_9_2(self,string:str,one_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '1111',
        '0000',
        '11110',
        '00001'
    ])
    def test_automaton_union_operation_9_3(self,string:str,one_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({one_terminated_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '1111',
        '0000',
        '11110',
        '00001'
    ])
    def test_automaton_union_operation_9_4(self,string:str,one_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({one_terminated_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '110',
        '011',
        '001',
        '100',
        '1010',
        '10101',
        '01010',
        '10100',
        '101010'
    ])
    def test_automaton_union_operation_10(self,string:str,five_multiplo_dfa:DFA,alternate_dfa:DFA):

        union_automaton = Automaton.Union({five_multiplo_dfa,alternate_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or alternate_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '110',
        '101',
        '011',
        '001',
        '010',
        '100',
        '1010',
        '10101',
        '11010',
        '11001',
        '1111',
        '0000',
        '1101',
        '0010',
        '00101'
        '10100',
        '10101',
        '11001',
        '11011',
        '11101'
    ])
    def test_automaton_union_operation_11_1(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):
        
        union_automaton = Automaton.Union({five_multiplo_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '110',
        '101',
        '011',
        '001',
        '010',
        '100',
        '1010',
        '10101',
        '11010',
        '11001',
        '1111',
        '0000',
        '1101',
        '0010',
        '00101'
        '10100',
        '10101',
        '11001',
        '11011',
        '11101'
    ])
    def test_automaton_union_operation_11_2(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):
        
        union_automaton = Automaton.Union({five_multiplo_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '110',
        '101',
        '011',
        '001',
        '010',
        '100',
        '1010',
        '10101',
        '11010',
        '11001',
        '1111',
        '0000',
        '1101',
        '0010',
        '00101'
        '10100',
        '10101',
        '11001',
        '11011',
        '11101'
    ])
    def test_automaton_union_operation_11_3(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):
        
        dfa = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({five_multiplo_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '110',
        '101',
        '011',
        '001',
        '010',
        '100',
        '1010',
        '10101',
        '11010',
        '11001',
        '1111',
        '0000',
        '1101',
        '0010',
        '00101'
        '10100',
        '10101',
        '11001',
        '11011',
        '11101'
    ])
    def test_automaton_union_operation_11_4(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()
        
        union_automaton = Automaton.Union({five_multiplo_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '111',
        '000',
        '110',
        '101',
        '011',
        '100',
        '010',
        '001',
        '1111',
        '0000',
        '0001',
        '1000',
        '1010',
        '1101',
        '1110',
        '0111'
    ])
    def test_automaton_union_operation_12_1(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({five_multiplo_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '111',
        '000',
        '110',
        '101',
        '011',
        '100',
        '010',
        '001',
        '1111',
        '0000',
        '0001',
        '1000',
        '1010',
        '1101',
        '1110',
        '0111'
    ])
    def test_automaton_union_operation_12_2(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({five_multiplo_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '111',
        '000',
        '110',
        '101',
        '011',
        '100',
        '010',
        '001',
        '1111',
        '0000',
        '0001',
        '1000',
        '1010',
        '1101',
        '1110',
        '0111'
    ])
    def test_automaton_union_operation_12_3(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({five_multiplo_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '111',
        '000',
        '110',
        '101',
        '011',
        '100',
        '010',
        '001',
        '1111',
        '0000',
        '0001',
        '1000',
        '1010',
        '1101',
        '1110',
        '0111'
    ])
    def test_automaton_union_operation_12_4(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({five_multiplo_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '010',
        '101',
        '110',
        '011',
        '001',
        '100',
        '0101010101',
        '010101010',
        '00001',
        '10101'
    ])
    def test_automaton_union_operation_13_1(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({alternate_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '010',
        '101',
        '110',
        '011',
        '001',
        '100',
        '0101010101',
        '010101010',
        '00001',
        '10101'
    ])
    def test_automaton_union_operation_13_2(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        union_automaton = Automaton.Union({alternate_dfa,nfa_0_1_terminated}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '010',
        '101',
        '110',
        '011',
        '001',
        '100',
        '0101010101',
        '010101010',
        '00001',
        '10101'
    ])
    def test_automaton_union_operation_13_3(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({alternate_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '10',
        '01',
        '010',
        '101',
        '110',
        '011',
        '001',
        '100',
        '0101010101',
        '010101010',
        '00001',
        '10101'
    ])
    def test_automaton_union_operation_13_4(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        union_automaton = Automaton.Union({alternate_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '000',
        '111',
        '1001',
        '0110',
        '0001',
        '1000',
        '0111',
        '1110',
        '0101010',
        '1010101',
        '1101',
        '0010'
    ])
    def test_automaton_union_operation_14_1(self,string:str,alternate_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({alternate_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '000',
        '111',
        '1001',
        '0110',
        '0001',
        '1000',
        '0111',
        '1110',
        '0101010',
        '1010101',
        '1101',
        '0010'
    ])
    def test_automaton_union_operation_14_2(self,string:str,alternate_dfa:DFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({alternate_dfa,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '000',
        '111',
        '1001',
        '0110',
        '0001',
        '1000',
        '0111',
        '1110',
        '0101010',
        '1010101',
        '1101',
        '0010'
    ])
    def test_automaton_union_operation_14_3(self,string:str,alternate_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({alternate_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '000',
        '111',
        '1001',
        '0110',
        '0001',
        '1000',
        '0111',
        '1110',
        '0101010',
        '1010101',
        '1101',
        '0010'
    ])
    def test_automaton_union_operation_14_4(self,string:str,alternate_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({alternate_dfa,dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_1(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({nfa_0_1_terminated,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_2(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({nfa_0_1_terminated,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_3(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({nfa_0_1_terminated,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_4(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        union_automaton = Automaton.Union({nfa_0_1_terminated,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_5(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({dfa1,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa2 = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_6(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()

        union_automaton = Automaton.Union({dfa1,nfa_zeros_or_ones}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa2 = nfa_zeros_or_ones.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_7(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({nfa_0_1_terminated,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_8(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({nfa_0_1_terminated,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()

        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_9(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({dfa1,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_10(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({dfa1,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_11(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({dfa1,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '00001',
        '10000',
        '01111',
        '11110',
        '0000',
        '1111',
        '01010101',
        '1010101'
    ])
    def test_automaton_union_operation_15_12(self,string:str,nfa_0_1_terminated:NFA,nfa_zeros_or_ones:NFA):

        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({dfa1,dfa2}).to_deterministic()
        minimized = union_automaton.minimize()


        assert union_automaton.accept(list(string)) == (dfa1.accept(list(string)) or dfa2.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_1(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            nfa_zeros_or_ones
        }).to_deterministic()

        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_2(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa1,
            nfa_zeros_or_ones
        }).to_deterministic()

        minimized = union_automaton.minimize()

        dfa2 = nfa_zeros_or_ones.to_deterministic()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_3(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa1,
            nfa_zeros_or_ones
        }).to_deterministic()

        minimized = union_automaton.minimize()

        dfa2 = nfa_zeros_or_ones.to_deterministic()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_4(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_5(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        dfa1 = nfa_0_1_terminated.to_deterministic()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_6(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_7(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_8(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '101',
        '010',
        '110',
        '001',
        '1111',
        '0000',
        '0001',
        '1010',
        '11001',
        '0010',
        '0100'
    ])
    def test_automaton_union_operation_16_9(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA,
        nfa_zeros_or_ones:NFA
    ):
        dfa1 = nfa_0_1_terminated.to_deterministic().minimize()
        dfa2 = nfa_zeros_or_ones.to_deterministic().minimize()

        union_automaton = Automaton.Union({
            zero_terminated_dfa,
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated,
            dfa2
        }).to_deterministic()

        minimized = union_automaton.minimize()

        input_ = list(string)

        should_accept = zero_terminated_dfa.accept(input_)
        should_accept |= one_terminated_dfa.accept(input_)
        should_accept |= five_multiplo_dfa.accept(input_)
        should_accept |= alternate_dfa.accept(input_)
        should_accept |= dfa1.accept(input_)
        should_accept |= dfa2.accept(input_)

        assert union_automaton.accept(input_) == should_accept
        assert minimized.accept(input_) == union_automaton.accept(input_)
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        'a',
        'b',
        '00',
        '11',
        '01',
        '10',
        'aa',
        'bb',
        'ab',
        'ba',
        '00001',
        '10000',
        '01111',
        '11110',
        'aaaab',
        'baaaa',
        'aaaab',
        'bbbba',
        '010101',
        '101010',
        'ababab',
        'bababa',
        '0101ab01',
        'abab01abab',
        '01010ababab0101',
        'ababab0101abab'
    ])
    def test_automaton_union_operation_17(self,string:str,alternate_dfa:DFA,alternate_a_b_dfa:DFA):

        union_automaton = Automaton.Union({alternate_dfa,alternate_a_b_dfa}).to_deterministic()
        minimized = union_automaton.minimize()

        assert union_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) or alternate_a_b_dfa.accept(list(string)))
        assert minimized.accept(list(string)) == union_automaton.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '00101010010',
        '0',
        '00',
        '00000',
        '1110',
        '11101',
        '',
        '0010101',
        '00001',
    ])
    def test_automaton_complement_operation_1_1(self,string:str,zero_terminated_dfa:DFA):

        complement_automaton = Automaton.Complement(zero_terminated_dfa)

        assert complement_automaton.accept(list(string)) == (not zero_terminated_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '00101010010',
        '0',
        '00',
        '00000',
        '1110',
        '11101',
        '',
        '0010101',
        '00001',
    ])
    def test_automaton_complement_operation_1_2(self,string:str,zero_terminated_dfa:DFA):

        complement_automaton = Automaton.Complement(zero_terminated_dfa).minimize()

        assert complement_automaton.accept(list(string)) == (not zero_terminated_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '0010101001',
        '1',
        '11',
        '111111',
        '0001',
        '1110',
        '',
        '001010',
        '0000',
    ])
    def test_automaton_complement_operation_2_1(self,string:str,one_terminated_dfa:DFA):

        complement_automaton = Automaton.Complement(one_terminated_dfa)

        assert complement_automaton.accept(list(string)) == (not one_terminated_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '0010101001',
        '1',
        '11',
        '111111',
        '0001',
        '1110',
        '',
        '001010',
        '0000',
    ])
    def test_automaton_complement_operation_2_2(self,string:str,one_terminated_dfa:DFA):

        complement_automaton = Automaton.Complement(one_terminated_dfa).minimize()

        assert complement_automaton.accept(list(string)) == (not one_terminated_dfa.accept(list(string)))
    
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
    def test_automaton_complement_operation_3_1(self,value:int,five_multiplo_dfa:DFA):
        
        string = list(bin(value)[2:])

        complement_automaton = Automaton.Complement(five_multiplo_dfa)

        assert complement_automaton.accept(string) == (not five_multiplo_dfa.accept(string))

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
    def test_automaton_complement_operation_3_2(self,value:int,five_multiplo_dfa:DFA):
        
        string = list(bin(value)[2:])

        complement_automaton = Automaton.Complement(five_multiplo_dfa).minimize()

        assert complement_automaton.accept(string) == (not five_multiplo_dfa.accept(string))
    
    @pytest.mark.parametrize("string",[
        '0101010',
        '01010101',
        '0',
        '1',
        '10',
        '01',
        '010',
        '101',
        '1011',
        '1001',
        '0001',
        '1110',
        '0101010101010101001',
        '',
    ])
    def test_automaton_complement_operation_4_1(self,string:str,alternate_dfa:DFA):

        complement_automaton = Automaton.Complement(alternate_dfa)

        assert complement_automaton.accept(list(string)) == (not alternate_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '0101010',
        '01010101',
        '0',
        '1',
        '10',
        '01',
        '010',
        '101',
        '1011',
        '1001',
        '0001',
        '1110',
        '0101010101010101001',
        '',
    ])
    def test_automaton_complement_operation_4_2(self,string:str,alternate_dfa:DFA):

        complement_automaton = Automaton.Complement(alternate_dfa).minimize()

        assert complement_automaton.accept(list(string)) == (not alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        'abababa',
        'abababab',
        'a',
        'b',
        'ba',
        'ab',
        'aba',
        'bab',
        'babb',
        'baab',
        'aaab',
        'bbba',
        'abababababababababab'
    ])
    def test_automaton_complement_operation_5_1(self,string:str,alternate_a_b_dfa:DFA):

        complement_automaton = Automaton.Complement(alternate_a_b_dfa)

        assert complement_automaton.accept(list(string)) == (not alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        'abababa',
        'abababab',
        'a',
        'b',
        'ba',
        'ab',
        'aba',
        'bab',
        'babb',
        'baab',
        'aaab',
        'bbba',
        'abababababababababab'
    ])
    def test_automaton_complement_operation_5_2(self,string:str,alternate_a_b_dfa:DFA):

        complement_automaton = Automaton.Complement(alternate_a_b_dfa).minimize()

        assert complement_automaton.accept(list(string)) == (not alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_1(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated)
        dfa = nfa_0_1_terminated.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_2(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated.to_deterministic())
        dfa = nfa_0_1_terminated.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_3(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated.to_deterministic().minimize())
        dfa = nfa_0_1_terminated.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_4(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated)
        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_5(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated.to_deterministic())
        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '10',
        '01',
        '101',
        '010',
        '101010',
        '10101',
        '000001',
        '111110',
    ])
    def test_automaton_complement_operation_6_6(self,string:str,nfa_0_1_terminated:NFA):

        complement_automaton = Automaton.Complement(nfa_0_1_terminated.to_deterministic().minimize())
        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))
    
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
    def test_automaton_complement_operation_7_1(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones)
        dfa = nfa_zeros_or_ones.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))
    
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
    def test_automaton_complement_operation_7_2(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones.to_deterministic())
        dfa = nfa_zeros_or_ones.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))
    
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
    def test_automaton_complement_operation_7_3(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones.to_deterministic().minimize())
        dfa = nfa_zeros_or_ones.to_deterministic()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

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
    def test_automaton_complement_operation_7_4(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones)
        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

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
    def test_automaton_complement_operation_7_5(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones.to_deterministic())
        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))

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
    def test_automaton_complement_operation_7_6(self,string:str,nfa_zeros_or_ones:NFA):

        complement_automaton = Automaton.Complement(nfa_zeros_or_ones.to_deterministic().minimize())
        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        assert complement_automaton.accept(list(string)) == (not dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01101010',
        '101010101',
        '000001',
        '111110',
        '0111',
        '1000'
    ])
    def test_automaton_intersection_operation_1_1(self,string:str,zero_terminated_dfa:DFA,one_terminated_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,one_terminated_dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and one_terminated_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01101010',
        '101010101',
        '000001',
        '111110',
        '0111',
        '1000'
    ])
    def test_automaton_intersection_operation_1_2(self,string:str,zero_terminated_dfa:DFA,one_terminated_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,one_terminated_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and one_terminated_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '110',
        '011',
        '001',
        '100',
        '1010',
        '1101',
        '10100',
        '10110',
        '11110',
        '100100',
        '101000',
        '101010'
    ])
    def test_automaton_intersection_operation_2_1(self,string:str,zero_terminated_dfa:DFA,five_multiplo_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,five_multiplo_dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and five_multiplo_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '110',
        '011',
        '001',
        '100',
        '1010',
        '1101',
        '10100',
        '10110',
        '11110',
        '100100',
        '101000',
        '101010'
    ])
    def test_automaton_intersection_operation_2_2(self,string:str,zero_terminated_dfa:DFA,five_multiplo_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,five_multiplo_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and five_multiplo_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '010101',
        '01010',
        '00001',
        '11110',
        '01111',
        '10000',
        '0101001',
        '01010110',
        '01010011',
        '010101001',''
        '0101010101010',
        '01010101010101'
    ])
    def test_automaton_intersection_operation_3_1(self,string:str,zero_terminated_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,alternate_dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '010101',
        '01010',
        '00001',
        '11110',
        '01111',
        '10000',
        '0101001',
        '01010110',
        '01010011',
        '010101001',''
        '0101010101010',
        '01010101010101'
    ])
    def test_automaton_intersection_operation_3_2(self,string:str,zero_terminated_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,alternate_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        'a',
        'b',
        '01010101',
        '1010101010',
        'ababababab',
        'bababababa',
        '010101ba01',
        'babababab01ba'
    ])
    def test_automaton_intersection_operation_4_1(self,string:str,zero_terminated_dfa:DFA,alternate_a_b_dfa:DFA):
        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,alternate_a_b_dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        'a',
        'b',
        '01010101',
        '1010101010',
        'ababababab',
        'bababababa',
        '010101ba01',
        'babababab01ba'
    ])
    def test_automaton_intersection_operation_4_2(self,string:str,zero_terminated_dfa:DFA,alternate_a_b_dfa:DFA):
        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,alternate_a_b_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_1(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,nfa_0_1_terminated})

        dfa = nfa_0_1_terminated.to_deterministic()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_2(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,nfa_0_1_terminated}).minimize()

        dfa = nfa_0_1_terminated.to_deterministic()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_3(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_4(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_5(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '00',
        '11',
        '01',
        '10',
        '010101',
        '10101010',
        '0000001',
        '100000',
        '011111',
        '1111110'
    ])
    def test_automaton_intersection_operation_5_6(self,string:str,zero_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_1(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,nfa_zeros_or_ones})

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_2(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,nfa_zeros_or_ones}).minimize()

        dfa = nfa_zeros_or_ones.to_deterministic()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_3(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_4(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_5(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '10',
        '00',
        '11',
        '00000',
        '11110',
        '000001',
        '100000',
        '111111',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_6_6(self,string:str,zero_terminated_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '00001',
        '10000',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_7_1(self,string:str,one_terminated_dfa:DFA,five_multiplo_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,five_multiplo_dfa})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and five_multiplo_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '10',
        '01',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '00001',
        '10000',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_7_2(self,string:str,one_terminated_dfa:DFA,five_multiplo_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,five_multiplo_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and five_multiplo_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '11',
        '00',
        '01',
        '01001',
        '101001',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_8_1(self,string:str,one_terminated_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,alternate_dfa})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '11',
        '00',
        '01',
        '01001',
        '101001',
        '0101010',
        '1010101'
    ])
    def test_automaton_intersection_operation_8_2(self,string:str,one_terminated_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,alternate_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '01',
        '00',
        '11',
        '10',
        '0101010',
        '101010101',
        'a',
        'b',
        'ab',
        'ba',
        'aa',
        'bb',
        'abababba',
        'ababababaa',
        '010101010ab0',
        '0101010a0b1ba0'
    ])
    def test_automaton_intersection_operation_9_1(self,string:str,one_terminated_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,alternate_a_b_dfa})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        '01',
        '00',
        '11',
        '10',
        '0101010',
        '101010101',
        'a',
        'b',
        'ab',
        'ba',
        'aa',
        'bb',
        'abababba',
        'ababababaa',
        '010101010ab0',
        '0101010a0b1ba0'
    ])
    def test_automaton_intersection_operation_9_2(self,string:str,one_terminated_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,alternate_a_b_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '00',
        '11',
        '10',
        '01',
        '001010',
        '0010101',
        '11001',
        '11101',
        '1010111',
        '10010010011'
    ])
    def test_automaton_intersection_operation_10_1(self,string,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,nfa_0_1_terminated})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '00',
        '11',
        '10',
        '01',
        '001010',
        '0010101',
        '11001',
        '11101',
        '1010111',
        '10010010011'
    ])
    def test_automaton_intersection_operation_10_2(self,string,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,nfa_0_1_terminated}).minimize()

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '00',
        '11',
        '10',
        '01',
        '001010',
        '0010101',
        '11001',
        '11101',
        '1010111',
        '10010010011'
    ])
    def test_automaton_intersection_operation_10_3(self,string,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '00',
        '11',
        '10',
        '01',
        '001010',
        '0010101',
        '11001',
        '11101',
        '1010111',
        '10010010011'
    ])
    def test_automaton_intersection_operation_10_4(self,string,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '00',
        '11',
        '10',
        '01',
        '001010',
        '0010101',
        '11001',
        '11101',
        '1010111',
        '10010010011'
    ])
    def test_automaton_intersection_operation_10_5(self,string,one_terminated_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({one_terminated_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (one_terminated_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '101',
        '010',
        '00001',
        '10000',
        '1010',
        '10101',
        '01010',
        '010101',
        '10100',
        '11110',
        '0111111'
    ])
    def test_automaton_intersection_operation_11_1(self,string:str,five_multiplo_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,alternate_dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '11',
        '01',
        '10',
        '101',
        '010',
        '00001',
        '10000',
        '1010',
        '10101',
        '01010',
        '010101',
        '10100',
        '11110',
        '0111111'
    ])
    def test_automaton_intersection_operation_11_2(self,string:str,five_multiplo_dfa:DFA,alternate_dfa:DFA):

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,alternate_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        'a',
        'b',
        '10',
        '01',
        '11',
        '00',
        'ab',
        'ba',
        'aa',
        'bb',
        '01010ab01',
        'abababab01ab',
        '00011abb01',
        'aabbbba0101001ab'
    ])
    def test_automaton_intersection_operation_12_1(self,string:str,five_multiplo_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,alternate_a_b_dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '1',
        '0',
        'a',
        'b',
        '10',
        '01',
        '11',
        '00',
        'ab',
        'ba',
        'aa',
        'bb',
        '01010ab01',
        'abababab01ab',
        '00011abb01',
        'aabbbba0101001ab'
    ])
    def test_automaton_intersection_operation_12_2(self,string:str,five_multiplo_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,alternate_a_b_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_1(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,nfa_0_1_terminated})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_2(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,nfa_0_1_terminated}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_3(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_4(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_5(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '10',
        '01',
        '11',
        '00',
        '101',
        '010',
        '110',
        '011',
        '100',
        '001',
        '1010',
        '11001',
        '100011'
    ])
    def test_automaton_intersection_operation_13_6(self,string:str,five_multiplo_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_1(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,nfa_zeros_or_ones})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_2(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,nfa_zeros_or_ones}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_3(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,nfa_zeros_or_ones})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_4(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_5(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_6(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '11',
        '00',
        '10',
        '01',
        '010',
        '101',
        '1111',
        '01001'
    ])
    def test_automaton_intersection_operation_14_7(self,string:str,five_multiplo_dfa:DFA,nfa_zeros_or_ones:NFA):

        dfa = nfa_zeros_or_ones.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({five_multiplo_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (five_multiplo_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        'a',
        'b',
        '00',
        '01',
        '0a',
        '0b',
        '10',
        '11',
        '1a',
        '1b',
        'a0',
        'a1',
        'a0',
        'ab',
        'b0',
        'b1',
        'ba',
        'bb',
        'a01ba0',
        '010101ababab0101'
    ])
    def test_automaton_intersection_operation_15_1(self,string:str,alternate_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({alternate_dfa,alternate_a_b_dfa})

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        'a',
        'b',
        '00',
        '01',
        '0a',
        '0b',
        '10',
        '11',
        '1a',
        '1b',
        'a0',
        'a1',
        'a0',
        'ab',
        'b0',
        'b1',
        'ba',
        'bb',
        'a01ba0',
        '010101ababab0101'
    ])
    def test_automaton_intersection_operation_15_2(self,string:str,alternate_dfa:DFA,alternate_a_b_dfa:DFA):

        intersection_automaton = Automaton.Intersection({alternate_dfa,alternate_a_b_dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and alternate_a_b_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_1(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({alternate_dfa,nfa_0_1_terminated})

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_2(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({alternate_dfa,nfa_0_1_terminated}).minimize()

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_3(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({alternate_dfa,nfa_0_1_terminated})

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_4(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({alternate_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_5(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({alternate_dfa,dfa})

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_6(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({alternate_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '010101',
        '10101010',
        '00010',
        '11101',
        '0011',
        '1100',
        '0111',
        '1000',
        '010101010001001',
        '0010101',
        '0101010101010101'
    ])
    def test_automaton_intersection_operation_16_7(self,string:str,alternate_dfa:DFA,nfa_0_1_terminated:NFA):

        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({alternate_dfa,dfa}).minimize()

        assert intersection_automaton.accept(list(string)) == (alternate_dfa.accept(list(string)) and dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '010',
        '100',
        '001',
        '1010',
        '10101010'
    ])
    def test_automaton_intersection_operation_multiple_17_1(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA
    ):
        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,five_multiplo_dfa,alternate_dfa})

        should_accept = zero_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '010',
        '100',
        '001',
        '1010',
        '10101010'
    ])
    def test_automaton_intersection_operation_multiple_17_2(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA
    ):
        intersection_automaton = Automaton.Intersection({zero_terminated_dfa,five_multiplo_dfa,alternate_dfa}).minimize()

        should_accept = zero_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_1(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated
        })

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_2(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            nfa_0_1_terminated
        }).minimize()

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_3(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa
        })

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_4(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa
        })

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_5(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa
        }).minimize()

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '101',
        '110',
        '011',
        '100',
        '010',
        '001',
        '1010101'
    ])
    def test_automaton_intersection_operation_multiple_18_6(
        self,
        string:str,
        one_terminated_dfa:DFA,
        five_multiplo_dfa:DFA,
        alternate_dfa:DFA,
        nfa_0_1_terminated:NFA
    ):
        dfa = nfa_0_1_terminated.to_deterministic().minimize()

        intersection_automaton = Automaton.Intersection({
            one_terminated_dfa,
            five_multiplo_dfa,
            alternate_dfa,
            dfa
        }).minimize()

        should_accept = one_terminated_dfa.accept(list(string))
        should_accept &= five_multiplo_dfa.accept(list(string))
        should_accept &= alternate_dfa.accept(list(string))
        should_accept &= dfa.accept(list(string))

        assert intersection_automaton.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('0',False),
        ('1',False),
        ('01',True),
        ('10',False),
        ('00',False),
        ('11',False),
        ('000',False),
        ('100',False),
        ('010',False),
        ('001',True),
        ('110',False),
        ('101',True),
        ('011',True),
        ('111',False),
        ('0000',False),
        ('1000',False),
        ('0100',False),
        ('0010',False),
        ('0001',True),
        ('1100',False),
        ('1010',False),
        ('1001',True),
        ('0110',False),
        ('0101',True),
        ('0011',True),
        ('1110',False),
        ('1101',True),
        ('1011',True),
        ('0111',True),
        ('1111',False)
    ])
    def test_automaton_concatenation_operation_19_1(self,string:str,should_accept:bool,zero_terminated_dfa:DFA,one_terminated_dfa:DFA):
        
        conc = Automaton.Concat(zero_terminated_dfa,one_terminated_dfa).to_deterministic()

        assert conc.accept(list(string)) == should_accept