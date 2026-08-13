from typing import Any,List
import sys

from pylgen.common.types import AST
from pylgen.analysis.visitor import ASTChildrenSelector,ASTVisitor,TraversalStrategy
from pylgen.analysis.error import RuntimeError,SemanticError
from .context import ArithmeticExpressionContext
from .errors import (
    DivisionByZeroError,
    ModuleByZeroError,
    ModuleByNotIntegerError,
    ModuleWithComplexNumberError
)
from .grammar_symbols import VAR

class ArithmeticExpressionASTChildrenSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def select_children(self, ast: AST, context: ArithmeticExpressionContext) -> List[AST]:
        self._check_context_type(context)
        return ast.children()

class BinaryASTEvaluatorVisitor(ASTVisitor):
    _left_type:type
    _right_type:type
    _left_value:Any
    _right_value:Any
    _runtime_error = False

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._runtime_error = False
        self._left_type = type(context.get_ast_value(ast.left))
        self._left_value = context.get_ast_value(ast.left)
        self._right_type = type(context.get_ast_value(ast.right))
        self._right_value = context.get_ast_value(ast.right)

        if isinstance(self._left_value,RuntimeError):
            context.add_runtime_error(ast,self._left_value)
            self._runtime_error = True
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            self._runtime_error = True

class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value + self._right_value)

class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value - self._right_value)

class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value * self._right_value)

class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,DivisionByZeroError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value / self._right_value)

class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value ** self._right_value)

class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,ModuleByZeroError(context.stack_trace,ast.line,ast.column))
        elif self._right_type == complex or self._left_type == complex:
            context.add_runtime_error(ast,ModuleWithComplexNumberError(context.stack_trace,ast.line,ast.column))
        elif self._right_type != int:
            context.add_runtime_error(ast,ModuleByNotIntegerError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value % self._right_value)

class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._right_value = context.get_ast_value(ast.right)
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            return
        context.add_variable(ast.left.name,self._right_value)

class AtomicASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if '.' in ast.text:
            context.add_ast_value(ast,float(ast.text))
        else:
            context.add_ast_value(ast,int(ast.text))

class ExitASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        sys.exit(0)

class ClearASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        print('\033c',end="")


class VariableASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if not context.check_variable_in_context(ast.name):
            error = SemanticError(f'undeclared variable "{ast.name}"',ast.line,ast.column)
            context.add_semantic_error(error)

class AssignmentASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if ast.right.symbol == VAR:
            if not context.check_variable_in_context(ast.right.name):
                error = SemanticError(f'undeclared variable "{ast.right.name}"',ast.right.line,ast.right.column)
                context.add_semantic_error(error)

class PostOrderStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
        self._stack = []
        self._seen = []

    def init(self, root: AST) -> None:
        super().init(root)
        self._stack.append(root)

    def has_next(self) -> bool:
        return len(self._stack) > 0

    def current(self,context:ArithmeticExpressionContext) -> AST:
        self._check_context_type(context)
        selector = self._get_selector(self._stack[-1])
        children = selector.select_children(self._stack[-1],context)
        seen = self._stack[-1] in self._seen
        while children and not seen:
            self._seen.append(self._stack[-1])
            for child in children:
                self._stack.append(child)
            selector = self._get_selector(self._stack[-1])
            children = selector.select_children(self._stack[-1],context)
            seen = self._stack[-1] in self._seen
        return self._stack.pop()

    def reset(self) -> None:
        self._seen.clear()
        self._stack.clear()