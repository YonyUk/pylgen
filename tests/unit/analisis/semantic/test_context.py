import pytest

from pylgen.analisis.context import Context
from pylgen.analisis.error import RuntimeError
from pylgen.common.types import AST,Symbol

class TestContext:

    def test_context_creation(self):

        context = Context()
        with pytest.raises(NotImplementedError):
            context.errors
        
        assert not context.stack_trace

        with pytest.raises(NotImplementedError):
            context.push_new_scope()
        
        with pytest.raises(NotImplementedError):
            context.pop_scope()
        
        with pytest.raises(NotImplementedError):
            context.clear_runtime_errors()
        
        with pytest.raises(NotImplementedError):
            context.get_runtime_errors()

        with pytest.raises(NotImplementedError):
            context.clear_errors()
        
        with pytest.raises(NotImplementedError):
            context.reset()

        with pytest.raises(NotImplementedError):
            ast = AST(Symbol('s'),0,0)
            context.add_runtime_error(ast,RuntimeError([],0,0,''))
    
    def test_context_trace_pushing(self):

        context = Context()

        context.push_trace('trace 1')
        assert context.stack_trace == ['trace 1']
        context.pop_trace()
        assert not context.stack_trace