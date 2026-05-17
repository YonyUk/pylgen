from hashlib import sha256

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
        cdef bytes digest = sha256(f'{self._symbol}-{self._is_terminal}-{self._is_epsilon}'.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        return h # type:ignore

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
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol
    
    @property
    def line(self) -> int:
        return self._line
    
    @property
    def column(self) -> int:
        return self._column
    
    def __str__(self) -> str:
        return self._symbol._symbol
    
    def __repr__(self) -> str:
        return str(self)