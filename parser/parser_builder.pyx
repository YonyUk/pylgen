from typing import Set
from hashlib import sha256

from common.types cimport Symbol
from grammar.grammar cimport Grammar,Production
from .lr0_parser cimport LR0Item

_clousures:dict[tuple[str,str],set[LR0Item]] = {}

cdef class ParserBuilder:

    @staticmethod
    def clear_cache() -> None:
        _clousures.clear()

    @staticmethod
    def clousure(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]:
        '''
        Args:
            items (Set[LR0Item])
        
        Returns:
            Set[LR0Item]: the clousure of the given set
        '''
        cdef LR0Item item
        cdef str set_id
        cdef list[str] ids = []
        cdef tuple[str,str] key
        for item in items:
            ids.append(str(item))
        ids.sort()
        
        set_id = sha256('-'.join(ids).encode()).hexdigest()
        key = (g._id(),set_id)
        if not key in _clousures:
            _clousures[key] = _clousure(items,g)
        return _clousures[key]

cdef set[LR0Item] _clousure(set[LR0Item] items,Grammar g):
    cdef LR0Item item,new_item
    cdef Production production
    cdef Symbol head
    cdef set[LR0Item] result = items.copy()
    cdef set[LR0Item] copy
    cdef bint change = True # type:ignore

    while change:
        change = False # type:ignore
        
        copy = result.copy()
        
        for item in copy:
            if len(item._right) > 0:
                head = item._right[0]
                if not head._is_terminal:
                    for production in g._productions_by_symbol[head]:
                        new_item = LR0Item(head,[],production._production) # type:ignore
                        if not new_item in result:
                            change = True # type:ignore
                            result.add(new_item)
    
    return result