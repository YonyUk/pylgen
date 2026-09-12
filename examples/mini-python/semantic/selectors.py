from typing import List

from pylgen.analysis import ASTChildrenSelector
from pylgen.analysis.context import Context
from pylgen.common.types import AST

from grammar.asts import *

from .context import PythonContext

class DefaultSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def select_children(self, ast: AST, context: PythonContext) -> List[AST]: # type: ignore
        return ast.children()

class AssignASTSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def select_children(self, ast: AssignAST, context: PythonContext) -> List[AST]: # type: ignore
        return [ast.right]

class EvalFuncDefASTSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(PythonContext)
        self._children = []

    def select_children(self, ast: FuncDefAST, context: PythonContext) -> List[AST]: # type: ignore
        return self._children