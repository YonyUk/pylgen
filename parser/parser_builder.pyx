from typing import Set,Tuple
from hashlib import sha256

from common.types cimport Symbol
from common.table cimport Table
from grammar.grammar cimport Grammar,Production,_augment_grammar
from .lr0_parser cimport LR0Item,LR0State
from .lalr_parser cimport LALRState

_clousures:dict[tuple[str,str],set[LR0Item] | set[LALRItem]] = {}

cdef class ParserBuilder:

    @staticmethod
    def clear_cache() -> None:
        _clousures.clear()

    @staticmethod
    def clousure_lr0(items:Set[LR0Item],g:Grammar) -> Set[LR0Item]:
        '''
        Args:
            items (Set[LR0Item])
        
        Returns:
            Set[LR0Item]: the clousure of the given set
        '''
        return _clousure_lr0(items,g)
    
    @staticmethod
    def clousure_lalr(items:Set[LALRItem],g:Grammar) -> Set[LALRItem]:
        '''
        Args:
            items (Set[LALRItem])
        
        Returns:
            Set[LALRItem]: the clousure of the given set
        '''
        return _clousure_lalr(items,g)
    
    @staticmethod
    def goto_lr0(items:Set[LR0Item],x:Symbol,g:Grammar) -> Set[LR0Item]:
        '''
        Args:
            items (Set[LR0Item])
            x (Symbol)
            g (Grammar)
        
        Returns:
            Set[LR0Item]: The next state for the given state and the symbol x
        '''
        return _goto_lr0(items,x,g)
    
    @staticmethod
    def goto_lalr(items:Set[LALRItem],x:Symbol,g:Grammar) -> Set[LALRItem]:
        '''
        Args:
            items (Set[LALRItem])
            x (Symbol)
            g (Grammar)
        
        Returns:
            Set[LALRItem]: The next state for the given state and the symbol x
        '''
        return _goto_lalr(items,x,g)
    
    @staticmethod
    def get_canonical_lr0_states(g:Grammar) -> Set[LR0State]:
        '''
        Args:
            g (Grammar)
        
        Returns:
            Set[LR0State]: the set of lr0 states canonical
        '''
        return _get_canonical_lr0_states(g)
    
    @staticmethod
    def get_kernel_items_lr0(state:LR0State, g:Grammar) -> Set[LR0Item]:
        '''
        Args:
            state (LR0State)
            start (Symbol): start symbol of the grammar
                this is to accept the item S' -> . S
        
        Returns:
            Set[LR0Item]: the items kernel of the given state
        '''
        return _get_kernel_items_lr0(state,g)
    
    @staticmethod
    def get_kernel_items_lalr(state:LALRState, g:Grammar) -> Set[LALRItem]:
        '''
        Args:
            state (LALRState)
            start (Symbol): start symbol of the grammar
                this is to accept the item S' -> . S
        
        Returns:
            Set[LALRItem]: the items kernel of the given state
        '''
        return _get_kernel_items_lalr(state,g)
    
    @staticmethod
    def build_lookaheads_propagation_edges(initial_item:LALRItem,g:Grammar) -> Tuple[dict[tuple[Symbol,tuple,tuple],dict[Symbol,tuple[Symbol,tuple,tuple]]],set[LALRItem]]:
        '''
        Args:
            initial_item (LALRItem): initial item to start the building
            g (Grammar)
        
        Raises:
            ValueError('head must be a non-terminal')
            ValueError('head of initial item can not be in g.non_terminals')
        
        Returns:
            Table: the propagation's edges
        '''
        return _build_lookaheads_propagation_edges(initial_item,g)
    
    @staticmethod
    def get_canonical_lalr_states(g:Grammar) -> set[LALRState]:
        '''
        Args:
            g (Grammar)
        
        Returns:
            Set[LALRState]: the set of lr0 states canonical
        '''
        return _get_canonical_lalr_states(g)

cdef set[LR0Item] _clousure_lr0(set[LR0Item] items,Grammar g):
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
        return _clousures[key] # type:ignore
    
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

