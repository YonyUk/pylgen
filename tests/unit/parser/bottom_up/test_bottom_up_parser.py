import pytest
from typing import Any, List

from parser.parser import BottomUpParser
from grammar.grammar import Production
from common.types import AST, Symbol

class TestBottomUpParser:
    
    def test_parser_reduction_adding(self):
        
        def reductor(asts:List[AST]) -> AST:
            return asts[0]

        E = Symbol('E')
        plus = Symbol('+',True)
        T = Symbol('T')

        production = Production(E,[E,plus,T])
        parser = BottomUpParser({},{})

        parser[production] = reductor
    
    def test_parser_reduction_adding_fail(self):

        def invalid_reductor_1(asts:List[Any]) -> Any:
            return asts[0]
        
        def invalid_reductor_2(asts:List[AST]) -> Any:
            return asts[0]

        def invalid_reductor_3(asts:List[Any]) -> AST:
            return asts[0]
        
        E = Symbol('E')
        plus = Symbol('+',True)
        T = Symbol('T')

        production = Production(E,[E,plus,T])
        parser = BottomUpParser({},{})

        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_1
        
        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_2
        
        with pytest.raises(ValueError,match='invalid reductor function signature'):
            parser[production] = invalid_reductor_3