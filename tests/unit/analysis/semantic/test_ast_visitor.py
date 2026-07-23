import pytest

from pylgen.analysis.visitor import ASTVisitor
from pylgen.analysis.context import Context
from pylgen.common.types import AST,Symbol

class ValidContext(Context):
    pass

class InvalidContext:
    pass

class TestASTVisitor:

    def test_ast_visitor_creation(self):

        context = Context()
        visitor = ASTVisitor(Context)

        ast = AST(Symbol('s'),0,0)

        visitor._check_context_type(context)

        with pytest.raises(NotImplementedError):
            visitor.visit(ast,context)
    
    def test_ast_visitor_creation_failed(self):

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            visitor = ASTVisitor(str)
    
    def test_ast_visitor_check_context_type_1(self):

        context = ValidContext()
        visitor = ASTVisitor(ValidContext)

        ast = AST(Symbol('s'),0,0)

        visitor._check_context_type(context)
    
    def test_ast_visitor_check_context_type_2(self):
        
        context = InvalidContext()

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            visitor = ASTVisitor(InvalidContext)