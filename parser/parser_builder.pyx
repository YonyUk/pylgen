from typing import Set,Tuple,Dict
from hashlib import sha256

from common.types cimport Symbol
from grammar.grammar cimport Grammar,Production,_augment_grammar
from .parser cimport Parser,BottomUpParser
from .parser_type import ParserType
from .lr0_parser cimport LR0Item,LR0State
from .lalr_parser cimport LALRState
from .bottom_up_parser_actions import BottomUpParserAction

_clousures:dict[tuple[str,str],set[LR0Item]] = {}
_clousures_lalr:dict[tuple[str,str],set[LALRItem]] = {}

cdef class ParserBuildingConflictException(Exception):
    pass

cdef class LALRParserBuildingConflictException(ParserBuildingConflictException):

    def __init__(self,state:LALRState,symbol:Symbol):
        self._state = state
        self._symbol = symbol
    
    @property
    def state(self) -> LALRState:
        return self._state
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol

cdef class LALRShiftReduceConflictException(LALRParserBuildingConflictException):
    
    def __init__(self, state: LALRState, symbol: Symbol,next_state:LALRState,production:Production):
        super().__init__(state, symbol)
        self._next = next_state
        self._production = production
    
    @property
    def next_state(self) -> LALRState:
        return self._next
    
    @property
    def production(self) -> Production:
        return self._production

cdef class LALRReduceReduceConflictException(LALRParserBuildingConflictException):

    def __init__(self, state: LALRState, symbol: Symbol,old:Production,new_:Production):
        super().__init__(state, symbol)
        self._new = new_
        self._old = old
    
    @property
    def old(self) -> Production:
        return self._old
    
    @property
    def new_(self) -> Production:
        return self._new

cdef class ParserBuilder:

    @staticmethod
    def clear_cache() -> None:
        _clousures.clear()
        _clousures_lalr.clear()

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
    def build_lookaheads_propagation_edges(g:Grammar) -> Tuple[Dict[LR0State,Dict[Tuple[LR0Item,Symbol],Tuple[LR0State,LR0Item]]],Set[LR0State]]:
        '''
        Args:
            g (Grammar)

        Returns:
            Tuple[Dict[LR0State,Dict[Tuple[LR0Item,Symbol],Tuple[LR0State,set[LR0Item]]]],Set[LR0State]]: the propagation edges and the lr0 states
        '''
        return _build_lookaheads_propagation_edges(g)
    
    @staticmethod
    def get_canonical_lalr_states(g:Grammar) -> Set[LALRState]:
        '''
        Args:
            g (Grammar)
        
        Returns:
            Set[LALRState]: canonical states for LALR(1) parser
        '''
        return _get_canonical_lalr_states(g)
    
    @staticmethod
    def get_goto_action_tables_lalr(g:Grammar) -> Tuple[Dict[Tuple[LALRState,Symbol],LALRState],dict[Tuple[LALRState,Symbol],Tuple[str,LALRState | Production]]]:
        '''
        Args:
            g (Grammar)
        
        Returns:
            Tuple[Dict[Tuple[LALRState,Symbol],LALRState],dict[Tuple[LALRState,Symbol],Tuple[str,LALRState | Production]]]:
                The ACTION and GOTO tables for a LALR(1) parser from the given grammar in a tuple (GOTO,ACTION)
        '''
        return _get_goto_action_tables_lalr(g)
    
    @staticmethod
    def build_parser(g:Grammar,type_:ParserType) -> Parser:
        '''
        Args:
            g (Grammar)
            type_ (ParserType)
        
        Returns:
            Parser: a parser builded for the given grammar
        '''
        if type_ == ParserType.LALR1:
            return _build_lalr_parser(g)
        raise NotImplementedError()
    
    @staticmethod
    def build_parser_from_attributed(g:AttributedGrammar,type_:ParserType) -> Parser:
        '''
        Args:
            g (AttributedGrammar)
            type_ (ParserType)
        
        Returns:
            Parser: a parser builded for the given attributed grammar
        '''
        if type_ == ParserType.LALR1:
            return _build_lalr_parser_from_attributed(g)
        raise NotImplementedError()

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
    cdef set[Symbol] first,current_lookaheads

    for item in items:
        kernel = (item._head,tuple(item._left),tuple(item._right))
        item_by_kernel[kernel] = item
        ids.append(str(item))
    ids.sort()

    set_id = sha256('-'.join(ids).encode()).hexdigest()
    key = (g._id(),set_id)
    # checks for a precomputed value
    if key in _clousures_lalr:
        return _clousures_lalr[key] # type:ignore
    
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
                        current_lookaheads = new_item._lookaheads.copy()
                        for lookahead_symbol in item._lookaheads:
                            first = g.first(item._right[1:] + [lookahead_symbol])
                            for new_lookahead in first:
                                if not new_lookahead in current_lookaheads:
                                    current_lookaheads.add(new_lookahead)
                                    change = True # type:ignore
                        new_item._lookaheads = current_lookaheads
                        if not exists:
                            result.add(new_item)
                            change = True # type:ignore
                        item_by_kernel[kernel] = new_item
    _clousures_lalr[key] = result
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

