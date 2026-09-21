from typing import Any, List, Set, Tuple
from enum import StrEnum

from pylgen.analysis import Context
from pylgen.common.types import AST,RuntimeError

import sys

class Signals(StrEnum):

    CONTINUE = 'CONTINUE'
    BREAK = 'BREAK'
    RETURN = 'RETURN'

class InteralException(Exception):

    def __init__(self, msg:str, *args: object) -> None:
        super().__init__(*args)
        self._msg = msg

    @property
    def message(self) -> str:
        return self._msg

class UndeclaredVariableException(InteralException):

    def __init__(self, name:str,*args: object) -> None:
        super().__init__(f'Undeclared variable {name}',*args)
        self._name = name

    @property
    def name(self) -> str:
        return self._name
    
class FunctionAlreadyDefinedException(InteralException):

    def __init__(self, func_name:str,*args: object) -> None:
        super().__init__(f'function {func_name} already defined',*args)
        self._func_name = func_name

    @property
    def func_name(self) -> str:
        return self._func_name

class FuncDefContainer:

    def __init__(self) -> None:
        self._table = {}

    @property
    def functions(self) -> Set[str]:
        return set(self._table.keys())

    def define_func(self,func_name:str,body:AST,*args) -> None:
        if func_name in self._table:
            raise FunctionAlreadyDefinedException(func_name)
        self._table[func_name] = ([args],body)

    def get_func_data(self,func_name:str) -> Tuple[List[Tuple[str]],AST]:
        return self._table[func_name]

    def reset(self) -> None:
        self._table.clear()

class VariableManager:

    def __init__(self) -> None:
        self._scopes = [{}]

    def define_var(self,name:str) -> None:
        self._scopes[-1][name] = None

    def assign_var(self,name:str,value:Any) -> None:
        for i in range(len(self._scopes) - 1, -1, -1):
            if name in self._scopes[i]:
                self._scopes[i][name] = value
                return
        raise UndeclaredVariableException(name)

    def get_var(self,name:str) -> Any:
        for i in range(len(self._scopes) - 1, -1, -1):
            if name in self._scopes[i]:
                return self._scopes[i][name]
        raise UndeclaredVariableException(name)

    def exists(self,name:str) -> bool:
        for i in range(len(self._scopes) - 1, -1, -1):
            if name in self._scopes[i]:
                return True
        return False

    def push_scope(self) -> None:
        self._scopes.append({})

    def pop_scope(self) -> None:
        self._scopes.pop()

    def reset(self) -> None:
        self._scopes = [{}]

class BuiltInFunctions:

    def __init__(self) -> None:
        self._built_ins = {
            'print':self._print,
            'clear':self._clear,
            'exit':self._exit,
            'input':self._input
        }
        self._func_data = {
            'print':[None],
            'clear':[tuple()],
            'exit':[tuple()],
            'input':[tuple(),('message',)]
        }

    @property
    def built_ins(self) -> Set[str]:
        return set(self._built_ins.keys())

    def call_func(self, func_name:str, *args) -> Any:
        return self._built_ins[func_name](*args)

    def get_func_data(self,func_name:str) -> Tuple[List[Tuple[str] | None],AST]:
        return self._func_data[func_name],None # type: ignore

    def _print(self,*args) -> None:
        sys.stdout.write(' '.join(list(map(lambda arg:f'{arg}',args))))
        sys.stdout.write('\n')

    def _clear(self,*args) -> None:
        sys.stdout.write('\033c')

    def _exit(self,*args) -> None:
        sys.exit(0)

    def _input(self,*args) -> str:
        return input(args[0]) if len(args) > 0 else input()

class PythonContext(Context):

    def __init__(self) -> None:
        super().__init__()
        self._ebps = [0]
        self._eval_stack = []
        self._runtime_errors = set()
        self._built_ins = BuiltInFunctions()
        self._user_defined_functions = FuncDefContainer()
        self._vars_manager = VariableManager()
        self._function_scope_depth = 0
        self._loop_scope_depth = 0
        self._signals = []

    @property
    def last_instruction_result(self) -> Any:
        return self._eval_stack[-1] if self._eval_stack else None

    @property
    def inside_function_scope(self) -> bool:
        return self._function_scope_depth > 0

    @property
    def inside_loop_scope(self) -> bool:
        return self._loop_scope_depth > 0

    @property
    def current_signal(self) -> Signals | None:
        return self._signals[-1] if self._signals else None

    def enter_function_def_scope(self):
        self._function_scope_depth += 1

    def exit_function_def_scope(self):
        self._function_scope_depth -= 1

    def enter_loop_scope(self):
        self._loop_scope_depth += 1

    def exit_loop_scope(self):
        self._loop_scope_depth -= 1

    def push_signal(self,signal:Signals) -> None:
        self._signals.append(signal)

    def pop_signal(self) -> None:
        self._signals.pop()

    def exists_func(self,func_name:str) -> bool:
        return func_name in self._built_ins.built_ins or func_name in self._user_defined_functions.functions

    def get_func_data(self, func_name:str) -> Tuple[bool,List[Tuple[str]],AST]:
        if func_name in self._user_defined_functions.functions:
            args,body = self._user_defined_functions.get_func_data(func_name)
            return True, args, body
        args,_ = self._built_ins.get_func_data(func_name)
        return False, args, _ # type: ignore

    def call_func(self,func_name:str,*args) -> Any:
        if func_name in self._built_ins.built_ins:
            return self._built_ins.call_func(func_name,*args)
        return self._user_defined_functions.get_func_data(func_name)

    def define_func(self,func_name:str,body:AST,*args):
        self._user_defined_functions.define_func(func_name,body,*args)

    def exists_var(self,name:str) -> bool:
        return self._vars_manager.exists(name)

    def define_var(self,name:str) -> None:
        self._vars_manager.define_var(name)

    def assign_var(self,name:str,value:Any) -> None:
        self._vars_manager.assign_var(name,value)

    def get_var(self,name:str) -> Any:
        return self._vars_manager.get_var(name)

    def push_val(self,val:Any) -> None:
        self._eval_stack.append(val)

    def pop_val(self) -> Any:
        return self._eval_stack.pop()

    def push_new_scope(self) -> None:
        self._vars_manager.push_scope()
        self._ebps.append(len(self._eval_stack))

    def pop_scope(self) -> None:
        self._vars_manager.pop_scope()
        del self._eval_stack[self._ebps.pop():]

    def add_runtime_error(self, ast: AST, error: RuntimeError) -> None:
        if not error in self._runtime_errors:
            self._runtime_errors.add(error)

    def clear_runtime_errors(self) -> None:
        self._runtime_errors.clear()

    def get_runtime_errors(self) -> List[RuntimeError]:
        return list(self._runtime_errors)

    def reset(self) -> None:
        super().reset()
        self._eval_stack.clear()
        self._vars_manager.reset()
        self._user_defined_functions.reset()
        self._loop_scope_depth = 0
        self._function_scope_depth = 0
        self._eval_stack.clear()
        del self._ebps[1:]
        self._signals.clear()