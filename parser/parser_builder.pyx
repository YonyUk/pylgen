from typing import Set
from hashlib import sha256

from common.types cimport Symbol
from grammar.grammar cimport Grammar,Production,_augment_grammar
from .lr0_parser cimport LR0Item,LR0State

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
        return _clousure(items,g)
    
    @staticmethod
    def goto(items:Set[LR0Item],x:Symbol,g:Grammar) -> Set[LR0Item]:
        '''
        Args:
            items (Set[LR0Item])
            x (Symbol)
            g (Grammar)
        
        Returns:
            Set[LR0Item]: The next state for the given state and the symbol x
        '''
        return _goto(items,x,g)
    
    @staticmethod
    def get_canonical_lr0_states(g:Grammar) -> Set[LR0State]:
        '''
        Args:
            g (Grammar)
        
        Returns:
            Set[LR0State]: the set of lr0 states canonical
        '''
        return _get_canonical_lr0_states(g)

cdef set[LR0Item] _clousure(set[LR0Item] items,Grammar g):
    cdef LR0Item item,new_item
    cdef Production production
    cdef Symbol head
    cdef set[LR0Item] result = items.copy()
    cdef set[LR0Item] copy
    cdef bint change = True # type:ignore
    cdef str set_id
    cdef list[str] ids = []
    cdef tuple[str,str] key

    for item in items:
        ids.append(str(item))
    ids.sort()
    
    set_id = sha256('-'.join(ids).encode()).hexdigest()
    key = (g._id(),set_id)
    # checks for a precomputed value
    if key in _clousures:
        return _clousures[key]
    
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
    
    _clousures[key] = result
    return result

cdef set[LR0Item] _goto(set[LR0Item] items,Symbol x,Grammar g):
    cdef Symbol head
    cdef LR0Item item,new_item
    cdef set[LR0Item] result = set()

    for item in items:
        if len(item._right) > 0 and item._right[0] == x:
            new_item = LR0Item(item._head,item._left + [x],item._right[1:]) # type:ignore
            result.update(_clousure({new_item},g))
    
    return result

cdef set[LR0State] _get_canonical_lr0_states(Grammar g):
    cdef Grammar augmented = _augment_grammar(g)
    cdef LR0Item start = LR0Item(augmented._start_symbol,[],[g._start_symbol]) # type:ignore
    cdef LR0State state,new_state
    cdef set[LR0State] result = { LR0State(_clousure({start},augmented)) } # type:ignore
    cdef set[LR0State] copy
    cdef set[LR0Item] items
    cdef bint change = True # type:ignore
    cdef Symbol symbol

    while change:
        change = False # type:ignore
        copy = result.copy()

        for state in copy:
            for symbol in g._symbols:
                if symbol == augmented._end_symbol: continue
                items = _goto(state._items,symbol,g)
                if len(items) > 0:
                    new_state = LR0State(items,len(result)) # type:ignore
                    if not new_state in result:
                        change = True # type:ignore
                        result.add(new_state)
    
    return result