from pylgen.analysis import ASTVisitor

from grammar.asts import FuncDefAST

from .context import PythonContext
from errors.errors import FunctionAlreadyDefinedError

class FuncDefCollectorASTVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: FuncDefAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if context.exists_func(ast.func_name):
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            context.add_semantic_error(FunctionAlreadyDefinedError(ast.func_name,sl,sc,el,ec))
        else:
            func_args = [var.name for var in ast.args.args]
            context.define_func(ast.func_name,ast.body,*func_args)