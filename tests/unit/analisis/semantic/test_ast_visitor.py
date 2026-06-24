import pytest

from pylgen.analisis.visitor import ASTVisitor
from pylgen.analisis.context import Context
from pylgen.common.types import AST,Symbol

class TestASTVisitor:

    def test_ast_visitor_creation(self):

        context = Context()
        visitor = ASTVisitor(Context)

        ast = AST(Symbol('s'),0,0)

        visitor._check_context_type(context)

        with pytest.raises(NotImplementedError):
            visitor.visit(ast,context)
    
    def test_ast_visitor_creation_failed(self):
        context = Context()

        with pytest.raises(ValueError,match='context_type must be a subclass of '):
            visitor = ASTVisitor(str)