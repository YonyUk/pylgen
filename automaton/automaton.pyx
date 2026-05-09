from hashlib import sha256

cdef class State:
    '''
    State class for building automatons. This class is inmutable
    '''
    def __init__(self,str id,object value,bint is_accept=False): # type:ignore
        '''
        Args:
            id (str): id which identify to this state
            Two states with the same id are considered equals
        
            value (Any): the value contained inside this state

            is_accept (bool): tells if this state is an accepting state
        '''
        self._id = id
        self._value = value
        self._is_accept = is_accept
    
    @property
    def id(self) -> str:
        '''
        Returns:
            str: the id of this state
        '''
        return self._id
    
    @property
    def value(self) -> object:
        '''
        Returns:
            Any: the value contained inside this state
        '''
        return self._value
    
    @property
    def is_accept(self) -> bool:
        '''
        Returns:
            bool: if this state is accepting or not
        '''
        return self._is_accept # type:ignore
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o,State): return False
        return __o.id == self._id
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self._id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        return h # type:ignore