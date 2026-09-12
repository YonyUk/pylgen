from pylgen.analysis import ASTVisitor,ASTWalker
from pylgen.analysis.context import Context
from pylgen.common.types import AST

from grammar.asts import *
from grammar.asts import BinaryAST

from errors.errors import *
from .context import PythonContext,Signals

class VariableASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: VariableAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_val(context.get_var(ast.name))

class MinusMathExprASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: MinusMathExprAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        val = context.pop_val()
        if type(val) != int and type(val) != float and type(val) != complex:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'-',type(val)))
        else:
            context.push_val(-val)

class NotBoolExprASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: NotBoolExprAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        val = context.pop_val()
        context.push_val(not val)

class BinaryASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)
        self._left_type = None
        self._right_type = None
        self._left_value = None
        self._right_value = None

    def visit(self, ast: BinaryAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        self._right_value = context.pop_val()
        self._left_value = context.pop_val()
        self._left_type = type(self._left_value)
        self._right_type = type(self._right_value)

class PlusEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: PlusEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str and self._right_type != str or self._right_type == str and self._left_type != str:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,plus.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value + self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'+',type(None)))

class MinusEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: MinusEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,minus.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value - self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'-',type(None)))

class MulEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: MulEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str and self._right_type == str:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,mul.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value * self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'*',type(None)))

class DivEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: DivEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._right_value == 0:
                context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
            elif self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,div.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value / self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'/',type(None)))

class IntDivEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: IntDivEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._right_value == 0:
                context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
            elif self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,int_div.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value // self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'//',type(None)))

class ModEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: ModEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
                if self._right_value == 0:
                    context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
                elif self._left_type == complex or self._right_type == complex:
                    context.add_runtime_error(ast,ModuleWithComplexRuntimeError(context.stack_trace,ast.line,ast.column))
                elif self._left_type == str or self._right_type == str:
                    error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,mod.symbol,str)
                    context.add_runtime_error(ast,error)
                else:
                    context.assign_var(ast.variable.name,self._left_value % self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'%',type(None)))

class PowEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: PowEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,power.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.assign_var(ast.variable.name,self._left_value ** self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'**',type(None)))

class BitOrEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BitOrEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.assign_var(ast.variable.name,self._left_value | self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'|',type(None)))

class BitAndEqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BitAndEqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.assign_var(ast.variable.name,self._left_value & self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'&',type(None)))

class EqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: EqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        context.push_val(self._left_value == self._right_value)

class NeqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: NeqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        context.push_val(self._left_value != self._right_value)

class LeASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: LeAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None and self._right_value is None):
            has_error = self._left_type == str and (self._right_type == bool or self._right_type == int or self._right_type == float or self._right_type == complex)
            has_error |= self._right_type == str and (self._left_type == bool or self._left_type == int or self._left_type == float or self._left_type == complex)
            if has_error:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,le.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value < self._right_value) # type: ignore
        else:
            error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,le.symbol,type(None))
            context.add_runtime_error(ast,error)

class LeqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: LeqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None and self._right_value is None):
            has_error = self._left_type == str and (self._right_type == bool or self._right_type == int or self._right_type == float or self._right_type == complex)
            has_error |= self._right_type == str and (self._left_type == bool or self._left_type == int or self._left_type == float or self._left_type == complex)
            if has_error:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,leq.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value <= self._right_value) # type: ignore
        else:
            error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,leq.symbol,type(None))
            context.add_runtime_error(ast,error)

class GeASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: GeAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None and self._right_value is None):
            has_error = self._left_type == str and (self._right_type == bool or self._right_type == int or self._right_type == float or self._right_type == complex)
            has_error |= self._right_type == str and (self._left_type == bool or self._left_type == int or self._left_type == float or self._left_type == complex)
            if has_error:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,ge.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value > self._right_value) # type: ignore
        else:
            error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,ge.symbol,type(None))
            context.add_runtime_error(ast,error)

class GeqASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: GeqAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None and self._right_value is None):
            has_error = self._left_type == str and (self._right_type == bool or self._right_type == int or self._right_type == float or self._right_type == complex)
            has_error |= self._right_type == str and (self._left_type == bool or self._left_type == int or self._left_type == float or self._left_type == complex)
            if has_error:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,geq.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value >= self._right_value) # type: ignore
        else:
            error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,geq.symbol,type(None))
            context.add_runtime_error(ast,error)

class AssignASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AssignAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        right_value = context.pop_val()
        context.define_var(ast.target.name)
        context.assign_var(ast.target.name,right_value)

class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: PlusAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast,context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str and self._right_type != str or self._right_type == str and self._left_type != str:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,plus.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value + self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'+',type(None)))

class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: MinusAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,minus.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value - self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'-',type(None)))

class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: MulAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str and self._right_type == str:
                error = OperationNotSupportedForTypesRuntimeError(context.stack_trace,ast.line,ast.column,mul.symbol,self._left_type,self._right_type) # type: ignore
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value * self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'*',type(None)))

class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: DivAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._right_value == 0:
                context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
            elif self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,div.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value / self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'/',type(None)))

class IntDivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: IntDivAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._right_value == 0:
                context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
            elif self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,int_div.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value // self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'//',type(None)))

class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: ModAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
                if self._right_value == 0:
                    context.add_runtime_error(ast,DivizionByZeroRuntimeError(context.stack_trace,ast.line,ast.column))
                elif self._left_type == complex or self._right_type == complex:
                    context.add_runtime_error(ast,ModuleWithComplexRuntimeError(context.stack_trace,ast.line,ast.column))
                elif self._left_type == str or self._right_type == str:
                    error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,mod.symbol,str)
                    context.add_runtime_error(ast,error)
                else:
                    context.push_val(self._left_value % self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'%',type(None)))

class PowASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: PowAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            if self._left_type == str or self._right_type == str:
                error = OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,power.symbol,str)
                context.add_runtime_error(ast,error)
            else:
                context.push_val(self._left_value ** self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'**',type(None)))

class OrASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: OrAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.push_val(self._left_value or self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'|',type(None)))

class AndASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AndAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.push_val(self._left_value and self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'&',type(None)))

class BitOrASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BitOrAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.push_val(self._left_value | self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'|',type(None)))

class BitAndASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BitAndAST, context: PythonContext) -> None: # type: ignore
        super().visit(ast, context)
        if not (self._left_value is None or self._right_value is None):
            context.push_val(self._left_value & self._right_value)
        else:
            context.add_runtime_error(ast,OperationNotSupportedForTypeRuntimeError(context.stack_trace,ast.line,ast.column,'&',type(None)))

class NumberASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: NumberAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_val(ast.type(ast.value))

class BooleanASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: BooleanAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_val(True if ast.val == 'True' else False)

class StringASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: StringAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_val(ast.value)

class FuncCallASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: FuncCallAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        is_user_defined,_,_ = context.get_func_data(ast.func_name)
        if not is_user_defined:
            args = []
            for _ in range(len(ast.args.args)):
                args.insert(0,context.pop_val())
            val = context.call_func(ast.func_name,*args)
            context.push_val(val)

class VoidReturnASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: VoidReturnAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_val(None)
        context.push_signal(Signals.RETURN)

class ReturnASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: ReturnAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_signal(Signals.RETURN)

class BreakASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: BreakAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_signal(Signals.BREAK)

class ContinueASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(PythonContext)

    def visit(self, ast: ContinueAST, context: PythonContext) -> None: # type: ignore
        self._check_context_type(context)
        context.push_signal(Signals.CONTINUE)