cdef set[LALRItem] _clousure_lalr(set[LALRItem] items,Grammar g):
    cdef LALRItem item,new_item
    cdef Production production
    cdef Symbol head,lookahead_symbol,new_lookahead
    cdef set[LALRItem] result = items.copy()
    cdef set[LALRItem] copy
    cdef bint change = True # type:ignore
    cdef bint exists = False # type:ignore
    cdef str set_id
    cdef list[str] ids = []
    cdef tuple[str,str] key
    cdef tuple[Symbol,tuple,tuple] kernel
    cdef dict[tuple[Symbol,tuple,tuple],LALRItem] item_by_kernel = {}
    cdef set[Symbol] first

    for item in items:
        kernel = (item._head,tuple(item._left),tuple(item._right))
        item_by_kernel[kernel] = item
        ids.append(str(item))
    ids.sort()

    set_id = sha256('-'.join(ids).encode()).hexdigest()
    key = (g._id(),set_id)
    # checks for a precomputed value
    if key in _clousures:
        return _clousures[key] # type:ignore
    
    while change:
        change = False # type:ignore

        copy = result.copy()

        for item in copy:
            if len(item._right) > 0:
                # I = [A -> α . B β] { a }
                head = item._right[0]
                if not head._is_terminal:
                    for production in g._productions_by_symbol[head]:
                        new_item = LALRItem(head,[],production._production) # type:ignore
                        kernel = (new_item._head,tuple(new_item._left),tuple(new_item._right))
                        exists = kernel in item_by_kernel # type:ignore
                        new_item = item_by_kernel.get(kernel,new_item)
                        # [B -> . γ ] b ∈ first(β a)
                        for lookahead_symbol in item._lookaheads:
                            first = g.first(item._right[1:] + [lookahead_symbol])
                            for new_lookahead in first:
                                if not new_lookahead in new_item._lookaheads:
                                    new_item._lookaheads.add(new_lookahead)
                                    change = True # type:ignore
                        if not exists:
                            result.add(new_item)
                        item_by_kernel[kernel] = new_item
    _clousures[key] = result
    return result

cdef set[LR0Item] _goto_lr0(set[LR0Item] items,Symbol x,Grammar g):
    cdef Symbol head
    cdef LR0Item item,new_item
    cdef set[LR0Item] result = set()

    for item in items:
        if len(item._right) > 0 and item._right[0] == x:
            new_item = LR0Item(item._head,item._left + [x],item._right[1:]) # type:ignore
            result.update(_clousure_lr0({new_item},g))
    
    return result

cdef set[LALRItem] _goto_lalr(set[LALRItem] items,Symbol x,Grammar g):
    cdef Symbol head
    cdef LALRItem item,new_item
    cdef set[LALRItem] result = set()

    for item in items:
        if len(item._right) > 0 and item._right[0] == x:
            new_item = LALRItem(item._head,item._left + [x],item._right[1:],item._lookaheads.copy()) # type:ignore
            result.update(_clousure_lalr({new_item},g))

    return result

cdef set[LR0State] _get_canonical_lr0_states(Grammar g):
    cdef Grammar augmented = _augment_grammar(g)
    cdef LR0Item start = LR0Item(augmented._start_symbol,[],[g._start_symbol]) # type:ignore
    cdef LR0State state,new_state
    cdef set[LR0State] result = { LR0State(_clousure_lr0({start},augmented)) } # type:ignore
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
                items = _goto_lr0(state._items,symbol,g)
                if len(items) > 0:
                    new_state = LR0State(items,len(result)) # type:ignore
                    if not new_state in result:
                        change = True # type:ignore
                        result.add(new_state)
    
    return result

cdef set[LR0Item] _get_kernel_items_lr0(LR0State state,Grammar g):
    cdef LR0Item item
    cdef set[LR0Item] result = set()

    for item in state._items:
        if not item._head in g._non_terminals and len(item._left) == 0:
            result.add(item)
        if len(item._left) > 0:
            result.add(item)
    
    return result

cdef set[LALRItem] _get_kernel_items_lalr(LALRState state,Grammar g):
    cdef LALRItem item
    cdef set[LALRItem] result = set()

    for item in state._items:
        if not item._head in g._non_terminals and len(item._left) == 0:
            result.add(item)
        if len(item._left) > 0:
            result.add(item)
    
    return result

