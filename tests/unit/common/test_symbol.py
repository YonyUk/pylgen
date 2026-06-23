import pytest

from pylgen.common.types import Symbol

class TestSymbol:

    @pytest.mark.parametrize("is_terminal,is_epsilon",[
        (False,False),
        (False,True),
        (True,False),
        (True,True)
    ])
    def test_correct_symbol_creation(self,is_terminal:bool,is_epsilon:bool):

        if is_epsilon and not is_terminal:
            with pytest.raises(ValueError):
                symbol = Symbol('Symbol',is_terminal,is_epsilon)
        else:
            symbol = Symbol('Symbol',is_terminal,is_epsilon)

            assert symbol.symbol == 'Symbol'
            assert symbol.is_terminal == is_terminal
            assert symbol.is_epsilon == is_epsilon
    
    @pytest.mark.parametrize("symbol_1,symbol_2,are_equals",[
        (Symbol('A'),Symbol('A'),True),
        (Symbol('A'),Symbol('B'),False),
        (Symbol('A'),Symbol('A',True),False),
        (Symbol('A',True),Symbol('A',True),True),
        (Symbol('A',True),Symbol('A'),False),
        (Symbol('A',True),Symbol('B',True),False),
        (Symbol('A',True),Symbol('A',True,True),False),
        (Symbol('A',True,True),Symbol('A',True),False),
        (Symbol('A',True,True),Symbol('B',True,True),False),
        (Symbol('A',True,True),Symbol('A',True,True),True)
    ])
    def test_symbol_equality(self,symbol_1:Symbol,symbol_2:Symbol,are_equals:bool):

        assert (symbol_1 == symbol_2) == are_equals