cdef tuple[dict[LR0State,dict[tuple[LR0Item,Symbol],tuple[LR0State,LR0Item]]],set[LR0State]] _build_lookaheads_propagation_edges(Grammar g):
    cdef set[LR0State] states = _get_canonical_lr0_states(g)
    cdef dict[LR0State,dict[tuple[LR0Item,Symbol],tuple[LR0State,LR0Item]]] result = {}
    cdef dict[LR0State,dict[tuple[LR0Item,Symbol],tuple[LR0State,LR0Item]]] copy
    cdef LR0State state,next_state
    cdef LR0Item item,next_item
    cdef set[LR0Item] kernel_items
    cdef tuple[LR0Item,Symbol] edge
    cdef set[LR0Item] clousure

    for state in states:
        kernel_items = _get_kernel_items_lr0(state,g)
        result[LR0State(kernel_items,state._index)] = {} # type:ignore
    
    for state in result:
        clousure = _clousure_lr0(state._items,g)
        for item in clousure:
            if len(item._right) > 0:
                next_state = LR0State(_goto_lr0(clousure,item._right[0],g)) # type:ignore
                edge = (item,item._right[0])
                if not edge in result[state]:
                    result[state][edge] = (next_state,LR0Item(item._head,item._left + [item._right[0]],item._right[1:])) # type:ignore
    
    copy = result.copy()
    for state in copy:
        if not result[state]:
            del result[state]

    return result,states

