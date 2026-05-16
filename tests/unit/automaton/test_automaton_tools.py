import pytest

from automaton import get_word_automaton

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