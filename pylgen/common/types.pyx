from hashlib import sha256
from .enums import TokenType,ErrorType

cdef class Symbol:
    '''
    Class that represents a grammar symbol
    '''

    def __init__(self,str symbol,bint is_terminal = False,bint is_epsilon = False): # type:ignore
        '''
        Args:
            symbol (str): the symbol
            is_terminal (bool): says if this symbol is a terminal symbol
            is_epsilon (bool): says if this symbol is the epsilon symbol.
                A symbol only can be epsilon if is a terminal symbol
        
        Raises:
            ValueError('A symbol only can be epsilon if its a terminal symbol')
        '''
        cdef bytes digest = sha256(f'{symbol}-{is_terminal}-{is_epsilon}'.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        self._hash = h
        self._symbol = symbol
        self._is_terminal = is_terminal
        if is_epsilon and not is_terminal:
            raise ValueError('A symbol only can be epsilon if its a terminal symbol')
        self._is_epsilon = is_epsilon
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @property
    def is_terminal(self) -> bool:
        return self._is_terminal # type:ignore
    
    @property
    def is_epsilon(self) -> bool:
        return self._is_epsilon # type:ignore
    
    def __str__(self) -> str:
        return self._symbol
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self,other) -> bool:
        cdef Symbol o
        if not isinstance(other,Symbol):
            return False
        o = other
        return o._symbol == self._symbol and o._is_terminal == self._is_terminal and o._is_epsilon == self._is_epsilon
    
    def __hash__(self) -> int:
        return self._hash

cdef class AST:
    '''
    Abstract Syntax Tree class
    '''
    def __init__(self,Symbol symbol,int start_line,int start_column, int end_line, int end_column):
        '''
        Args:
            symbol (Symbol): internal symbol of this ast
            start_line (int): line in the source code where this ast starts
            start_column (int): column in the source code where this ast starts
            end_line (int): line in the source code where this ast ends
            end_column (int): column in the source code where this ast ends
        '''
        if start_line < 0 or start_column < 0:
            raise ValueError('start_line and start_column must be non-negative values')
        if end_line < start_line:
            raise ValueError('end_line cannot be less than start_line')
        if end_line == start_line and end_column <= start_column:
            raise ValueError('start_column must be less than end_column')
        self._symbol = symbol
        self._start_line = start_line
        self._start_column = start_column
        self._end_line = end_line
        self._end_column = end_column
        self._is_error = False # type:ignore
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol
    
    @property
    def start_position(self) -> tuple[int,int]:
        return (self._start_line,self._start_column)
    
    @property
    def end_position(self) -> tuple[int,int]:
        return (self._end_line,self._end_column)
    
    @property
    def is_error(self) -> bool:
        return self._is_error # type:ignore
    
    cpdef list[AST] children(self):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self._symbol._symbol
    
    def __repr__(self) -> str:
        return str(self)

