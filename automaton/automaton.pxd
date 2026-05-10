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

    cpdef void add_transition(self,State from_state,State to_state,str symbol)
    cpdef bint has_transition(self,State state,str symbol)
    cpdef State next(self,State state,str symbol)
    cpdef void reset(self)
    cpdef set[State] clousure(self,State state)
    cpdef void make_complete(self)
    cpdef void restore_to_before_complete(self)

cdef class DFA(Automaton):
    cpdef bint accept(self,list[str] string)
    cpdef void walk(self,str symbol)

cdef class NFA(Automaton):
    cpdef void add_epsilon_transition(self,State from_state,State to_state)
    cpdef DFA to_deterministic(self)