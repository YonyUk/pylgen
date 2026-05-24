from typing import Sequence,Set
from hashlib import sha256

from common.types cimport Symbol

cdef class LR0Item:

    def __init__(self,head:Symbol,left:Sequence[Symbol],right:Sequence[Symbol]):
        self._head = head
        self._left = list(left)
        self._right = list(right)
    
    @property
    def id(self) -> str:
        return str(self)
    
    @property
    def head(self) -> Symbol:
        return self._head
    
    @property
    def left(self) -> list[Symbol]:
        return self._left.copy()
    
    @property
    def right(self) -> list[Symbol]:
        return self._right.copy()

    def __str__(self) -> str:
        cdef str left,right
        cdef list[str] left_l,right_l
        cdef Symbol sym

        left_l = [sym._symbol for sym in self._left]
        right_l = [sym._symbol for sym in self._right]
        left = ' '.join(left_l)
        right = ' '.join(right_l)
        return f'{self._head} -> {left} ◦ {right}'
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        cdef LR0Item other
        if not isinstance(__o,LR0Item):
            return False
        other = __o
        return self._head == other._head and self._left == other._left and self._right == other._right
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self.id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i

        for i in range(8):
            h = (h << 8) | digest[i]
        
        return h # type:ignore

cdef class LR0State:

    def __init__(self,items:Set[LR0Item]):
        cdef list[str] ids = []
        cdef LR0Item item
        for item in items:
            ids.append(str(item))
        ids.sort()
        self._id = sha256('-'.join(ids).encode()).hexdigest()
        self._items = items.copy()
    
    @property
    def id(self) -> str:
        return self._id
    
    def __eq__(self, __o: object) -> bool:
        cdef LR0State other

        if not isinstance(__o,LR0State):
            return False
        other = __o
        return self._id == other._id
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self._id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        
        for i in range(8):
            h = (h << 8) | digest[i]
        
        return h # type:ignore