cdef class Error:

    def __init__(self,object type_,int start_line,int start_column, int end_line, int end_column,str msg) -> None:
    
        cdef bytes digest = sha256(f'{type_}-{start_line}-{start_column}-{end_line}-{end_column}-{msg}'.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i

        if not (isinstance(type_,ErrorType) or isinstance(type_,str)):
            raise TypeError('type_ must be a member of ErrorType')
        if isinstance(type_,str) and not type_ in ErrorType: # type:ignore
            raise ValueError('type_ must be a member of ErrorType')
        if start_line < 0 or start_column < 0:
            raise ValueError('start_line and start_column must be non-negative values')
        if end_line < start_line:
            raise ValueError('end_line cannot be less than start_line')
        if end_line == start_line and end_column <= start_column:
            raise ValueError('start_column must be less than end_column')
        
        if isinstance(type_,str):
            self._type = ErrorType[type_] # type:ignore
        else:
            self._type = type_

        for i in range(8):
            h = (h << 8) | digest[i]
        
        self._hash = h
        self._start_line = start_line
        self._start_column = start_column
        self._end_line = end_line
        self._end_column = end_column
        self._msg = msg
    
    @property
    def start_position(self) -> tuple[int,int]:
        return (self._start_line,self._start_column)

    @start_position.setter
    def start_position(self,tuple[int,int] start_position):
        sl,sc = start_position

        if sl < 0 or sc < 0:
            raise ValueError('start_line and start_column must be non-negative values')

        if self._end_line < sl:
            raise ValueError('end_line cannot be less than start_line')

        if self._end_line == sl and self._end_column <= sc:
            raise ValueError('start_column must be less than end_column')

        self._start_line = sl
        self._start_column = sc
    
    @property
    def end_position(self) -> tuple[int,int]:
        return (self._end_line,self._end_column)
        
    @end_position.setter
    def end_position(self,tuple[int,int] end_position):
        el,ec = end_position

        if el < self._start_line:
            raise ValueError('end_line cannot be less than start_line')
            
        if el == self._start_line and ec <= self._start_column:
            raise ValueError('start_column must be less than end_column')

        self._end_line = el
        self._end_column = ec

    @property
    def type(self) -> ErrorType:
        return self._type # type:ignore
    
    @property
    def message(self) -> str:
        return self._msg
    
    def __str__(self) -> str:
        return f'{self._type} ERROR at line {self._start_line}: {self._msg}'
    
    def __repr__(self) -> str:
        return str(self)
    
    def __hash__(self) -> int:
        return self._hash
    
    def __eq__(self, __o: object) -> bool:
        cdef Error other

        if not isinstance(__o,Error):
            return False
        
        other = __o

        if other._type != self._type:
            return False
        
        if other._msg != self._msg:
            return False

        if other._start_line != self._start_line or other._start_column != self._start_column:
            return False
        
        if other._end_line != self._end_line or other._end_column != self._end_column:
            return False

        return True

cdef class LexicalError(Error):

    def __init__(self, str msg,int start_line,int start_column, int end_line, int end_column) -> None:
        super().__init__(ErrorType.LEXICAL, start_line, start_column, end_line, end_column,msg)

cdef class SyntaxError(Error):

    def __init__(self, str msg,int start_line,int start_column, int end_line, int end_column) -> None:
        super().__init__(ErrorType.SYNTAX, start_line, start_column, end_line, end_column, msg)

cdef class SemanticError(Error):

    def __init__(self, str msg,int start_line,int start_column, int end_line, int end_column) -> None:
        super().__init__(ErrorType.SEMANTIC, start_line, start_column, end_line, end_column, msg)

cdef class RuntimeError(Error):

    def __init__(self,list[str] stack_trace,int start_line,int start_column, int end_line, int end_column,str msg) -> None:
        super().__init__(ErrorType.RUNTIME,start_line,start_column,end_line,end_column,msg)
        self._stack_trace = stack_trace
    
    @property
    def stack_trace(self) -> list[str]:
        return self._stack_trace

cdef class ErrorAST(AST):
    '''
    Error Syntax Tree Class
    '''
    def __init__(self,Symbol symbol,int start_line,int start_column, int end_line, int end_column,set[SemanticError] errors):
        '''
        Args:
            symbol (Symbol): internal symbol of this ast
            start_line (int): line in the source code where this ast starts
            start_column (int): column in the source code where this ast starts
            end_line (int): line in the source code where this ast ends
            end_column (int): column in the source code where this ast ends
            errors (Set[SemanticError])
        '''
        if start_line < 0 or start_column < 0:
            raise ValueError('start_line and start_column must be non-negative values')
        if end_line < start_line:
            raise ValueError('end_line cannot be less than start_line')
        if end_line == start_line and end_column <= start_column:
            raise ValueError('start_column must be less than end_column')
        self._symbol = symbol
        self._start_line = start_line
        self._start_column = start_column
        self._end_line = end_line
        self._end_column = end_column
        self._is_error = True # type:ignore
        self._errors = errors

cdef class ASTListView:

    cdef inline AST _get(self,int idx):
        if idx < 0 or idx >= self._end - self._start:
            raise IndexError('ASTListView index out of range')
        return self._data[self._start + idx]

    cdef inline int _size(self):
        return self._end - self._start

    def __getitem__(self,int idx):
        return self._get(idx)

    def __len__(self):
        return self._size()

cdef class Token(AST):

    def __init__(self,str text, object type_, Symbol symbol, int line, int column):
        if not issubclass(type(type_),TokenType):
            raise ValueError('type_ parameter must be a subclass of TokenType')
        super().__init__(symbol,line,column,line,column + len(text))
        self._text = text
        self._type = type_
    
    cpdef list[AST] children(self):
        return []

    @property
    def text(self) -> str:
        return self._text
    
    @property
    def type(self) -> TokenType:
        return self._type # type:ignore