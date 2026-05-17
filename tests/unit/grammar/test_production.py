import pytest

from grammar.grammar import Production
from common.types import Symbol

class TestProduction:

    def test_production_creation(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True,True)
        d = Symbol('d',True)

        prod = Production(A,[B,c,d])

        assert prod.id == f'{A} -> {B},{c},{d}'
        assert prod.head == A
        assert prod.production == [B,c,d]

        with pytest.raises(ValueError):
            prod = Production(c,[A,B,d])
    
    def test_production_comparision(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True,True)
        d = Symbol('d',True)

        prod_1 = Production(A,[c])
        prod_2 = Production(B,[d])
        prod_3 = Production(A,[d])
        prod_4 = Production(B,[c])
        prod_5 = Production(A,[c])

        assert prod_1 != prod_2
        assert prod_1 != prod_3
        assert prod_1 != prod_4
        assert prod_2 != prod_3
        assert prod_2 != prod_4
        assert prod_2 != prod_5
        assert prod_3 != prod_4
        assert prod_3 != prod_5
        assert prod_1 == prod_5