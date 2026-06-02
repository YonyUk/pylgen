from typing import Any, List
from string import ascii_letters
import random

import pytest

from automaton import get_word_automaton,get_words_automaton,get_word_automaton_with_value,get_words_automaton_with_value

class TestAutomatonTools:

    @pytest.mark.parametrize("string",[
        'hello',
        'world',
        'from',
        'python',
        'tests'
    ])
    def test_get_word_automaton(self,string:str):
        aut = get_word_automaton(string)

        assert aut.accept(list(string))
        assert not aut.accept(list('prove'+string))
        assert not aut.accept(list('not'+string))
        assert not aut.accept(list('prove'+string+'nothing'))
    
    @pytest.mark.parametrize("string,value,only_finals",[
        ('hello',2,True),
        ('world',True,False),
        ('from',False,True),
        ('python','nada',False),
        ('tests',[0],True)
    ])
    def test_get_word_automaton_with_value(self,string:str,value:Any,only_finals:bool):
        aut = get_word_automaton_with_value(string,value,only_finals)

        if only_finals:
            for state in aut.states:
                if not state.is_accept:
                    assert state.value != value
                else:
                    assert state.value == value
        else:
            for state in aut.states:
                assert state.value == value
        
        assert aut.accept(list(string))
        assert not aut.accept(list('prove'+string))
        assert not aut.accept(list('not'+string))
        assert not aut.accept(list('prove'+string+'nothing'))
    
    @pytest.mark.parametrize("words",[
        ['hello','world'],
        ['buscando','a','nemo'],
        ['welcome','to','the','hell']
    ])
    def test_get_words_automaton(self,words:List[str]):
        aut = get_words_automaton(words).to_deterministic()
        minimized = aut.minimize()

        for word in words:
            assert aut.accept(list(word))
            assert minimized.accept(list(word))
        
        for _ in range(20):
            word = ''.join(random.choices(ascii_letters,k=5))
            if not word in words:
                assert not aut.accept(list(word))
    
    @pytest.mark.parametrize("words,value,only_finals",[
        (['hello','world'],2,True),
        (['buscando','a','nemo'],True,False),
        (['welcome','to','the','hell'],'nada',True)
    ])
    def test_get_words_automaton_with_value(self,words:List[str],value:Any,only_finals:bool):
        aut = get_words_automaton_with_value(words,value,only_finals)

        if only_finals:
            for state in aut.states:
                if not state.is_accept:
                    assert state.value != value
                else:
                    assert state.value == value
        else:
            for state in aut.states:
                assert state.value == value

        aut = aut.to_deterministic()        
        minimized = aut.minimize()

        for word in words:
            assert aut.accept(list(word))
            assert minimized.accept(list(word))
        
        for _ in range(20):
            word = ''.join(random.choices(ascii_letters,k=5))
            if not word in words:
                assert not aut.accept(list(word))