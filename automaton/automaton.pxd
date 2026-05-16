from common.table cimport Table

cdef class State:
    cdef bint _is_accept
    cdef object _value
    cdef str _id

cdef class Automaton:
    cdef dict[str,State] _states_by_id
    cdef set[str] _alphabet
    cdef State _start_state,_current_state
    cdef Table _trans_func
    cdef dict[str,set[str]] _epsilons
    cdef dict[str,set[State]] _clousures
    cdef list[tuple[str,str]] _transitions_added_while_completing
    cdef bint _is_complete,_is_stuck
    cdef str _fault_id
    cdef dict[tuple[str,str],set[State]] _preimages

    cpdef void add_transition(self,State from_state,State to_state,str symbol)
    cpdef bint has_transition(self,State state,str symbol)
    cpdef State next(self,State state,str symbol)
    cpdef void reset(self)
    cpdef set[State] clousure(self,State state)
    cpdef void make_complete(self)
    cpdef void restore_to_before_complete(self)

cdef class DFA(Automaton):
    cdef set[State] _state_preimage_for_symbol(self,State state,str symbol)
    cdef set[State] _block_preimage_for_symbol(self,set[State] states,str symbol)
    cdef Table _build_new_transition_function(self,dict[str,str] old_ids_to_new_ids_map)
    cdef DFA _build_new_dfa(self,list[set[State]] partition)

    cpdef bint accept(self,list[str] string)
    cpdef void walk(self,str symbol)
    cpdef DFA minimize(self)

cdef class NFA(Automaton):
    cdef State _build_state(self,set[State] states)
    cdef State _build_new_state(self,State state,Table target_table,set[State] current_states)

    cpdef void add_epsilon_transition(self,State from_state,State to_state)
    cpdef DFA to_deterministic(self)

cdef DFA _copy_dfa(DFA dfa)
cdef NFA _copy_nfa(NFA nfa)
cdef NFA _automaton_union(set[Automaton] automatons)
cdef DFA _dfa_complement(DFA automaton)
cdef DFA _nfa_complement(NFA automaton)
cdef DFA _automaton_complement(Automaton automaton)
cdef DFA _automaton_intersection(set[Automaton] automatons)
cdef NFA _automaton_concatenation(Automaton first,Automaton second)
cdef NFA _automaton_clousure(Automaton automaton,bint positive)

cpdef DFA create_dfa(set[State] states,Table transition_function,str start_id,set[str] alphabet)