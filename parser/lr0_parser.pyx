from typing import Sequence

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