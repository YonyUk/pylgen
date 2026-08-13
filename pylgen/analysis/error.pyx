from .error_type import ErrorType

from hashlib import sha256

cdef class Error:

    def __init__(self,object type_,int line,int column,str msg) -> None:
    
        cdef bytes digest = sha256(f'{type_}-{line}-{column}-{msg}'.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i

        if not (isinstance(type_,ErrorType) or isinstance(type_,str)):
            raise TypeError('type_ must be a member of ErrorType')
        if isinstance(type_,str) and not type_ in ErrorType: # type:ignore
            raise ValueError('type_ must be a member of ErrorType')
        if isinstance(type_,str):
            self._type = ErrorType[type_] # type:ignore
        else:
            self._type = type_
        
        for i in range(8):
            h = (h << 8) | digest[i]
        
        self._hash = h
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
    
    def __hash__(self) -> int:
        return self._hash
    
    def __eq__(self, __o: object) -> bool:
        cdef Error other

        if not isinstance(__o,Error):
            return False
        
        other = __o

        return other._type == self._type and other._line == self._line and other._column == self._column and other._msg == self._msg

cdef class LexicalError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.LEXICAL, line, column, msg)

cdef class SyntaxError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.SYNTAX, line, column, msg)

cdef class SemanticError(Error):

    def __init__(self, str msg,int line, int column) -> None:
        super().__init__(ErrorType.SEMANTIC, line, column, msg)

cdef class RuntimeError(Error):

    def __init__(self,list[str] stack_trace,int line,int column,str msg) -> None:
        super().__init__(ErrorType.RUNTIME,line,column,msg)
        self._stack_trace = stack_trace
    
    @property
    def stack_trace(self) -> list[str]:
        return self._stack_trace