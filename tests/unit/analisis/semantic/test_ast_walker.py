from pylgen.analisis.visitor import ASTWalker,TraversalStrategy
from pylgen.analisis.context import Context

class TestASTWalker:

    def test_ast_walker_creation(self):
        strategy = TraversalStrategy(Context)
        context = Context()
        walker = ASTWalker(context,strategy)