from typing import List

from pylgen.analysis import SemanticError,RuntimeError

############################################################################
# SEMANTIC ERRORS
############################################################################


class DivisionByZeroError(SemanticError):

    def __init__(self, line: int, column: int) -> None:
        super().__init__('division by zero not allowed', line, column)

class ModuleByZeroError(SemanticError):

    def __init__(self, line: int, column: int) -> None:
        super().__init__('module by zero not allowed', line, column)

class ModuleWithComplexError(SemanticError):

    def __init__(self, line: int, column: int) -> None:
        super().__init__('module not defined for complex numbers', line, column)

class UndeclaredVariableError(SemanticError):

    def __init__(self, name: str, line: int, column: int) -> None:
        super().__init__(f'undeclared variable "{name}"', line, column)

class UndeclaredFunctionError(SemanticError):

    def __init__(self, func_name: str, line: int, column: int) -> None:
        super().__init__(f'undeclared function "{func_name}"', line, column)

class OperationNotSupportedForTypesError(SemanticError):

    def __init__(self, left:str, right:str, operation:str, line: int, column: int) -> None:
        super().__init__(f'operation "{operation}" no supported for types "{left}" and "{right}"', line, column)

class OperationNotSupportedForTypeError(SemanticError):

    def __init__(self, target: str, operation:str, line: int, column: int) -> None:
        super().__init__(f'operation "{operation}" not supported for type "{target}"', line, column)

class FunctionAlreadyDefinedError(SemanticError):

    def __init__(self, func_name: str, line: int, column: int) -> None:
        super().__init__(f'function {func_name} already defined', line, column)

class ArgumentCountMissmatchError(SemanticError):

    def __init__(self, expected:List[int], got:int, line: int, column: int) -> None:
        super().__init__(f'arguments count missmatch error; expected {expected if expected else "no arguments"}, got {got}', line, column)

class InvalidInstructionError(SemanticError):

    def __init__(self,instruction:str, reason:str, line: int, column: int) -> None:
        super().__init__(f'invalid instruction "{instruction}"; {reason}', line, column)

############################################################################
# RUNTIME ERRORS
############################################################################

class OperationNotSupportedForTypeRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, operation:str, type_value:type) -> None:
        super().__init__(stack_trace, line, column, f'operation "{operation}" not supported for "{type_value}" type')

class OperationNotSupportedForTypesRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, operation:str, left_type_value:type, right_type_value:type) -> None:
        super().__init__(stack_trace, line, column, f'operation "{operation}" not supported for types "{left_type_value}" and "{right_type_value}"')

class DivizionByZeroRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'division by zero not allowed')

class ModuleByZeroRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'module by zero not allowed')

class ModuleWithComplexRuntimeError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'module with complexs not allowed')