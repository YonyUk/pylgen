from typing import List

from pylgen.common.types import SemanticError,RuntimeError

############################################################################
# SEMANTIC ERRORS
############################################################################


class DivisionByZeroError(SemanticError):

    def __init__(self, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__('division by zero not allowed', start_line,start_column,end_line,end_column)

class ModuleByZeroError(SemanticError):

    def __init__(self, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__('module by zero not allowed', start_line,start_column,end_line,end_column)

class ModuleWithComplexError(SemanticError):

    def __init__(self, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__('module not defined for complex numbers', start_line,start_column,end_line,end_column)

class UndeclaredVariableError(SemanticError):

    def __init__(self, name: str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'undeclared variable "{name}"', start_line,start_column,end_line,end_column)

class UndeclaredFunctionError(SemanticError):

    def __init__(self, func_name: str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'undeclared function "{func_name}"', start_line,start_column,end_line,end_column)

class OperationNotSupportedForTypesError(SemanticError):

    def __init__(self, left:str, right:str, operation:str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'operation "{operation}" no supported for types "{left}" and "{right}"', start_line,start_column,end_line,end_column)

class OperationNotSupportedForTypeError(SemanticError):

    def __init__(self, target: str, operation:str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'operation "{operation}" not supported for type "{target}"', start_line,start_column,end_line,end_column)

class FunctionAlreadyDefinedError(SemanticError):

    def __init__(self, func_name: str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'function {func_name} already defined', start_line,start_column,end_line,end_column)

class ArgumentCountMissmatchError(SemanticError):

    def __init__(self, expected:List[int], got:int, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'arguments count missmatch error; expected {expected if expected else "no arguments"}, got {got}', start_line,start_column,end_line,end_column)

class InvalidInstructionError(SemanticError):

    def __init__(self,instruction:str, reason:str, start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(f'invalid instruction "{instruction}"; {reason}', start_line,start_column,end_line,end_column)

############################################################################
# RUNTIME ERRORS
############################################################################

class OperationNotSupportedForTypeRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line:int,start_column:int,end_line:int,end_column:int, operation:str, type_value:type) -> None:
        super().__init__(stack_trace, start_line,start_column,end_line,end_column,f'operation "{operation}" not supported for "{type_value}" type')

class OperationNotSupportedForTypesRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line:int,start_column:int,end_line:int,end_column:int, operation:str, left_type_value:type, right_type_value:type) -> None:
        super().__init__(stack_trace, start_line,start_column,end_line,end_column,f'operation "{operation}" not supported for types "{left_type_value}" and "{right_type_value}"')

class DivizionByZeroRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(stack_trace, start_line,start_column,end_line,end_column,'division by zero not allowed')

class ModuleByZeroRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(stack_trace, start_line,start_column,end_line,end_column,'module by zero not allowed')

class ModuleWithComplexRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line:int,start_column:int,end_line:int,end_column:int) -> None:
        super().__init__(stack_trace, start_line,start_column,end_line,end_column,'module with complexs not allowed')