# cython: language_level=3

from hashlib import sha256
from typing import Set,Dict,Tuple

from common.table cimport Table

cdef class State:
    '''
    State class for building automatons. This class is inmutable
    '''
    def __init__(self,str id,object value,bint is_accept=False): # type:ignore
        '''
        Args:
            id (str): id which identify to this state
            Two states with the same id are considered equals
        
            value (Any): the value contained inside this state

            is_accept (bool): tells if this state is an accepting state
        '''
        self._id = id
        self._value = value
        self._is_accept = is_accept
    
    @property
    def id(self) -> str:
        '''
        Returns:
            str: the id of this state
        '''
        return self._id
    
    @property
    def value(self) -> object:
        '''
        Returns:
            Any: the value contained inside this state
        '''
        return self._value
    
    @property
    def is_accept(self) -> bool:
        '''
        Returns:
            bool: if this state is accepting or not
        '''
        return self._is_accept # type:ignore
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o,State): return False
        return __o.id == self._id
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self._id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        return h # type:ignore

cdef class Automaton:
    '''
    Base class for automaton definition
    '''
    
    def __init__(self):
        raise ValueError("Can not instance this class")
    
    @property
    def alphabet(self) -> Set[str]:
        '''
        Returns:
            Set[str]: a copy of the alphabet of this automaton
        '''
        return set(self._alphabet)
    
    @property
    def start_state(self) -> State:
        '''
        Returns:
            State: A copy of the start state of this automaton
        '''
        cdef State result = State(self._start_state._id,self._start_state._value,self._start_state._is_accept)
        if isinstance(result._value,set):
            result._value = set(result._value)
        return result
    
    @property
    def current_state(self) -> State:
        '''
        Returns:
            State: A copy of the current state of the automaton
        '''
        cdef State result = State(self._current_state._id,self._current_state._value,self._current_state._is_accept)
        if isinstance(result._value,set):
            result._value = set(result._value)
        return result
    
    @property
    def states(self) -> Set[State]:
        '''
        Returns:
            Set[State]: A copy of the states of this automaton
        '''
        cdef State state,copy_state
        cdef set result = set()
        for state in self._states_by_id.values():
            copy_state = State(state._id,state._value,state._is_accept)
            if isinstance(copy_state._value,set):
                copy_state._value = set(copy_state._value)
            result.add(copy_state)
        return result
    
    @property
    def finals(self) -> Set[State]:
        '''
        Returns:
            Set[State]: A copy of the finals states of this automaton
        '''
        cdef State state
        cdef set result = set()
        for state in self.states:
            if state._is_accept:
                result.add(state)
        return result
    
    @property
    def is_complete(self) -> bool:
        return self._is_complete # type:ignore
    
    @property
    def transition_function(self) -> Dict[Tuple[str,str],str]:
        '''
        Returns:
            Dict[Tuple[str,str],str]: A dictionary representing the transition function of this automaton
        '''
        return self._trans_func.to_dict()
    
    cpdef void add_transition(self,State from_state,State to_state,str symbol):
        '''
        Args:
            from_state (State): Origin state
            to_state (State): destination state
            symbol (str): symbol that raise this transition
        
        Returns:
            None: adds a new transition to this automaton
        '''
        cdef str f_id = from_state._id
        cdef str t_id = to_state._id
        cdef object f_value = from_state._value
        cdef object t_value = to_state._value
        cdef bint f_accept = from_state._is_accept
        cdef bint t_accept = to_state._is_accept

        cdef tuple[str,str] key = (f_id,symbol)

        if not symbol in self._alphabet:
            raise ValueError(f'Symbol {symbol} must be in the alphabet')
        if not f_id in self._states_by_id:
            self._states_by_id[f_id] = State(f_id,f_value,f_accept)
            if isinstance(f_value,set):
                self._states_by_id[f_id]._value = set(f_value)
        if not t_id in self._states_by_id:
            self._states_by_id[t_id] = State(t_id,t_value,t_accept)
            if isinstance(t_value,set):
                self._states_by_id[t_id]._value = set(t_value)
        self._trans_func._table[key] = t_id
        self._is_complete = len(self._trans_func._table) == len(self._states_by_id) * len(self._alphabet) # type:ignore
    
    cpdef bint has_transition(self,State state, str symbol):
        '''
        Args:
            state (State)
            symbol (str)

        Returns:
            bool: True if there is a transition for the givne tuple (state,symbol)
        '''
        cdef tuple[str,str] key = (state._id,symbol)
        return key in self._trans_func._table # type:ignore
    
    cpdef State next(self,State state,str symbol):
        '''
        Args:
            state (State)
            symbol (str)
        
        Returns:
            State: the destination state for this transition if exists
        
        Raises:
            KeyError: If there is no transition for the given pair (state,symbol)
        '''
        cdef tuple[str,str] key = (state._id,symbol)
        return self._states_by_id[self._trans_func._table[key]]
    
    cpdef void reset(self):
        '''
        Returns:
            None: Reset this automaton to its initial state
        '''
        self._current_state = self._start_state
        self._is_stuck = False # type:ignore
    
    cpdef set[State] clousure(self,State state):
        '''
        Args:
            state (State):
        
        Returns:
            Set[State]: the clousure-set of the given state
        '''
        cdef str state_id = state._id
        cdef object state_value = state._value
        cdef set[State] result
        cdef State current_state,loop_state,inner_loop_state
        cdef set[State] current_clousure,loop_state_clousure
        cdef int last_state_idx
        cdef int idx = 0
        cdef tuple[State,set[State],int,list[State]] stack_head
        cdef list[State] states_to_check = []
        cdef list[State] new_states_to_check = []
        cdef str loop_state_id,inner_loop_state_id
        cdef list[tuple[State,set[State],int,list[State]]] stack = []
        cdef set[str] in_progress = set()
        cdef bint entered = False # type:ignore

        # if clousure is already computed for this state
        if state_id in self._clousures:
            return self._clousures[state_id]
        # if this state has not epsilon-transitions
        if state_id not in self._epsilons:
            # clousure is a set with only this state inside
            self._clousures[state_id] = { state }
            return self._clousures[state_id]

        # initialize clousure
        current_clousure = { state }
        # put in all states reachable from the given state with one epsilon-transition into
        # the clousure, put in this states into states_to_check
        for loop_state_id in self._epsilons[state_id]:
            current_clousure.add(self._states_by_id[loop_state_id])
            states_to_check.append(self._states_by_id[loop_state_id])
        
        stack_head = (state,current_clousure,idx,states_to_check)
        stack.append(stack_head)
        in_progress.add(state_id)

        # while there is clousures to compute
        while stack:
            entered = False # type:ignore
            # pop the current computing process
            stack_head = stack[-1]

            current_state = <State>stack_head[0]
            current_clousure = <set[State]>stack_head[1]
            last_state_idx = <int>stack_head[2]
            states_to_check = <list[State]>stack_head[3]

            # continues the process from the last iteration
            for idx in range(last_state_idx,len(states_to_check)):

                loop_state = <State>[states_to_check][idx]
                loop_state_id = loop_state._id

                # if this state clousure is already in progress, ignore it
                if loop_state_id in in_progress:
                    continue

                # if the current state has not clousure already computed
                if not loop_state_id in self._clousures:
                    new_states_to_check = []
                    # initialize its clousure
                    loop_state_clousure = { loop_state }
                    # if this state has epsilon-transitions
                    if loop_state_id in self._epsilons:
                        # adds all reachable states with an epsilon-transition to the clousure
                        # of the state and put it to new_states_to_check
                        for inner_loop_state_id in self._epsilons[loop_state_id]:
                            loop_state_clousure.add(self._states_by_id[inner_loop_state_id])
                            new_states_to_check.append(self._states_by_id[inner_loop_state_id])
                        
                        stack_head = (loop_state,loop_state_clousure,0,new_states_to_check)
                        stack.append(stack_head)
                        in_progress.add(loop_state_id)
                        entered = True # type:ignore
                        break
                    else:
                        self._clousures[loop_state_id] = loop_state_clousure
                # adds the states on the clousure of loop_state
                current_clousure.update(self._clousures[loop_state_id])
                # advance the idx counter in 1
                stack_head = (current_state,current_state,idx + 1,states_to_check)
            
            if not entered:
                self._clousures[current_state._id] = current_clousure
                stack.pop()
                in_progress.discard(current_state._id)
            
        return self._clousures[state_id]
    
    cpdef void make_complete(self):
        '''
        Returns:
            None: adds any missing transition if any
        '''
        cdef State state,state_fault
        cdef str symbol,state_id
        cdef tuple[str,str] transition
        cdef list[str] states_ids = [state._id for state in self._states_by_id.values()]

        if not self._is_complete:
            states_ids.sort()
            state_fault = State(sha256(''.join(states_ids).encode()).hexdigest(),'FAULT')
            self._states_by_id[state_fault._id] = state_fault
            self._fault_id = state_fault._id
            for state in self._states_by_id.values():
                state_id = state._id
                for symbol in self._alphabet:
                    transition = (state_id,symbol)
                    if not transition in self._trans_func._table:
                        self._transitions_added_while_completing.append(transition)
                        self._trans_func._table[transition] = state_fault._id
            self._is_complete = True # type:ignore
    
    cpdef void restore_to_before_complete(self):
        '''
        Returns:
            None: restore this automaton to before it was completed
        '''
        cdef tuple[str,str] transition

        if self._transitions_added_while_completing:
            del self._states_by_id[self._fault_id]
            for transition in self._transitions_added_while_completing:
                del self._trans_func._table[transition]
            self._is_complete = False # type:ignore

