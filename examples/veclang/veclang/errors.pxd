from pylgen.analisis.error cimport RuntimeError

cdef class DivisionByZeroError(RuntimeError):
    pass

cdef class ModuleByZeroError(RuntimeError):
    pass

cdef class UnSupportedOperationError(RuntimeError):
    pass

cdef class UnSupportedOperationForTypeError(UnSupportedOperationError):
    pass

cdef class UnSupportedOperationForTypesError(UnSupportedOperationError):
    pass

cdef class InvalidOperationError(RuntimeError):
    pass

cdef class BadRangeError(InvalidOperationError):
    pass

cdef class IndexOutOfRangeError(RuntimeError):
    pass