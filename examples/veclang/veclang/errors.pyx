from pylgen.common.types cimport RuntimeError

cdef class DivisionByZeroError(RuntimeError):

    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'Division by zero not allowed')

cdef class ModuleByZeroError(RuntimeError):
    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, 'Module by zero not allowed')

cdef class UnSupportedOperationError(RuntimeError):

    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column, str msg) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, msg)

cdef class UnSupportedOperationForTypeError(UnSupportedOperationError):

    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column,str operation ,type _type) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, f'operation "{operation}" not supported for type {_type}')

cdef class UnSupportedOperationForTypesError(UnSupportedOperationError):
    
    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column,str operation ,type _type1,type _type2) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, f'operation ({_type1} "{operation}" {_type2}) not supported')

cdef class InvalidOperationError(RuntimeError):

    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column, str msg) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, msg)

cdef class BadRangeError(InvalidOperationError):

    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, f'The args[1] < args[0] is not allowed')

cdef class IndexOutOfRangeError(RuntimeError):
    
    def __init__(self, list[str] stack_trace, int start_line, int start_column, int end_line, int end_column,int index, int size) -> None:
        super().__init__(stack_trace, start_line, start_column, end_line, end_column, f'Index {index} out of range (0-{size - 1})')