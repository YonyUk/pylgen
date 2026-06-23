from pylgen.analisis.error import Error,LexicError,SintaxError,SemanticError
from pylgen.analisis.error_type import ErrorType

import pytest

class TestError:
    
    @pytest.mark.parametrize("error_type,line,column,msg",[
        (ErrorType.LEXIC,1,1,'nada'),
        (ErrorType.SINTAX,1,20,'nuevo'),
        (ErrorType.SEMANTIC,2,13,'aqui'),
    ])
    def test_error_creation(self,error_type:ErrorType,line:int,column:int,msg:str):
        error = Error(error_type,line,column,msg)

        assert error.type == error_type
        assert error.line == line
        assert error.column == column
        assert msg in error.message
    
    def test_error_creation_failed(self):
        with pytest.raises(TypeError,match='type_ must be a member of ErrorType'):
            error = Error(10,0,0,'') # type:ignore
        with pytest.raises(ValueError,match='type_ must be a member of ErrorType'):
            error = Error('nada',0,0,'') # type:ignore
    
    def test_lexic_error(self):
        error = LexicError('nada',1,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.LEXIC
        assert 'nada' in error.message

    def test_sintax_error(self):
        error = SintaxError('nada',1,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.SINTAX
        assert 'nada' in error.message

    def test_semantic_error(self):
        error = SemanticError('nada',1,1)
        assert error.line == 1
        assert error.column == 1
        assert error.type == ErrorType.SEMANTIC
        assert 'nada' in error.message