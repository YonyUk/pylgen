import pytest

from common.types import Symbol

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