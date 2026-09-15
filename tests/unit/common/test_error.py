from pylgen.common.types import Error,LexicalError,SyntaxError,SemanticError,RuntimeError
from pylgen.common.enums import ErrorType

import pytest

class TestError:
    
    @pytest.mark.parametrize("error_type,line,column,msg",[
        (ErrorType.LEXICAL,1,1,'nada'),
        (ErrorType.SYNTAX,1,20,'nuevo'),
        (ErrorType.SEMANTIC,2,13,'aqui'),
    ])
    def test_error_creation(self,error_type:ErrorType,line:int,column:int,msg:str):
        error = Error(error_type,line,column,column,column + 1,msg)

        assert error.type == error_type
        assert error.line == line
        assert error.column == column
        assert error.source_line_interval == (column,column + 1)
        assert msg in error.message
    
    def test_error_creation_failed(self):
        with pytest.raises(TypeError,match='type_ must be a member of ErrorType'):
            error = Error(10,0,0,0,1,'') # type:ignore
        with pytest.raises(ValueError,match='type_ must be a member of ErrorType'):
            error = Error('nada',0,0,0,1,'') # type:ignore
    
    def test_lexic_error(self):
        error = LexicalError('nada',1,1,0,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.LEXICAL
        assert error.source_line_interval == (0,1)
        assert 'nada' in error.message

    def test_sintax_error(self):
        error = SyntaxError('nada',1,1,0,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.SYNTAX
        assert error.source_line_interval == (0,1)
        assert 'nada' in error.message

    def test_semantic_error(self):
        error = SemanticError('nada',1,1,0,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.SEMANTIC
        assert error.source_line_interval == (0,1)
        assert 'nada' in error.message

    def test_errors_comparision(self):
        err1 = LexicalError('nada',1,1,0,1)
        err2 = LexicalError('nada',1,1,0,1)

        assert err1 == err2
        assert hash(err1) == hash(err2)

        err2 = LexicalError('nada1',1,1,0,1)

        assert err1 != err2
        assert hash(err1) != hash(err2)

        err2 = LexicalError('nada',1,1,0,2)

        assert err1 != err2
        assert hash(err1) != hash(err2)

        err2 = SyntaxError('nada',1,1,0,1)

        assert err1 != err2
        assert hash(err1) != hash(err2)

        err2 = SemanticError('nada',1,1,0,1)

        assert err1 != err2
        assert hash(err1) != hash(err2)

        err2 = RuntimeError([],1,1,0,1,'nada')

        assert err1 != err2
        assert hash(err1) != hash(err2)