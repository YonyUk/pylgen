from typing import Set
import pytest

from automaton import DFA,NFA,State
from regex import RegexEngine

class TestAutomatonToRegex:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'0','1'}
    
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
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '000',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '111',
        '00101010',
        '010100101'
    ])
    def test_automaton_to_grammar_1(self,string:str,zero_terminated_dfa:DFA):

        G = RegexEngine.GetGrammar(zero_terminated_dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert zero_terminated_dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '000',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '111',
        '00101010',
        '010100101'
    ])
    def test_automaton_to_grammar_2(self,string:str,one_terminated_dfa:DFA):

        G = RegexEngine.GetGrammar(one_terminated_dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert one_terminated_dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '00',
        '10',
        '11',
        '000',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '111',
        '1111',
        '10100',
        '1010',
        '11001',
        '01001',
        '1001010'
    ])
    def test_automaton_to_grammar_3(self,string:str,five_multiplo_dfa:DFA):
        
        G = RegexEngine.GetGrammar(five_multiplo_dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert five_multiplo_dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize('string',[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '00101001',
        '10101110100',
        '010101010101010',
        '1010101010101010101'
    ])
    def test_automaton_to_grammar_4(self,string:str,alternate_dfa:DFA):

        G = RegexEngine.GetGrammar(alternate_dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert alternate_dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '00',
        '10',
        '11',
        '010110011',
        '01001010001',
        '111111110',
        '100000000',
        '0111111111',
        '000000001'
    ])
    def test_automaton_to_grammar_5_1(self,string:str,nfa_0_1_terminated:NFA):
        dfa = nfa_0_1_terminated.to_deterministic()
        G = RegexEngine.GetGrammar(nfa_0_1_terminated)

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '00',
        '10',
        '11',
        '010110011',
        '01001010001',
        '111111110',
        '100000000',
        '0111111111',
        '000000001'
    ])
    def test_automaton_to_grammar_5_2(self,string:str,nfa_0_1_terminated:NFA):
        dfa = nfa_0_1_terminated.to_deterministic()
        G = RegexEngine.GetGrammar(dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '01',
        '00',
        '10',
        '11',
        '010110011',
        '01001010001',
        '111111110',
        '100000000',
        '0111111111',
        '000000001'
    ])
    def test_automaton_to_grammar_5_3(self,string:str,nfa_0_1_terminated:NFA):
        dfa = nfa_0_1_terminated.to_deterministic()
        G = RegexEngine.GetGrammar(dfa.minimize())

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '000000',
        '11111111',
        '10000',
        '000001',
        '11111110',
        '0111111'
    ])
    def test_automaton_to_grammar_6_1(self,string:str,nfa_zeros_or_ones:NFA):
        dfa = nfa_zeros_or_ones.to_deterministic()
        G = RegexEngine.GetGrammar(nfa_zeros_or_ones)

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '000000',
        '11111111',
        '10000',
        '000001',
        '11111110',
        '0111111'
    ])
    def test_automaton_to_grammar_6_2(self,string:str,nfa_zeros_or_ones:NFA):
        dfa = nfa_zeros_or_ones.to_deterministic()
        G = RegexEngine.GetGrammar(dfa)

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '000000',
        '11111111',
        '10000',
        '000001',
        '11111110',
        '0111111'
    ])
    def test_automaton_to_grammar_6_3(self,string:str,nfa_zeros_or_ones:NFA):
        dfa = nfa_zeros_or_ones.to_deterministic()
        G = RegexEngine.GetGrammar(dfa.minimize())

        aut = RegexEngine.GetAutomaton(G)

        assert dfa.accept(list(string)) == aut.accept(list(string))