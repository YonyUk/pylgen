import pytest

from pylgen.analysis.context import Context
from pylgen.analysis.visitor import ASTChildrenSelector
from pylgen.common.types import AST,Symbol

class ValidContext(Context):
    pass

class InvalidContext:
    pass

class TestASTChildrenSelector:

    def test_ast_children_selector_creation(self):

        context = Context()
        ast = AST(Symbol('n'),0,0)

        selector = ASTChildrenSelector(Context)

        selector._check_context_type(context)

        with pytest.raises(NotImplementedError):
            selector.select_children(ast,context)
    
    def test_ast_children_selector_creation_failed(self):

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            selector = ASTChildrenSelector(str)
    
    def test_ast_children_selector_check_context_type_1(self):

        context = ValidContext()
        visitor = ASTChildrenSelector(ValidContext)

        ast = AST(Symbol('s'),0,0)

        visitor._check_context_type(context)
    
    def test_ast_children_selector_check_context_type_2(self):
        
        context = InvalidContext()

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            visitor = ASTChildrenSelector(InvalidContext)