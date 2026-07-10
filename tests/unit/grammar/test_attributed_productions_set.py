from typing import Any, List

import pytest

from pylgen.grammar.grammar import AttributedProductionsSet
from pylgen.common.types import Symbol,AST,ASTListView

def comodin_reductor(asts:ASTListView) -> AST:
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
    
    def test_add_production_fail(self):

        def invalid_reductor_1(asts:Any) -> Any:
            return AST(Symbol('s'),0,0)
        
        def invalid_reductor_2(asts:List[Any]) -> Any:
            return AST(Symbol('s'),0,0)

        def invalid_reductor_3(asts:ASTListView) -> Any:
            return AST(Symbol('s'),0,0)

        def invalid_reductor_4(asts:Any) -> AST:
            return AST(Symbol('s'),0,0)

        def invalid_reductor_5(asts:List[Any]) -> AST:
            return AST(Symbol('s'),0,0)

        A = Symbol('A')
        B = Symbol('B')
        c = Symbol('c',True)

        p = AttributedProductionsSet()

        with pytest.raises(ValueError,match='Invalid signature for second item of tuple, reduction must have annotation \\(List\\[AST\\]\\) -> AST'):
            p += (A,c,B),invalid_reductor_1
        
        with pytest.raises(ValueError,match='Invalid signature for second item of tuple, reduction must have annotation \\(List\\[AST\\]\\) -> AST'):
            p += (A,c,B),invalid_reductor_2
        
        with pytest.raises(ValueError,match='Invalid signature for second item of tuple, reduction must have annotation \\(List\\[AST\\]\\) -> AST'):
            p += (A,c,B),invalid_reductor_3
        
        with pytest.raises(ValueError,match='Invalid signature for second item of tuple, reduction must have annotation \\(List\\[AST\\]\\) -> AST'):
            p += (A,c,B),invalid_reductor_4
        
        with pytest.raises(ValueError,match='Invalid signature for second item of tuple, reduction must have annotation \\(List\\[AST\\]\\) -> AST'):
            p += (A,c,B),invalid_reductor_5