cdef class DFA(Automaton):

    def __init__(
        self,
        str start_id,
        object start_value,
        set[str] alphabet,
        bint start_accept=False # type:ignore
    ):
        '''
        Args:
            start_id (str): id of the start state
            start_value (object): value of the start_state
            alphabet (Set[str]): alphabet of this automaton
            start_accept (bool): says if the start state is an accepting state
        '''
        if isinstance(start_value,set):
            self._start_state = State(start_id,set(start_value),start_accept)
        else:
            self._start_state = State(start_id,start_value,start_accept)
        self._alphabet = set(alphabet)
        self._current_state = self._start_state
        self._states_by_id = { start_id:self._start_state }
        self._clousures = {}
        self._epsilons = {}
        self._is_complete = False # type:ignore
        self._is_stuck = False # type:ignore
        self._trans_func = Table()
        self._transitions_added_while_completing = []
        self._fault_id = ''
    
    cpdef void walk(self,str symbol):
        '''
        Args:
            symbol (str):
        
        Returns:
            None: move forward with the given symbol if its possible
        '''
        cdef tuple[str,str] transition = (self._current_state._id,symbol)
        
        if not self._is_stuck:
            if transition in self._trans_func._table:
                self._current_state = self._states_by_id[self._trans_func._table[transition]]
            else:
                self._is_stuck = True # type:ignore
    
    cpdef bint accept(self,list[str] string):
        '''
        Args:
            string (List[str])
        
        Returns:
            bool: says when this automaton ends on an accepting state after read all the given string
        '''
        cdef str symbol
        for symbol in string:
            self.walk(symbol)
            if self._is_stuck:
                return False # type:ignore
        return self._current_state._is_accept
    
    def __iadd__(self,tuple[State,str,State] transition) -> DFA:
        '''
        Description:
            '+=' operator overwrite, equivalent to self.add_transition
        
        Args:
            transition (Tuple[State,str,State]): corresponds to (from_state,symbol,to_state)
        
        Returns:
            DFA: the same automaton with the transition added
        '''
        cdef State from_state = <State>transition[0]
        cdef State to_state = <State>transition[2]
        cdef str symbol = <str>transition[1]

        self.add_transition(from_state,to_state,symbol)
        return self

