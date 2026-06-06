from typing import List

import pytest

from grammar.grammar import AttributedProductionsSet
from common.types import Symbol,AST

def comodin_reductor(asts:List[AST]) -> AST:
    return AST(Symbol('s'),0,0)

class TestProductionsSet:

    def test_create_productions_set(self):

        p = AttributedProductionsSet()

        assert p.productions == []
    
    def test_add_production(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True)

        p = AttributedProductionsSet()

        p += (A,c,B),comodin_reductor

        assert [A,c,B] in p.productions
    
    def test_add_many_productions(self):

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True)
        e = Symbol('e',True,True)

        p = AttributedProductionsSet()

        p += (A,c),comodin_reductor
        p += (B,e),comodin_reductor

        assert [A,c] in p.productions
        assert [B,e] in p.productions
