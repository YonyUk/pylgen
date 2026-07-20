from pylgen.analysis.visitor import ASTWalker,TraversalStrategy
from pylgen.analysis.context import Context

class TestASTWalker:

    def test_ast_walker_creation(self):
        strategy = TraversalStrategy(Context)
        context = Context()
        walker = ASTWalker(context,strategy)