cdef class NFA(Automaton):

    def __init__(
        self,
        str start_id,
        object start_value,
        set[str] alphabet,
        bint start_accept=False # type:ignore
    ):
        '''
        Args:
            start_id (str): id of the start state
            start_value (object): value of the start_state
            alphabet (Set[str]): alphabet of this automaton
            start_accept (bool): says if the start state is an accepting state
        '''
        if isinstance(start_value,set):
            self._start_state = State(start_id,set(start_value),start_accept)
        else:
            self._start_state = State(start_id,start_value,start_accept)
        self._alphabet = set(alphabet)
        self._current_state = self._start_state
        self._states_by_id = { start_id:self._start_state }
        self._clousures = {}
        self._epsilons = {}
        self._is_complete = False # type:ignore
        self._is_stuck = False # type:ignore
        self._trans_func = Table()
        self._transitions_added_while_completing = []
        self._fault_id = ''
    
    cpdef void add_epsilon_transition(self,State from_state,State to_state):
        '''
        Args:
            from_state (State): origin state
            to_state (State): destination state
        
        Returns:
            None: adds an epsilon-transition from from_state to to_state
        '''
        cdef str f_id = from_state._id
        cdef str t_id = to_state._id
        cdef object f_value = from_state._value
        cdef object t_value = to_state._value
        cdef bint f_accept = from_state._is_accept
        cdef bint t_accept = to_state._is_accept

        if not f_id in self._states_by_id:
            self._states_by_id[f_id] = State(f_id,f_value,f_accept)
            if isinstance(f_value,set):
                self._states_by_id[f_id]._value = set(f_value)
        if not t_id in self._states_by_id:
            self._states_by_id[t_id] = State(t_id,t_value,t_accept)
            if isinstance(t_value,set):
                self._states_by_id[t_id]._value = set(t_value)

        if not f_id in self._epsilons:
            self._epsilons[f_id] = set()
        self._epsilons[f_id] = t_id
    
    cpdef DFA to_deterministic(self):
        '''
        Returns:
            DFA: the equivalent dfa to this one
        '''
        raise NotImplementedError()