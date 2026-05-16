from typing import List
from string import ascii_letters
import random

import pytest

from automaton import get_word_automaton,get_words_automaton

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