from automaton.automaton cimport NFA,DFA,State,Automaton
from grammar.grammar cimport Grammar,_is_left_regular,_is_right_regular,ProductionsSet
from common.types cimport Symbol

cdef class RegexEngine:
    
    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA:
        '''
        Args:
            g (Grammar)
        
        Returns:
            DFA: the automaton that accepts L(g)
        
        Raises:
            ValueError('g must be a regular grammar')
        '''
        return _get_automaton(g)
    
    @staticmethod
    def GetGrammar(automaton:Automaton) -> Grammar:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            Grammar: the equivalent grammar to the given automaton
        '''
        if isinstance(automaton,DFA):
            return _get_grammar_from_dfa(automaton)
        raise NotImplementedError()

cdef DFA _left_regular_automaton(Grammar g):
    cdef NFA result
    cdef State state,from_state,to_state,initial,old_to_state,temp_state
    cdef Symbol nt
    cdef set[str] alphabet = set()
    cdef dict[Symbol,State] state_by_symbol = {}
    cdef ProductionsSet productions
    cdef list[Symbol] production
    cdef dict[State,State] epsilon_transition = {}
    cdef tuple[str,str] transition

    # maps non-terminals to states
    for nt in g._non_terminals:
        state = State(nt._symbol,nt._symbol,nt == g._start_symbol) # type:ignore
        state_by_symbol[nt] = state
    
    # builds the alphabet
    for nt in g._terminals:
        if nt == g._end_symbol or nt._is_epsilon: continue
        alphabet.add(nt._symbol)
    
    # builds the automaton
    result = NFA('start','start',alphabet) # type:ignore
    initial = result._start_state

    # adds the transitions
    for nt,productions in g._productions.items():
        for production in productions._productions.values():
            to_state = state_by_symbol[nt]
            # A -> B b
            if len(production) == 2:
                from_state = state_by_symbol[production[0]]
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[1])._symbol):
                    # if is the first time we face to this for the state
                    if not from_state in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[1])._symbol)
                        old_to_state = result.next(from_state,transition[1])
                        # create an intermediate state
                        epsilon_transition[from_state] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[from_state]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[from_state]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,to_state,(<Symbol>production[1])._symbol)
            # A -> B
            elif not (<Symbol>production[0])._is_terminal:
                from_state = state_by_symbol[production[0]]
                result.add_epsilon_transition(from_state,to_state)
            # A -> b
            elif not (<Symbol>production[0])._is_epsilon:
                if result.has_transition(initial,(<Symbol>production[0])._symbol):
                    if not initial in epsilon_transition:
                        transition = (initial._id,(<Symbol>production[0])._symbol)
                        old_to_state = result.next(initial,transition[1])
                        epsilon_transition[initial] = State(f'{initial._id}-{transition[1]}',f'{initial._id}-{transition[1]}') # type:ignore
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[initial]
                        result.add_transition(initial,temp_state,transition[1])
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[initial]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(initial,to_state,(<Symbol>production[0])._symbol)
            # A -> ε
            else:
                result.add_epsilon_transition(initial,to_state)
    
    return result.to_deterministic().minimize()

cdef DFA _right_regular_automaton(Grammar g):
    cdef NFA result
    cdef State state,final_state,from_state,to_state,temp_state,old_to_state
    cdef Symbol nt
    cdef set[str] alphabet = set()
    cdef dict[Symbol,State] state_by_symbol = {}
    cdef ProductionsSet productions
    cdef list[Symbol] production
    cdef dict[Symbol,State] epsilon_transition = {}
    cdef tuple[str,str] transition

    # creates the final state
    final_state = State('final','final',True) # type:ignore

    # maps the non-terminals to states
    for nt in g._non_terminals:
        state = State(nt._symbol,nt._symbol) # type:ignore
        state_by_symbol[nt] = state
    
    # builds the alphabet
    for nt in g._terminals:
        if nt == g._end_symbol or nt._is_epsilon: continue
        alphabet.add(nt._symbol)

    # builds the NFA
    result = NFA(g._start_symbol._symbol,g._start_symbol._symbol,alphabet) # type:ignore
    # sets the start state
    result._start_state = state_by_symbol[g._start_symbol]
    # sets the current state
    result._current_state = result._start_state
    result._states_by_id[g._start_symbol._symbol] = result._start_state
    
    for nt,productions in g._productions.items():
        for production in productions._productions.values():
            from_state = state_by_symbol[nt]
            # A -> b B
            if len(production) == 2:
                to_state = state_by_symbol[production[1]]
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[0])._symbol):
                    # if is the first time we face to this for the state
                    if not nt in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[0])._symbol)
                        old_to_state = result.next(from_state,transition[1])
                        # create an intermediate state
                        epsilon_transition[nt] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[nt]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[nt]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,to_state,(<Symbol>production[0])._symbol)
            # A -> B
            elif not (<Symbol>production[0])._is_terminal:
                to_state = state_by_symbol[production[0]]
                result.add_epsilon_transition(from_state,to_state)
            # A -> b
            elif not (<Symbol>production[0])._is_epsilon:
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[0])._symbol):
                    # if is the first time we face to this for the state
                    if not nt in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[0])._symbol)
                        # create an intermediate state
                        epsilon_transition[nt] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[nt]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,final_state)
                    temp_state = epsilon_transition[nt]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,final_state,(<Symbol>production[0])._symbol)
            # A -> ε
            else:
                result.add_epsilon_transition(from_state,final_state)
    
    return result.to_deterministic().minimize()

cdef DFA _get_automaton(Grammar g):

    if not (_is_right_regular(g) or _is_left_regular(g)):
        raise ValueError('g must be a regular grammar')
    
    if _is_left_regular(g):
        return _left_regular_automaton(g)
    
    return _right_regular_automaton(g)

cdef Grammar _get_grammar_from_dfa(DFA dfa):
    cdef Grammar result
    cdef dict[str,Symbol] symbols = {}
    cdef State state
    cdef str symbol,f_id,t_id
    cdef tuple[str,str] transition
    cdef Symbol epsilon = Symbol('epsilon',True,True) # type:ignore
    cdef Symbol head,terminal,non_terminal

    for state in dfa._states_by_id.values():
        if state == dfa._start_state:
            f_id = 'S'
        else:
            f_id = f'A{len(symbols)}'
        symbols[state._id] = Symbol(f_id) # type:ignore

    for symbol in dfa._alphabet:
        symbols[symbol] = Symbol(symbol,True) # type:ignore
    
    result = Grammar(symbols[dfa._start_state._id]) # type:ignore
    
    for transition,t_id in dfa._trans_func._table.items():
        f_id = <str>transition[0]
        symbol = <str>transition[1]
        head = symbols[f_id]
        terminal = symbols[symbol]
        non_terminal = symbols[t_id]
        result._add_production(head,[terminal,non_terminal])
    
    for state in dfa._states_by_id.values():
        if state._is_accept:
            head = symbols[state._id]
            result._add_production(head,[epsilon])
    
    return result