cdef tuple[dict[tuple[Symbol,tuple,tuple],dict[Symbol,tuple[Symbol,tuple,tuple]]],set[LALRItem]] _build_lookaheads_propagation_edges(LALRItem initial_item,Grammar g):
    cdef dict[tuple[Symbol,tuple,tuple],dict[Symbol,tuple[Symbol,tuple,tuple]]] result = {}
    cdef set[LALRItem] kernel_items = set()
    cdef set[LALRItem] kernel_items_copy
    cdef LALRItem item,origin,destination
    cdef bint change = True # type:ignore
    cdef tuple[Symbol,tuple,tuple] origin_key,destination_key

    if initial_item._head._is_terminal:
        raise ValueError('head must be a non-terminal')
    
    if initial_item._head in g._non_terminals:
        raise ValueError('head of initial item can not be in g.non_terminals')

    if len(initial_item._left) > 0:
        raise ValueError('initial item is expected to be S\' -> ◦ S, where S\' is the new start symbol for the grammar augmented')

    kernel_items.add(initial_item)

    for item in _clousure_lalr({initial_item},g):
        if len(item._left) > 0:
            kernel_items.add(item)
    
    while change:
        change = False # type:ignore
        kernel_items_copy = kernel_items.copy()

        for item in kernel_items_copy:
            # for each kernel item
            for origin in _clousure_lalr({item},g):
                if len(origin._right) > 0:
                    # gets the clousure and if it can propagate lookaheads
                    origin_key = (origin._head,tuple(origin._left),tuple(origin._right))
                    destination = LALRItem(origin._head,origin._left + [origin._right[0]],origin._right[1:]) # type:ignore
                    destination_key = (destination._head,tuple(destination._left),tuple(destination._right))
                    # if kernel item not in kernel_items
                    if not destination in kernel_items:
                        kernel_items.add(destination)
                        change = True # type:ignore
                    # if there is a new propagation edge
                    if not origin_key in result:
                        result[origin_key] = {}
                    if not origin._right[0] in result[origin_key]:
                        result[origin_key][origin._right[0]] = destination_key
                        change = True # type:ignore
    
    return result,kernel_items

cdef set[LALRState] _get_canonical_lalr_states(Grammar g):
    cdef Grammar augmented = _augment_grammar(g)
    cdef LALRItem initial_item = LALRItem(augmented._start_symbol,[],[g._start_symbol],{g._end_symbol}) # type:ignore
    cdef dict[tuple[Symbol,tuple,tuple],dict[Symbol,tuple[Symbol,tuple,tuple]]] propagation_edges
    cdef set[LALRItem] kernel_items
    cdef bint change = True # type:ignore
    cdef set[LALRState] result = set()
    cdef set[LALRState] copy
    cdef LALRState state,new_state
    cdef dict[tuple[Symbol,tuple,tuple],set[Symbol]] lookaheads = {}
    cdef set[Symbol] origin_lookahead,destination_lookahead
    cdef tuple[Symbol,tuple,tuple] origin_key,destination_key
    cdef LALRItem item
    cdef set[LALRItem] items
    cdef Symbol lookahead,symbol

    # gets the propagation edges and the kernel items
    propagation_edges,kernel_items = _build_lookaheads_propagation_edges(initial_item,g)

    # initialize lookaheads
    for item in kernel_items:
        origin_key = (item._head,tuple(item._left),tuple(item._right))
        lookaheads[origin_key] = set()

    # first state for initialize lookaheads sets
    state = LALRState(_clousure_lalr({initial_item},g)) # type:ignore

    # updates initial lookaheads
    for item in state._items:
        origin_key = (item._head,tuple(item._left),tuple(item._right))
        lookaheads[origin_key] = item._lookaheads

    # iterate until fixed point is reached
    while change:
        change = False # type:ignore

        # generate espontaneous lookaheads
        for item in kernel_items:
            origin_key = (item._head,tuple(item._left),tuple(item._right))
            item._lookaheads = lookaheads[origin_key]
            items = _clousure_lalr({item},g)
            for item in items:
                if origin_key in propagation_edges:
                    lookaheads[origin_key] = item._lookaheads
        
        # for each propagation edge
        for origin_key in propagation_edges:
            if not origin_key in lookaheads:
                lookaheads[origin_key] = set()
            origin_lookahead = lookaheads[origin_key]
            if len(origin_lookahead) == 0:
                continue
            # propagate lookaheads
            for destination_key in propagation_edges[origin_key].values():
                if not destination_key in lookaheads:
                    lookaheads[destination_key] = set()
                destination_lookahead = lookaheads[destination_key]
                for lookahead in origin_lookahead:
                    if not lookahead in destination_lookahead:
                        change = True # type:ignore
                        destination_lookahead.add(lookahead)
                lookaheads[destination_key] = destination_lookahead

    change = True # type:ignore
    # adds initial state
    origin_key = (initial_item._head,tuple(initial_item._left),tuple(initial_item._right))
    initial_item._lookaheads = lookaheads[origin_key]
    state = LALRState(_clousure_lalr({initial_item},g)) # type:ignore
    result.add(state)
    
    # build states
    while change:
        change = False # type:ignore
        copy = result.copy()
        for state in copy:
            for symbol in g._symbols:
                if symbol == g._end_symbol: continue
                items = _goto_lalr(state._items,symbol,g)
                if len(items) == 0: continue
                for item in items:
                    # sets the lookaheads
                    origin_key = (item._head,tuple(item._left),tuple(item._right))
                    item._lookaheads = lookaheads[origin_key]
                new_state = LALRState(items,len(result)) # type:ignore
                # adds the new state
                if not new_state in result:
                    change = True # type:ignore
                    result.add(new_state)

    return result