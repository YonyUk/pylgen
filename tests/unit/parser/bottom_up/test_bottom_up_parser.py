import pytest
from typing import Any, List

from pylgen.parser.parser import BottomUpParser
from pylgen.grammar.grammar import Production
from pylgen.common.types import AST, Symbol, ASTListView

class TestBottomUpParser:
    
    def test_parser_reduction_adding(self):
        
        def reductor(asts:ASTListView) -> AST:
            return asts[0]

        E = Symbol('E')
        plus = Symbol('+',True)
        T = Symbol('T')

        production = Production(E,[E,plus,T])
        parser = BottomUpParser('I0',{},{})

        parser[production] = reductor
    
    def test_parser_reduction_adding_fail(self):

        def invalid_reductor_1(asts:ASTListView) -> Any:
            return asts[0]
        
        def invalid_reductor_2(asts:ASTListView) -> Any:
            return asts[0]

        def invalid_reductor_3(asts:List[Any]) -> AST:
            return asts[0]
        
        E = Symbol('E')
        plus = Symbol('+',True)
        T = Symbol('T')

        production = Production(E,[E,plus,T])
        parser = BottomUpParser('I0',{},{})

        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_1
        
        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_2
        
        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_3