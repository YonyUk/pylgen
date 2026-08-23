from hashlib import sha256
from typing import Sequence,Set
from ..common.types cimport Symbol
from .lr0_parser cimport LR0Item

cdef class LR1Item(LR0Item):

    def __init__(self, head: Symbol, left: Sequence[Symbol], right: Sequence[Symbol],lookahead:Symbol) -> None:
        cdef str _left,_right
        cdef list[str] left_l,right_l
        cdef Symbol sym
        cdef bytes digest
        cdef long long h = 0 # type:ignore
        cdef int i

        self._head = head
        self._left = list(left)
        self._right = list(right)
        self._lookahead = lookahead

        left_l = [sym._symbol for sym in self._left]
        right_l = [sym._symbol for sym in self._right]
        _left = ' '.join(left_l)
        _right = ' '.join(right_l)

        self._id = f'{self._head} -> {_left} ◦ {_right} ({self._lookahead})'

        digest = sha256(self._id.encode()).digest()
        for i in range(8):
            h = (h << 8) | digest[i]
        
        self._hash = h
    
    @property
    def lookahead(self) -> Symbol:
        return self._lookahead
    
    def __str__(self) -> str:
        return self._id
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        cdef LR1Item other

        if not isinstance(__o,LR1Item):
            return False
        
        other = __o
        return self._head == other._head and self._left == other._left and self._right == other.right and self._lookahead == other._lookahead
    
    def __hash__(self) -> int:
        return self._hash

cdef class LR1State:
    
    def __init__(self,items:Set[LR1Item],index:int=0):
        cdef list[str] ids = []
        cdef LR1Item item
        cdef bytes digest
        cdef long long h = 0 # type:ignore
        cdef int i

        for item in items:
            ids.append(str(item))
        
        ids.sort()
        self._id = sha256('-'.join(ids).encode()).hexdigest()
        self._items = items.copy()
        self._index = index

        digest = sha256(self._id.encode()).digest()
        for i in range(8):
            h = (h << 8) | digest[i]
        
        self._hash = h
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def index(self) -> int:
        return self._index

    @property
    def items(self) -> Set[LR1Item]:
        return self._items.copy()

    def __eq__(self, __o: object) -> bool:
        cdef LR1State other

        if not isinstance(__o,LR1State):
            return False
        
        other = __o
        return self._id == other._id
    
    def __hash__(self) -> int:
        return self._hash