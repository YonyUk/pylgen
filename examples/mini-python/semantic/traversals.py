from pylgen.analysis import TraversalStrategy
from pylgen.common.types import AST

from .context import PythonContext,Signals

from grammar.symbols import *
from grammar.asts import FuncCallAST

class PostOrder(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(PythonContext)
        self._stack = []
        self._has_next = False

    def _push_children(self,ast:AST,context:PythonContext) -> None:
        selector = self._get_selector(ast)
        children = selector.select_children(ast,context)
        for i in range(len(children) - 1, -1 , -1):
            self._stack.append((False,children[i]))

    def init(self, root: AST) -> None:
        self._stack = [(False,root)]
        self._has_next = True

    def reset(self) -> None:
        self._has_next = False
        self._stack.clear()

    def has_next(self) -> bool:
        return self._has_next

    def current(self, context: PythonContext) -> AST: # type: ignore
        while self._stack:
            processed,ast = self._stack[-1]
            if not processed:
                self._stack[-1] = (True,ast)
                self._push_children(ast,context)
            else:
                self._stack.pop()
                if not self._stack:
                    self._has_next = False
                return ast

class CheckerPostOrder(PostOrder):

    def current(self, context: PythonContext) -> AST: # type: ignore
        while self._stack:
            processed,ast = self._stack[-1]
            if not processed:
                if ast.symbol == FuncDef:
                    context.push_new_scope()
                    context.enter_function_def_scope()
                    _,func_args,_ = context.get_func_data(ast.func_name) # type: ignore
                    for variant in func_args:
                        if len(variant) == len(ast.args.args): # type: ignore
                            for var in variant:
                                context.define_var(var)
                            break
                elif ast.symbol == WhileSmt:
                    context.enter_loop_scope()
                self._stack[-1] = (True,ast)
                self._push_children(ast,context)
            else:
                self._stack.pop()
                if not self._stack:
                    self._has_next = False
                if ast.symbol == FuncDef:
                    context.pop_scope()
                    context.exit_function_def_scope()
                elif ast.symbol == WhileSmt:
                    context.exit_loop_scope()
                return ast

class EvalPostOrder(PostOrder):

    def __init__(self) -> None:
        super().__init__()
        self._function_has_returned = []
        self._conditional_scopes = []

    def _handle_func_call(self,ast:FuncCallAST,context:PythonContext):
        user_defined,func_args,body = context.get_func_data(ast.func_name) # type: ignore
        if user_defined:
            for variant in func_args:
                if len(variant) == len(ast.args.args):
                    call_args = [context.pop_val() for _ in range(len(variant))]
                    context.push_new_scope()
                    context.push_trace(ast.func_name) # type: ignore
                    self._stack.append((False,body))
                    self._function_has_returned.append(False)
                    for i in range(len(variant)):
                        context.define_var(variant[i])
                        context.assign_var(variant[i],call_args[i])

    def current(self, context: PythonContext) -> AST: # type: ignore
        if context.get_runtime_errors():
            self._has_next = False

        while self._has_next and not context.get_runtime_errors():

            processed,ast = self._stack[-1]

            if not processed:

                if context.current_signal in (Signals.CONTINUE,Signals.BREAK) and ast.symbol != WhileBody:
                    self._stack.pop()
                    continue

                if context.current_signal == Signals.RETURN and ast.symbol != FuncBody:
                    self._stack.pop()
                    continue

                if ast.symbol == PythonInstruction:
                    context._ebps.append(len(context._eval_stack))
                elif ast.symbol == ReturnSmt:
                    self._function_has_returned[-1] = True
                elif ast.symbol in (IfSmt,IfElseSmt,IfElifSmt,IfElifElseSmt):
                    self._conditional_scopes.append(ast.symbol)
                elif ast.symbol == IfBody:
                    condition = context.pop_val()
                    if condition:
                        while self._stack[-1][1].symbol != self._conditional_scopes[-1]:
                            self._stack.pop()
                        self._stack.append((processed,ast))
                    else:
                        self._stack.pop()
                        continue
                elif ast.symbol == WhileBody:
                    condition = context.pop_val()
                    if not condition:
                        self._stack.pop()
                        continue

                self._stack[-1] = (True,ast)
                self._push_children(ast,context)
                
            else:
                    
                self._stack.pop()
                if not self._stack:
                    self._has_next = False

                if context.current_signal != Signals.BREAK and ast.symbol == WhileBody:
                    _,w_ast = self._stack[-1]
                    self._stack[-1] = (False,w_ast)

                if ast.symbol == WhileBody and context.current_signal in (Signals.BREAK,Signals.CONTINUE):
                    context.pop_signal()
                elif ast.symbol == FuncBody and context.current_signal == Signals.RETURN:
                    context.pop_signal()
                    has_returned = self._function_has_returned.pop()
                    if has_returned:
                        return_val = context.pop_val()
                    else:
                        return_val = None
                    context.pop_scope()
                    context.pop_trace()
                    context.push_val(return_val)
                elif ast.symbol == FuncCall:
                    self._handle_func_call(ast,context) # type: ignore
                elif ast.symbol in (IfSmt,IfElseSmt,IfElifSmt,IfElifElseSmt):
                    self._conditional_scopes.pop()
                elif ast.symbol == PythonInstruction:
                    del context._eval_stack[context._ebps.pop():]

                return ast

    def reset(self) -> None:
        super().reset()
        self._function_has_returned.clear()
        self._conditional_scopes.clear()