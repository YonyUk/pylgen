import pytest

from pylgen.analysis.visitor import TraversalStrategy
from pylgen.analysis.context import Context
from pylgen.common.types import Symbol,AST

class ValidContext(Context):
    pass

class InvalidContext:
    pass

class TestTraversalStrategy:

    def test_traversal_strategy_creation(self):

        context = Context()
        ast = AST(Symbol('s'),0,0)
        strategy = TraversalStrategy(Context)

        strategy._check_context_type(context)
        strategy.init(ast)

        with pytest.raises(NotImplementedError):
            strategy.has_next()
        
        with pytest.raises(NotImplementedError):
            strategy.current(context)
        
        with pytest.raises(NotImplementedError):
            strategy.reset()
    
    def test_traversal_strategy_creation_failed(self):

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            strategy = TraversalStrategy(str)
    
    def test_traversal_strategy_check_context_type_1(self):
        context = ValidContext()
        strategy = TraversalStrategy(ValidContext)
        strategy._check_context_type(context)
    
    def test_traversal_strategy_check_context_type_2(self):

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            strategy = TraversalStrategy(InvalidContext)