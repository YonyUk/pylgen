from hashlib import sha256
from typing import Set,Sequence
from common.types cimport Symbol
from parser.lr0_parser cimport LR0Item

cdef class LALRItem(LR0Item):
    
    def __init__(self, head: Symbol, left: Sequence[Symbol], right: Sequence[Symbol],lookaheads:Set[Symbol]=set()):
        super().__init__(head, left, right)
        self._lookaheads = lookaheads.copy()
    
    @property
    def lookaheads(self) -> Set[Symbol]:
        return self._lookaheads.copy()

    def __str__(self) -> str:
        cdef str left,right
        cdef list[str] left_l,right_l
        cdef Symbol sym

        left_l = [sym._symbol for sym in self._left]
        right_l = [sym._symbol for sym in self._right]
        left = ' '.join(left_l)
        right = ' '.join(right_l)
        return f'{self._head} -> {left} ◦ {right} f{self._lookaheads}'
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        cdef LALRItem other
        if not isinstance(__o,LALRItem):
            return False
        other = __o
        return self._head == other._head and self._left == other._left and self._right == other._right and other._lookaheads == self._lookaheads
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self.id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i

        for i in range(8):
            h = (h << 8) | digest[i]
        
        return h # type:ignore

cdef class LALRState:

    def __init__(self,items:Set[LALRItem],index:int=0):
        cdef list[str] ids = []
        cdef LALRItem item

        for item in items:
            ids.append(str(item))
        
        ids.sort()
        self._id = sha256('-'.join(ids).encode()).hexdigest()
        self._items = items.copy()
        self._index = index
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def index(self) -> int:
        return self._index

    @property
    def items(self) -> Set[LALRItem]:
        return self._items.copy()
    
    def __eq__(self, __o: object) -> bool:
        cdef LALRState other

        if not isinstance(__o,LALRState):
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