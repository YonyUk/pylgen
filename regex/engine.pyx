from automaton.automaton cimport NFA,DFA,State,_automaton_reverse
from grammar.grammar cimport Grammar,_reverse_grammar,_is_left_regular,_is_right_regular,ProductionsSet
from common.types cimport Symbol

cdef class RegexEngine:
    
    @staticmethod
    def get_automaton(g:Grammar) -> DFA:
        '''
        Args:
            g (Grammar)
        
        Returns:
            DFA: the automaton that accepts L(g)
        
        Raises:
            ValueError('g must be a regular grammar')
        '''
        return _get_automaton(g)

cdef DFA _get_automaton(Grammar g):
    cdef NFA result
    cdef State state,final_state,from_state,to_state
    cdef set[State] states = set()
    cdef Symbol nt
    cdef set[str] alphabet = set()
    cdef dict[Symbol,State] state_by_symbol = {}
    cdef ProductionsSet productions
    cdef list[Symbol] production

    if not (_is_right_regular(g) or _is_left_regular(g)):
        raise ValueError('g must be a regular grammar')
    
    if _is_left_regular(g):
        return _automaton_reverse(_get_automaton(_reverse_grammar(g))).to_deterministic().minimize()

    # creates the final state
    final_state = State('final','final',True) # type:ignore

    # maps the non-terminals to states
    for nt in g._non_terminals:
        state = State(nt._symbol,nt._symbol) # type:ignore
        states.add(state)
        state_by_symbol[nt] = state
    
    # builds the alphabet
    for nt in g._terminals:
        if nt == g._end_symbol or nt._is_epsilon: continue
        alphabet.add(nt._symbol)

    # adds the final state
    states.add(final_state)

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
                if (<Symbol>production[0])._is_terminal:
                    to_state = state_by_symbol[production[1]]
                    result.add_transition(from_state,to_state,(<Symbol>production[0])._symbol)
            # A -> B
            elif not (<Symbol>production[0])._is_terminal:
                to_state = state_by_symbol[production[0]]
                result.add_epsilon_transition(from_state,to_state)
            # A -> b
            elif not (<Symbol>production[0])._is_epsilon:
                result.add_transition(from_state,final_state,(<Symbol>production[0])._symbol)
            # A -> ε
            else:
                result.add_epsilon_transition(from_state,final_state)
    
    return result.to_deterministic().minimize()