cdef set[LALRState] _get_canonical_lalr_states(Grammar g):
    cdef set[LR0State] lr0_states
    cdef dict[LR0State,dict[tuple[LR0Item,Symbol],tuple[LR0State,LR0Item]]] propagation_edges
    cdef bint change = True # type:ignore
    cdef dict[tuple[LR0State,LR0Item],set[Symbol]] lookaheads = {}
    cdef LR0State lr0_state,lr0_state_to
    cdef LR0Item lr0_item,lr0_item_to
    cdef set[LR0Item] lr0_kernel_items
    cdef LALRState lalr_state
    cdef LALRItem lalr_item
    cdef set[LALRItem] lalr_items
    cdef set[Symbol] lookahead_set
    cdef tuple[LR0State,LR0Item] key,key_to
    cdef Symbol lookahead_symbol
    cdef set[LALRState] result = set()

    # make the propagation edges
    propagation_edges,lr0_states = _build_lookaheads_propagation_edges(g)

    # initialize lookaheads
    for lr0_state in lr0_states:

        # gets kernel items
        lr0_kernel_items = _get_kernel_items_lr0(lr0_state,g)
        if len(lr0_kernel_items) == 1:
            lr0_item = next(iter(lr0_kernel_items))
            # if is the initial item S' -> ∘ S
            # compute the lookaheads
            if lr0_item._head not in g._non_terminals and len(lr0_item._left) == 0:
                lalr_item = LALRItem(lr0_item._head,[],[g._start_symbol],{g._end_symbol}) # type:ignore
                lalr_state = LALRState(_clousure_lalr({lalr_item},g)) # type:ignore
            else:
                # lets the lookaheads empty
                lalr_item = LALRItem(lr0_item._head,lr0_item._left,lr0_item._right) # type:ignore
                lalr_state = LALRState(_clousure_lalr({lalr_item},g),lr0_state._index) # type:ignore
        else:
            lalr_items = set()
            for lr0_item in lr0_kernel_items:
                lalr_item = LALRItem(lr0_item._head,lr0_item._left,lr0_item._right) # type:ignore
                lalr_items.add(lalr_item)
            lalr_state = LALRState(_clousure_lalr(lalr_items,g),lr0_state._index) # type:ignore

        # sets the lookahead initial value
        for lalr_item in lalr_state._items:
            lr0_item = LR0Item(lalr_item._head,lalr_item._left,lalr_item._right) # type:ignore
            key = (lr0_state,lr0_item)
            lookaheads[key] = lalr_item._lookaheads
        
    # iterate until a fixed point is reached
    while change:
        change = False # type:ignore

        # generate espontaneous lookaheads
        for lr0_state in lr0_states:
            lr0_kernel_items = _get_kernel_items_lr0(lr0_state,g)
            lalr_items = set()
            # create the equivalent LALRState with the current lookahead set
            for lr0_item in lr0_kernel_items:
                key = (lr0_state,lr0_item)
                lookahead_set = lookaheads[key]
                lalr_item = LALRItem(lr0_item._head,lr0_item._left,lr0_item._right,lookahead_set) # type:ignore
                lalr_items.add(lalr_item)
            # make the state with the clousure, generating espontaneous lookaheads
            lalr_state = LALRState(_clousure_lalr(lalr_items,g),lr0_state._index) # type:ignore
            # update the lookaheads
            for lalr_item in lalr_state._items:
                lr0_item = LR0Item(lalr_item._head,lalr_item._left,lalr_item._right) # type:ignore
                key = (lr0_state,lr0_item)
                if not key in lookaheads:
                    lookaheads[key] = set()
                lookahead_set = lalr_item._lookaheads
                for lookahead_symbol in lookahead_set:
                    if not lookahead_symbol in lookaheads[key]:
                        change = True # type:ignore
                        lookaheads[key].add(lookahead_symbol)
        
        # propagate lookaheads
        for lr0_state in propagation_edges:
            for (lr0_item,_),(lr0_state_to,lr0_item_to) in propagation_edges[lr0_state].items(): # type:ignore
                # edge that propagate lookaheads
                lr0_state = LR0State(_clousure_lr0(lr0_state._items,g),lr0_state._index) # type:ignore
                key = (lr0_state,lr0_item)
                if len(lookaheads[key]) == 0: continue
                lr0_state_to = LR0State(_clousure_lr0(lr0_state_to._items,g),lr0_state_to._index) # type:ignore
                key_to = (lr0_state_to,lr0_item_to)
                for lookahead_symbol in lookaheads[key]:
                    if not lookahead_symbol in lookaheads[key_to]:
                        change = True # type:ignore
                        lookaheads[key_to].add(lookahead_symbol)

    # build lalr states
    for lr0_state in lr0_states:
        lalr_items = set()
        for lr0_item in lr0_state._items:
            key = (lr0_state,lr0_item)
            lookahead_set = lookaheads[key]
            lalr_item = LALRItem(lr0_item._head,lr0_item._left,lr0_item._right,lookahead_set) # type:ignore
            lalr_items.add(lalr_item)
        lalr_state = LALRState(lalr_items,lr0_state._index) # type:ignore
        result.add(lalr_state)
    
    return result

cdef tuple[dict[tuple[LALRState,Symbol],LALRState],dict[tuple[LALRState,Symbol],tuple]] _get_goto_action_tables_lalr(Grammar g):
    cdef dict[tuple[LALRState,Symbol],LALRState] goto = {}
    cdef dict[tuple[LALRState,Symbol],tuple] action = {}
    cdef set[LALRState] states = _get_canonical_lalr_states(g)
    cdef dict[LR0State,LALRState] states_by_kernel = {}
    cdef dict[tuple[LALRState,LR0Item],set[Symbol]] lookaheads_by_kernel_item = {}
    cdef tuple[LALRState,LR0Item] lookahead_key
    cdef dict[LR0Item,Production] productions_by_kernel_item = {}
    cdef LR0Item lr0_item
    cdef LALRItem lalr_item
    cdef set[LR0Item] lr0_kernel
    cdef LALRState lalr_state
    cdef LR0State lr0_state,next_state
    cdef Symbol symbol
    cdef tuple[LALRState,Symbol] key
    cdef tuple action_value
    cdef str action_type
    cdef Production reduction

    # build mapping of lalr states by kernel
    for lalr_state in states:
        lr0_kernel = set()
        for lalr_item in lalr_state._items:
            lr0_item = LR0Item(lalr_item._head,lalr_item._left,lalr_item._right) # type:ignore
            lr0_kernel.add(lr0_item)
            lookahead_key = (lalr_state,lr0_item)
            lookaheads_by_kernel_item[lookahead_key] = lalr_item._lookaheads
            if len(lr0_item._right) == 0 and lr0_item._head in g._non_terminals:
                for reduction in g._productions_by_symbol[lalr_item._head]:
                    if reduction._head == lr0_item._head and reduction._production == lr0_item._left:
                        productions_by_kernel_item[lr0_item] = reduction
                        break
        states_by_kernel[LR0State(lr0_kernel,lalr_state._index)] = lalr_state # type:ignore
    
    for lr0_state in states_by_kernel:
        for lr0_item in lr0_state._items:
            if len(lr0_item._right) > 0:
                symbol = lr0_item._right[0]
                next_state = LR0State(_goto_lr0(lr0_state._items,symbol,g)) # type:ignore
                key = (states_by_kernel[lr0_state],symbol)
                goto[key] = states_by_kernel[next_state]
                action_value = (f'{BottomUpParserAction.SHIFT}',states_by_kernel[next_state])
                if symbol._is_terminal:
                    if key in action:
                        action_value = action[key]
                        action_type = action_value[0]
                        if action_type != f'{BottomUpParserAction.SHIFT}':
                            reduction = action_value[1]
                            raise LALRShiftReduceConflictException(key[0],symbol,states_by_kernel[next_state],reduction)
                action[key] = action_value
            else:
                lookahead_key = (states_by_kernel[lr0_state],lr0_item)
                for symbol in lookaheads_by_kernel_item[lookahead_key]:
                    key = (lookahead_key[0],symbol)
                    if symbol == g._end_symbol and lr0_item._head not in g._non_terminals:
                        action[key] = (f'{BottomUpParserAction.ACCEPT}',None)
                        continue
                    reduction = productions_by_kernel_item[lr0_item]
                    if key in action:
                        action_value = action[key]
                        action_type = action_value[0]
                        if action_type != f'{BottomUpParserAction.REDUCE}':
                            raise LALRShiftReduceConflictException(key[0],symbol,action_value[1],reduction)
                        if action_value[1] != reduction:
                            raise LALRReduceReduceConflictException(key[0],symbol,action_value[1],reduction)
                    else:
                        action_value = (f'{BottomUpParserAction.REDUCE}',reduction)
                        action[key] = action_value
    
    return goto,action

