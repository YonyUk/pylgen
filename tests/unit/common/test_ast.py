import pytest
from pylgen.common.types import AST,Symbol,ErrorAST
from pylgen.analysis.error import SemanticError
from pylgen.analysis.error_type import ErrorType

class TestAST:

    @pytest.mark.parametrize("symbol,line,column",[
        (Symbol('A'),0,0),
        (Symbol('A'),1,2),
        (Symbol('A'),10,2),
        (Symbol('A',True),0,0),
        (Symbol('A',True),1,2),
        (Symbol('A',True),10,2),
        (Symbol('A',True,True),0,0),
        (Symbol('A',True,True),1,2),
        (Symbol('A',True,True),10,2),
        (Symbol('B'),0,0),
        (Symbol('B'),1,2),
        (Symbol('B'),10,2),
        (Symbol('B',True),0,0),
        (Symbol('B',True),1,2),
        (Symbol('B',True),10,2),
        (Symbol('B',True,True),0,0),
        (Symbol('B',True,True),1,2),
        (Symbol('B',True,True),10,2)
    ])
    def test_correct_ast_creation(self,symbol:Symbol,line:int,column:int):

        ast = AST(symbol,line,column)

        assert ast.symbol == symbol
        assert ast.line == line
        assert ast.column == column
        assert not ast.is_error
        with pytest.raises(NotImplementedError):
            ast.children()

        error = SemanticError('error 1',line,column)
        error_ast = ErrorAST(symbol,line,column,error)

        assert error_ast.symbol == symbol
        assert error_ast.line == line
        assert error_ast.column == column
        assert error_ast.is_error
        assert error_ast.children() == []