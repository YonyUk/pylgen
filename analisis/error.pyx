from .error_type import ErrorType

cdef class Error:

    def __init__(self,object type_,int line,int column,str msg) -> None:
        if not (isinstance(type_,ErrorType) or isinstance(type_,str)):
            raise ValueError('type_ must be a member of ErrorType')
        if isinstance(type_,str) and not type_ in ErrorType: # type:ignore
            raise ValueError('type_ must be a member of ErrorType')
        if isinstance(type_,str):
            self._type = ErrorType[type_] # type:ignore
        else:
            self._type = type
        self._line = line
        self._column = column
        self._msg = msg
    
    @property
    def line(self) -> int:
        return self._line

    @property
    def column(self) -> int:
        return self._column
    
    @property
    def type(self) -> ErrorType:
        return self._type # type:ignore

    @property
    def message(self) -> str:
        return f'{self._type} ERROR at line {self._line}, column {self._column}: {self._msg}'
    
    def __str__(self) -> str:
        return self.message
    
    def __repr__(self) -> str:
        return self.message

cdef class LexicError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.LEXIC, line, column, msg)

cdef class SintaxError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.SINTAX, line, column, msg)

cdef class SemanticError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.SEMANTIC, line, column, msg)