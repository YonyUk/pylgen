from typing import List
from pylgen.common.types import RuntimeError

class DivisionByZeroError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line: int, start_column: int, end_line: int, end_column: int) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'division by zero not allowed')

class ModuleByZeroError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line: int, start_column: int, end_line: int, end_column: int) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'module by zero not allowed')

class ModuleByNotIntegerError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line: int, start_column: int, end_line: int, end_column: int) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'module by a not-integer not allowed')

class ModuleWithComplexNumberError(RuntimeError):

    def __init__(self, stack_trace: List[str], start_line: int, start_column: int, end_line: int, end_column: int) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'module operation not supported for complex numbers')