import pytest

from common.types import Symbol
from grammar.attributed_grammar import AttributedProduction

class TestAttributedProduction:

    def test_correct_creation(self):

        a = Symbol('A')
        b = Symbol('B')
        d = Symbol('C')

        def reductor(value):
            return value
        
        prod = AttributedProduction(a,[b,d],reductor)

        assert prod.head == a
        assert prod.production == [b,d]
        assert prod.reductor == reductor
    
    def test_attributed_production_error_raising(self):

        a = Symbol('A',True)
        b = Symbol('B')
        d = Symbol('C')

        with pytest.raises(ValueError):
            prod = AttributedProduction(a,[b,d],None) # type: ignore
        
    def test_attributed_production_none_reductor(self):

        a = Symbol('A')
        b = Symbol('B')
        d = Symbol('C')

        prod = AttributedProduction(a,[b,d],None) # type: ignore

        assert prod.reductor == None