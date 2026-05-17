from typing import List,Tuple
from hashlib import sha256
from common.types cimport Symbol

cdef class Production:

    def __init__(self,Symbol head,list[Symbol] production):
        '''
        Args:
            head (Symbol): symbol that produces the given list of symbols
            production (List[Symbol])
        
        Raises:
            ValueError("head can't be a terminal symbol")
        '''
        cdef Symbol symbol
        cdef list[str] prod = [symbol._symbol for symbol in production]
        if head._is_terminal:
            raise ValueError("head can't be a terminal symbol")
        self._head = head
        self._production = production
        self._id = f'{head} -> {",".join(prod)}'
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def head(self) -> Symbol:
        return self._head
    
    @property
    def production(self) -> List[Symbol]:
        return self._production
    
    def __str__(self) -> str:
        return self._id
    
    def __repr__(self) -> str:
        return self._id
    
    def __eq__(self, o) -> bool:
        cdef Production other
        if not isinstance(o,Production):
            return False
        other = o
        if other._head != self._head:
            return False
        return self._production == other._production
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self._id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        return h # type:ignore

cdef class ProductionsSet:

    def __init__(self):
        self._productions = {}
    
    @property
    def productions(self) -> List[List[Symbol]]:
        cdef list[list[Symbol]] result = []
        cdef list[Symbol] production

        for production in self._productions.values():
            result.append(production.copy())
        
        return result
    
    def __iadd__(self,production:Tuple[Symbol,...]) -> ProductionsSet:
        cdef Symbol symbol
        cdef list[str] p_ids = []
        cdef str p_id

        for symbol in production:
            p_ids.append(symbol._symbol)
        
        p_id = ','.join(p_ids)

        if not p_id in self._productions:
            self._productions[p_id] = list(production)
        
        return self