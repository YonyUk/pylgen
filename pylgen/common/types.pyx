from ..analysis.error cimport SemanticError

from hashlib import sha256
from .enums import TokenType

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
    def __init__(self,Symbol symbol,int line,int column):
        '''
        Args:
            symbol (Symbol): internal symbol of this ast
            line (int): line in the source code where this ast is located
            column (int): column in the source code where this ast is located
        '''
        self._symbol = symbol
        if line < 0 or column < 0:
            raise ValueError('line and column must be non-negative values')
        self._line = line
        self._column = column
        self._is_error = False # type:ignore
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol
    
    @property
    def line(self) -> int:
        return self._line
    
    @property
    def column(self) -> int:
        return self._column
    
    @property
    def is_error(self) -> bool:
        return self._is_error # type:ignore
    
    cpdef list[AST] children(self):
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self._symbol._symbol
    
    def __repr__(self) -> str:
        return str(self)

cdef class ErrorAST(AST):
    '''
    Error Syntax Tree Class
    '''
    def __init__(self,Symbol symbol,int line,int column,set[SemanticError] errors):
        '''
        Args:
            symbol (Symbol): internal symbol of this ast
            line (int): line in the source code where this ast is located
            column (int): column in the source code where this ast is located
            error (Error)
        '''
        self._symbol = symbol
        if line < 0 or column < 0:
            raise ValueError('line and column must be non-negative values')
        self._line = line
        self._column = column
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
        super().__init__(symbol, line, column)
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