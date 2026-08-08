import pytest
from typing import List, Set, Tuple
from random import random

from pylgen.automaton import DFA,State,Automaton

class TestAutomaton:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'0','1'}
    
    @pytest.fixture
    def automaton(self,alphabet:Set[str]) -> Automaton:
        return DFA('start','start',alphabet)
    
    @pytest.mark.parametrize("is_accept",[
        True,
        False
    ])
    def test_automaton_creation(self,is_accept:bool,alphabet:Set[str]):

        dfa = DFA('start','start',alphabet,is_accept)

        assert len(dfa.alphabet) == len(alphabet)
        assert len(dfa.alphabet.difference(alphabet)) == 0
        assert dfa.start_state.id == 'start'
        assert dfa.start_state.value == 'start'
        assert dfa.start_state.is_accept == is_accept
        assert dfa.start_state == dfa.current_state
        assert len(dfa.states) == 1 and dfa.start_state in dfa.states
        if is_accept:
            assert len(dfa.finals) == 1 and dfa.start_state in dfa.finals
        assert not dfa.is_complete
        assert len(dfa.transition_function) == 0

    @pytest.mark.parametrize("is_accept,symbol",[
        (True,'0'),
        (True,'1'),
        (False,'0'),
        (False,'1')
    ])
    def test_automaton_add_transition(self,is_accept:bool,symbol:str,automaton:Automaton):
        s0 = State('s0','s0',is_accept)

        automaton.add_transition(automaton.start_state,s0,symbol)

        assert s0 in automaton.states
        if is_accept:
            assert s0 in automaton.finals
        assert automaton.has_transition(automaton.start_state,symbol)
        assert automaton.next(automaton.start_state,symbol) == s0
        assert (automaton.start_state.id,symbol) in automaton.transition_function
        assert automaton.transition_function[(automaton.start_state.id,symbol)] == s0.id
    
    @pytest.mark.parametrize("is_accept,symbol",[
        (True,'0'),
        (True,'1'),
        (False,'0'),
        (False,'1')
    ])
    def test_automaton_overwrite_transition(self,is_accept:bool,symbol:str,automaton:Automaton):
        s0 = State('s0','s0')
        s1 = State('s1','s1',is_accept)

        automaton.add_transition(automaton.start_state,s0,symbol)
        automaton.add_transition(automaton.start_state,s1,symbol)

        assert s0 in automaton.states
        assert s1 in automaton.states
        if is_accept:
            assert s1 in automaton.finals
        assert automaton.has_transition(automaton.start_state,symbol)
        assert automaton.next(automaton.start_state,symbol) == s1
        assert (automaton.start_state.id,symbol) in automaton.transition_function
        assert automaton.transition_function[(automaton.start_state.id,symbol)] == s1.id
    
    @pytest.mark.parametrize("symbol",[
        '0',
        '1'
    ])
    def test_automaton_key_error(self,symbol:str,automaton:Automaton):
        with pytest.raises(KeyError):
            n = automaton.next(automaton.start_state,symbol)
        
    def test_automaton_make_complete(self,automaton:Automaton):
        automaton.make_complete()
        assert automaton.is_complete
        assert len(automaton.transition_function) == len(automaton.states) * len(automaton.alphabet)

        automaton.restore_to_before_complete()
        assert not automaton.is_complete
        assert len(automaton.transition_function) != len(automaton.states) * len(automaton.alphabet)

    @pytest.mark.parametrize("symbols",[
        set('asdj'),
        set('23843209'),
        set('sdfsfsef2083jsda9iasd129gwmzxcvhb ')
    ])
    def test_automaton_extend_alphabet(self,symbols:Set[str],automaton:Automaton):
        automaton.extend_alphabet(symbols)

        assert symbols.issubset(automaton.alphabet)