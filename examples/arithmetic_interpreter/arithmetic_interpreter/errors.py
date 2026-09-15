from typing import List
from pylgen.common.types import RuntimeError

class DivisionByZeroError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, source_line_interval_start: int, source_line_interval_end: int) -> None:
        super().__init__(stack_trace, line, column, source_line_interval_start, source_line_interval_end ,'division by zero not allowed')

class ModuleByZeroError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, source_line_interval_start: int, source_line_interval_end: int) -> None:
        super().__init__(stack_trace, line, column, source_line_interval_start, source_line_interval_end,'module by zero not allowed')

class ModuleByNotIntegerError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, source_line_interval_start: int, source_line_interval_end: int) -> None:
        super().__init__(stack_trace, line, column, source_line_interval_start, source_line_interval_end ,'module by a not-integer not allowed')

class ModuleWithComplexNumberError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int, source_line_interval_start: int, source_line_interval_end: int) -> None:
        super().__init__(stack_trace, line, column, source_line_interval_start, source_line_interval_end, 'module operation not supported for complex numbers')