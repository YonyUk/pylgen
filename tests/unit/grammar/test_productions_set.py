import pytest

from grammar.grammar import ProductionsSet
from common.types import Symbol

class TestProductionsSet:

    def test_create_productions_set(self):

        p = ProductionsSet()

        assert p.productions == []
    
    def test_add_production(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True)

        p = ProductionsSet()

        p += A,c,B

        assert [A,c,B] in p.productions
    
    def test_add_many_productions(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True)
        e = Symbol('e',True,True)

        p = ProductionsSet()

        p += A,c
        p += B,e

        assert [A,c] in p.productions
        assert [B,e] in p.productions
