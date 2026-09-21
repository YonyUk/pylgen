from pylgen.analysis import ASTVisitor

from grammar.asts import *

from errors.errors import *
from .context import PythonContext

class AssignASTSemanticCheckingVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: AssignAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.define_var(ast.target.name)

class VariableASTSemanticCheckingVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: VariableAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if not context.exists_var(ast.name):
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            context.add_semantic_error(UndeclaredVariableError(ast.name,sl,sc,el,ec))

class FuncCallASTSemanticCheckingVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: FuncCallAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if not context.exists_func(ast.func_name):
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            context.add_semantic_error(UndeclaredFunctionError(ast.func_name,sl,sc,el,ec))
            return
        _,data,_ = context.get_func_data(ast.func_name)
        expected = []
        for variants in data:
            if variants is None:
                return
            expected.append(len(variants))
            if len(variants) == len(ast.args.args):
                return
        (sl,sc),(el,ec) = ast.args.start_position,ast.args.end_position
        context.add_semantic_error(ArgumentCountMissmatchError(expected,len(ast.args.args),sl,sc,el,ec))

class ReturnASTSemanticCheckingVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: ReturnAST | VoidReturnAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if not context.inside_function_scope:
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            reason = '"return" instruction must be inside a function body'
            context.add_semantic_error(InvalidInstructionError('return',reason,sl,sc,el,ec))

class BreakASTSemanticVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: BreakAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if not context.inside_loop_scope:
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            reason = '"break" instruction must be inside a loop body'
            context.add_semantic_error(InvalidInstructionError('break',reason,sl,sc,el,ec))

class ContinueASTSemanticVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: ContinueAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        if not context.inside_loop_scope:
            (sl,sc),(el,ec) = ast.start_position,ast.end_position
            reason = '"continue" instruction must be inside a loop body'
            context.add_semantic_error(InvalidInstructionError('continue',reason,sl,sc,el,ec))