cdef dict[tuple[str,Symbol],str] _plain_goto_table_lalr(dict[tuple[LALRState,Symbol],LALRState] table):
    cdef dict[tuple[str,Symbol],str] result = {}
    cdef LALRState from_state,to_state
    cdef Symbol symbol
    cdef tuple[LALRState,Symbol] key
    cdef tuple[str,Symbol] new_key

    for key,to_state in table.items():
        from_state = <LALRState>key[0]
        symbol = <Symbol>key[1]
        new_key = (f'I{from_state._index}',symbol)
        result[new_key] = f'I{to_state._index}'

    return result

cdef dict[tuple[str,Symbol],tuple[str,object]] _plain_action_table_lalr(dict[tuple[LALRState,Symbol],tuple] table):
    cdef dict[tuple[str,Symbol],tuple[str,object]] result = {}
    cdef LALRState from_state,to_state
    cdef Symbol symbol
    cdef tuple[LALRState,Symbol] key
    cdef tuple value,new_value
    cdef tuple[str,Symbol] new_key
    cdef Production production

    for key,value in table.items():
        from_state = <LALRState>key[0]
        symbol = <Symbol>key[1]
        new_key = (f'I{from_state._index}',symbol)
        if value[0] == BottomUpParserAction.SHIFT:
            to_state = <LALRState>value[1]
            new_value = (value[0],f'I{to_state._index}')
        else:
            new_value = (value[0],value[1])
        result[new_key] = new_value
    
    return result

cdef BottomUpParser _build_lalr_parser(Grammar g):
    cdef dict[tuple[LALRState,Symbol],LALRState] goto_table
    cdef dict[tuple[LALRState,Symbol],tuple] action_table
    cdef dict[tuple[str,Symbol],str] plain_goto_table
    cdef dict[tuple[str,Symbol],tuple[str,object]] plain_action_table
    cdef dict[Symbol,set[Symbol]] follows
    cdef Symbol non_terminal
    cdef BottomUpParser result

    goto_table,action_table = _get_goto_action_tables_lalr(g)

    follows = {}
    for non_terminal in g._non_terminals:
        follows[non_terminal] = g.follow(non_terminal)

    plain_goto_table = _plain_goto_table_lalr(goto_table)
    plain_action_table = _plain_action_table_lalr(action_table)

    result = BottomUpParser('I0',plain_goto_table,plain_action_table,follows) # type:ignore
    return result

cdef BottomUpParser _build_lalr_parser_from_attributed(AttributedGrammar g):
    cdef Production production
    cdef set[Production] productions
    cdef BottomUpParser result = _build_lalr_parser(g)

    for productions in g._productions_by_symbol.values():
        for production in productions:
            result._set_reductor(production,g.get_reductor(production))
    
    return result