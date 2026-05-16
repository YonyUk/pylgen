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
    def id(self) -> str:
        '''
        Returns:
            str: the id for this automaton
        '''
        cdef str result = ''
        cdef list[str] transitions_id = []
        cdef list[str] epsilons_transitions_id = []
        cdef list[str] states_id
        cdef tuple[str,str] transition
        cdef str state_id,to_id,epsilon_transition_id
        cdef set[str] epsilons
        cdef State state

        if self._trans_func._table:
            for transition,to_id in self._trans_func._table.items():
                transitions_id.append(f'({transition[0]},{transition[1]}) ---> {to_id}')
        if self._epsilons:
            for state_id,epsilons in self._epsilons.items():
                states_id = []
                for to_id in epsilons:
                    states_id.append(to_id)
                states_id.sort()
                epsilon_transition_id = f'{state_id} --e--> ' + '{' + ','.join(states_id) + '}'
                epsilons_transitions_id.append(epsilon_transition_id)
        states_id = []
        for state in self._states_by_id.values():
            states_id.append(f'{state._id} ACCEPTING: {state._is_accept}')
        states_id.sort()
        epsilons_transitions_id.sort()
        transitions_id.sort()
        result = sha256(f"START: {self._start_state._id} STATES: {'-'.join(states_id)} TRANSITIONS: {'-'.join(transitions_id)} EPSILONS: {'-'.join(epsilons_transitions_id)}".encode()).hexdigest()
        return result

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
    
    @staticmethod
    def Union(automatons:Set[Automaton]) -> NFA:
        '''
        Args:
            states (Set[State])
        
        Returns:
            NFA: returns the automaton equivalent to the union of each given automaton
        '''
        return _automaton_union(automatons)
    
    @staticmethod
    def Complement(automaton:Automaton) -> DFA:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            DFA: returns the complement automaton to the given automaton
        '''
        return _automaton_complement(automaton)
    
    @staticmethod
    def Intersection(automatons:Set[Automaton]) -> DFA:
        '''
        Args:
            automatons (Set[Automaton])
        
        Returns:
            DFA: the automaton equivalent to the intersection of all the given automatons
        '''
        return _automaton_intersection(automatons)
    
    @staticmethod
    def Concat(first:Automaton,second:Automaton) -> NFA:
        '''
        Args:
            first (Automaton)
            second (Automaton)
        
        Returns:
            NFA: the automaton equivalent to concat first followed by second automaton
        '''
        return _automaton_concatenation(first,second)
    
    @staticmethod
    def KleeneStar(automaton:Automaton) -> NFA:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            NFA: the automaton equivalent to L(automaton)* language
        '''
        return _automaton_clousure(automaton,0)
    
    @staticmethod
    def PositiveClousure(automaton:Automaton) -> NFA:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            NFA: the automaton equivalent to L(automaton)+ language
        '''
        return _automaton_clousure(automaton,1)
    
    @staticmethod
    def Optional(automaton:Automaton) -> NFA:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            NFA: the automaton equivalent to L(automaton)? language
        '''
        return _automaton_clousure(automaton,2)
    
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
        cdef State f_state,t_state

        cdef tuple[str,str] key = (f_id,symbol)

        if not symbol in self._alphabet:
            raise ValueError(f'Symbol {symbol} must be in the alphabet')
        if not f_id in self._states_by_id:
            f_state = State(f_id,f_value,f_accept)
            if isinstance(f_state._value,set):
                f_state._value = set(f_state._value)
            self._states_by_id[f_id] = f_state
        if not t_id in self._states_by_id:
            t_state = State(t_id,t_value,t_accept)
            self._states_by_id[t_id] = State(t_id,t_value,t_accept)
            if isinstance(t_state._value,set):
                t_state._value = set(t_state._value)
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
        cdef dict[str,set[str]] notify = {}

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

                loop_state = <State>states_to_check[idx]
                loop_state_id = loop_state._id

                # if this state clousure is already in progress, ignore it
                if loop_state_id in in_progress:
                    if not loop_state_id in notify:
                        notify[loop_state_id] = set()
                    notify[loop_state_id].add(current_state._id)
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
                        
                        # create the clousure computation instance
                        stack_head = (loop_state,loop_state_clousure,0,new_states_to_check)
                        # updates the top of the stack
                        stack[-1] = (current_state, current_clousure, idx, states_to_check)
                        # push the new instance
                        stack.append(stack_head)
                        in_progress.add(loop_state_id)
                        entered = True # type:ignore
                        break
                    else:
                        self._clousures[loop_state_id] = loop_state_clousure
                # adds the states on the clousure of loop_state
                current_clousure.update(self._clousures[loop_state_id])
                # advance the idx counter in 1
                stack_head = (current_state,current_clousure,idx + 1,states_to_check)
            
            if not entered:
                self._clousures[current_state._id] = current_clousure
                stack.pop()
                in_progress.discard(current_state._id)
                if current_state._id in notify:
                    for loop_state_id in notify[current_state._id]:
                        self._clousures[loop_state_id].update(current_clousure)
            
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
            self._transitions_added_while_completing.clear()
    
    def __or__(self, other: Automaton) -> NFA:
        '''
        Returns:
            NFA: the union between this automaton and other
        '''
        return _automaton_union({self,other})
    
    def __and__(self,other:Automaton) -> DFA:
        '''
        Returns:
            DFA: the intersection between this automaton and other
        '''
        return _automaton_intersection({self,other})

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
        self._preimages = {}
    
    cdef set[State] _state_preimage_for_symbol(self,State state,str symbol):
        cdef tuple[str,str] key = (state._id,symbol)
        cdef set[State] result = set()
        cdef str state_id
        cdef str current_state_id = state._id

        if key in self._preimages:
            return self._preimages[key]
        
        for key,state_id in self._trans_func._table.items():
            if state_id == current_state_id and key[1] == symbol:
                result.add(self._states_by_id[key[0]])
        key = (state._id,symbol)
        self._preimages[key] = result
        return result
    
    cdef set[State] _block_preimage_for_symbol(self,set[State] states,str symbol):
        cdef State state
        cdef set[State] result = set()

        for state in states:
            result.update(self._state_preimage_for_symbol(state,symbol))
        
        return result
    
    cdef Table _build_new_transition_function(self,dict[str,str] old_ids_to_new_ids_map):
        cdef str from_id,to_id
        cdef State from_state,to_state
        cdef tuple[str,str] key
        cdef Table result = Table()

        for key,to_id in self._trans_func._table.items():
            from_id = old_ids_to_new_ids_map[key[0]]
            to_id = old_ids_to_new_ids_map[to_id]
            key = (from_id,key[1])
            result._table[key] = to_id
        
        return result

    cdef DFA _build_new_dfa(self,list[set[State]] partition):
        cdef set[State] states,new_states
        cdef dict[str,str] old_ids_to_new_ids_map = {}
        cdef list[str] states_ids
        cdef State state
        cdef str new_state_id
        cdef bint is_accept
        cdef Table transition_function
        
        new_states = set()

        for states in partition:
            if not states:
                continue

            is_accept = False # type:ignore
            states_ids = [state._id for state in states]
            states_ids.sort()
            new_state_id = sha256(''.join(states_ids).encode()).hexdigest()
            
            for state in states:
                old_ids_to_new_ids_map[state._id] = new_state_id
                if state._is_accept:
                    is_accept = True # type:ignore
            
            state = State(new_state_id,set(states),is_accept)
            new_states.add(state)
        
        transition_function = self._build_new_transition_function(old_ids_to_new_ids_map)
        return create_dfa(new_states,transition_function,old_ids_to_new_ids_map[self._start_state._id],self._alphabet)

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
        cdef bint result = self._start_state._is_accept
        for symbol in string:
            self.walk(symbol)
            if self._is_stuck:
                result = False # type:ignore
                break
            else:
                result = self._current_state._is_accept
        self.reset()
        return result
    
    cpdef DFA minimize(self):
        '''
        Returns:
            DFA: a minimized dfa equivalent to this (this process is done with the Hopcroft's algortihm)
        '''
        # to know if the dfa was complete before start the minimization process
        cdef bint was_completed = False # type:ignore
        cdef set[State] finals,not_finals
        # partition of states to build equivalent classes
        cdef list[set[State]] partition = []
        # queue of work for the minimization process
        cdef list[set[State]] queue = []
        # current block that is processing
        cdef set[State] current_block
        # premiage of the current block processing
        cdef set[State] current_block_preimage,current_partition_item,intersection

        cdef str symbol
        cdef int block_idx
        cdef DFA result

        if not self._is_complete:
            was_completed = True # type:ignore
            self.make_complete()
        
        finals = self.finals
        not_finals = self.states.difference(finals)

        partition.append(finals)
        partition.append(not_finals)

        # puts into the queue the set with smaller size, if both has the same size,
        # puts both sets
        if len(finals) <= len(not_finals):
            queue.append(finals)
        if len(not_finals) <= len(finals):
            queue.append(not_finals)
        
        while queue:

            current_block = queue.pop()

            # if the current block already doesn't exists, is skiped
            if not current_block in partition:
                continue
            
            for symbol in self._alphabet:
                # for symbol in alphabet, gets the preimage for the current block of states
                current_block_preimage = self._block_preimage_for_symbol(current_block,symbol)
                block_idx = 0
                while block_idx < len(partition):
                    current_partition_item = partition[block_idx]
                    # gets the intersection between the preimage and the item
                    intersection = current_partition_item.intersection(current_block_preimage)
                    # if there is states in the preimage that are outside of the current item
                    # of the current partition
                    if intersection and intersection != current_partition_item:
                        # updates the partition
                        partition[block_idx] = intersection
                        diff = current_partition_item.difference(intersection)
                        partition.append(diff)
                        if not current_partition_item in queue:
                            if len(diff) <= len(intersection):
                                queue.append(diff)
                            if len(intersection) <= len(diff):
                                queue.append(intersection)
                        else:
                            queue.append(diff)
                            queue.append(intersection)

                    block_idx += 1
        
        result = self._build_new_dfa(partition)
        if was_completed:
            self.restore_to_before_complete()
        return result
    
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
    
    cdef State _build_state(self,set[State] states):
        cdef str state_id
        cdef State state
        cdef list[str] ids = []
        cdef bint is_accept = False # type:ignore
        cdef set[State] state_value = set(states)

        for state in states:
            ids.append(state._id)
            if state._is_accept:
                is_accept = True # type:ignore
        
        ids.sort()
        state_id = sha256(''.join(ids).encode()).hexdigest()
        return State(state_id,state_value,is_accept)
    
    cdef State _build_new_state(self,State state,Table target_table,set[State] current_states):
        cdef str symbol
        cdef State st
        cdef list[str] ids = [st._id for st in current_states]
        cdef set[State] state_value = state._value
        cdef set[State] new_states
        cdef tuple[str,str] key

        for symbol in self._alphabet:
            new_states = set()
            for st in state_value:
                key = (st._id,symbol)
                if key in self._trans_func._table:
                    new_states.update(self.clousure(self.next(st,symbol)))
            
            if len(new_states) == 0:
                continue
            
            st = self._build_state(new_states)
            key = (state._id,symbol)
            if not key in target_table._table:
                target_table._table[key] = st._id
            if not st._id in ids:
                return st
        return None # type:ignore

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
        cdef State f_state,t_state

        if not f_id in self._states_by_id:
            f_state = State(f_id,f_value,f_accept)
            if isinstance(f_state._value,set):
                f_state._value = set(f_state._value)
            self._states_by_id[f_id] = f_state
        if not t_id in self._states_by_id:
            t_state = State(t_id,t_value,t_accept)
            if isinstance(t_state._value,set):
                t_state._value = set(t_state._value)
            self._states_by_id[t_id] = t_state

        if not f_id in self._epsilons:
            self._epsilons[f_id] = set()
        self._epsilons[f_id].add(t_id)
    
    cpdef DFA to_deterministic(self):
        '''
        Returns:
            DFA: the equivalent dfa to this one
        '''
        cdef bint change = True # type:ignore
        cdef Table table = Table()
        cdef set[State] new_states = set()
        cdef State start_state = self._build_state(self.clousure(self._start_state))
        cdef State state,new_state

        if not self._epsilons:
            return create_dfa(self.states,self._trans_func,self._start_state._id,self._alphabet)

        new_states.add(start_state)

        while change:
            change = False # type:ignore

            for state in new_states:
                new_state = self._build_new_state(state,table,new_states)
                if new_state:
                    new_states.add(new_state)
                    change = True # type:ignore
                    break
        
        return create_dfa(new_states,table,start_state._id,self._alphabet)
    
    def __iadd__(self,tuple[State,str,State] transition) -> NFA:
        cdef State from_state = <State>transition[0]
        cdef State to_state = <State>transition[2]
        cdef str symbol = <str>transition[1]

        self.add_transition(from_state,to_state,symbol)
        return self

cdef DFA _copy_dfa(DFA dfa):
    cdef DFA result
    cdef State state,copy_state
    cdef str state_id
    cdef object state_value

    if isinstance(dfa._start_state._value,set):
        state_value = set(dfa._start_state._value)
    else:
        state_value = dfa._start_state._value

    result = DFA(dfa._start_state._id,state_value,set(dfa._alphabet),dfa._start_state._is_accept)

    for state_id,state in dfa._states_by_id.items():
        if isinstance(state._value,set):
            state_value = set(state._value)
        else:
            state_value = state._value
        copy_state = State(state_id,state_value,state._is_accept)
        result._states_by_id[state_id] = copy_state
    
    result._start_state = result._states_by_id[dfa._start_state._id]
    result._current_state = result._start_state
    result._trans_func._table.update(dfa._trans_func._table)
    result._is_complete = dfa._is_complete
    return result

cdef NFA _copy_nfa(NFA nfa):
    cdef NFA result
    cdef State state,copy_state
    cdef str state_id
    cdef object state_value
    cdef set[str] epsilons
    cdef set[State] clousure

    if isinstance(nfa._start_state._value,set):
        state_value = set(nfa._start_state._value)
    else:
        state_value = nfa._start_state._value
    
    result = NFA(nfa._start_state._id,state_value,set(nfa._alphabet),nfa._start_state._is_accept)

    for state_id,state in nfa._states_by_id.items():
        if isinstance(state._value,set):
            state_value = set(state._value)
        else:
            state_value = state._value
        copy_state = State(state_id,state_value,state._is_accept)
        result._states_by_id[state_id] = copy_state
    
    for state_id,epsilons in nfa._epsilons.items():
        result._epsilons[state_id] = set(epsilons)
    
    for state_id,clousure in nfa._clousures.items():
        result._clousures[state_id] = set()
        for state in nfa._clousures[state_id]:
            result._clousures[state_id].add(result._states_by_id[state._id])
    
    result._is_complete = nfa._is_complete
    return result

cdef NFA _automaton_union(set[Automaton] automatons):
    cdef Automaton aut
    cdef NFA result
    cdef str copy_state_id,union_start_id,to_id,state_id
    cdef State start_state,copy_state,from_state,to_state,state
    cdef object state_value,original_state_value
    cdef dict[str,State] states = {}
    cdef dict[tuple[str,str],str] old_state_to_new_state_map = {}
    cdef list[str] aut_ids = []
    cdef set[str] alphabet = set()
    cdef tuple[str,str] transition
    cdef set[str] epsilons

    for aut in automatons:
        # updates alphabet
        alphabet.update(aut._alphabet)
        aut_ids.append(aut.id)
        # copy states
        for state in aut._states_by_id.values():
            if isinstance(state._value,set):
                state_value = set(state._value)
            else:
                state_value = state._value
            copy_state_id = sha256(f'{aut.id}-{state._id}'.encode()).hexdigest()
            copy_state = State(copy_state_id,state_value,state._is_accept)
            # creates the map
            old_state_to_new_state_map[(aut.id,state._id)] = copy_state_id
            # maps the new id to teh copy state
            states[copy_state_id] = copy_state

    aut_ids.sort()
    union_start_id = sha256(f'UNION-{"-".join(aut_ids)}'.encode()).hexdigest()
    result = NFA(union_start_id,union_start_id,alphabet)

    for aut in automatons:
        # creates an epsilon transition to each start state of the automaton
        from_state = result._start_state
        to_state = states[old_state_to_new_state_map[(aut.id,aut._start_state._id)]]
        result.add_epsilon_transition(from_state,to_state)
        # copy transitions from every automaton
        for transition,to_id in aut._trans_func._table.items():
            from_state = states[old_state_to_new_state_map[(aut.id,transition[0])]]
            to_state = states[old_state_to_new_state_map[(aut.id,to_id)]]
            result.add_transition(from_state,to_state,transition[1])
        # copy epsilon transitions
        for state_id,epsilons in aut._epsilons.items():
            from_state = states[old_state_to_new_state_map[(aut.id,state_id)]]
            for to_id in epsilons:
                to_state = states[old_state_to_new_state_map[(aut.id,to_id)]]
                result.add_epsilon_transition(from_state,to_state)
    
    return result

cdef DFA _dfa_complement(DFA automaton):
    cdef DFA result
    cdef State state

    result = _copy_dfa(automaton)

    if not result.is_complete:
        result.make_complete()
    
    for state in result._states_by_id.values():
        state._is_accept = not state._is_accept # type:ignore
    
    return result

cdef DFA _nfa_complement(NFA automaton):
    cdef DFA dfa = automaton.to_deterministic().minimize()

    return _dfa_complement(dfa)

cdef DFA _automaton_complement(Automaton automaton):
    cdef DFA result

    if isinstance(automaton,DFA):
        result = _dfa_complement(automaton)
    else:
        result = _nfa_complement(automaton) # type:ignore
    return result

cdef DFA _automaton_intersection(set[Automaton] automatons):
    cdef Automaton aut
    cdef DFA dfa
    cdef list[DFA] dfa_list = []
    cdef set[str] alphabet = set()
    cdef int dfa_count, i
    cdef str sym, start_id, new_state_id
    cdef tuple comp_states_tuple, next_states_tuple
    cdef list[State] comp_states_list, next_states_list
    cdef State product_state, next_product_state, comp_state, st
    cdef Table product_transitions = Table()
    cdef dict[str,State] product_states = {}
    cdef list[State] worklist = []
    cdef set[State] new_states_set = set()
    cdef list[str] compound_ids
    cdef bint is_accept

    if not automatons:
        raise ValueError("Intersection of empty set of automata is not defined.")

    # convert every automaton to a dfa
    for aut in automatons:
        if isinstance(aut, DFA):
            dfa = _copy_dfa(<DFA>aut)
        elif isinstance(aut, NFA):
            dfa = (<NFA>aut).to_deterministic().minimize()
        else:
            raise TypeError("Unknown automaton type")
        # updates the alphabet
        alphabet.update(dfa._alphabet)
        dfa_list.append(dfa)

    dfa_count = len(dfa_list)

    # complement the automatons with the new alphabet
    for dfa in dfa_list:
        dfa._alphabet = set(alphabet)
        dfa._is_complete = False # type:ignore
        dfa.make_complete()

    # builds the start state
    comp_states_list = [dfa._start_state for dfa in dfa_list]
    comp_states_tuple = tuple(comp_states_list)

    is_accept = True # type:ignore
    for comp_state in comp_states_list:
        if not comp_state._is_accept:
            is_accept = False # type:ignore
            break

    compound_ids = [f"{dfa_list[i].id}-{(<State>comp_states_list[i])._id}" for i in range(dfa_count)]
    compound_ids.sort()
    start_id = sha256(''.join(compound_ids).encode()).hexdigest()

    product_state = State(start_id, comp_states_tuple, is_accept)
    product_states[start_id] = product_state
    worklist.append(product_state)

    while worklist:
        product_state = worklist.pop()
        comp_states_tuple = <tuple>product_state._value

        for sym in alphabet:
            next_states_list = []
            for i in range(dfa_count):
                comp_state = comp_states_tuple[i]
                # como el DFA está completo, next nunca lanza KeyError
                next_states_list.append(dfa_list[i].next(comp_state, sym))
            next_states_tuple = tuple(next_states_list)

            compound_ids = [f"{dfa_list[i].id}-{(<State>next_states_tuple[i])._id}" for i in range(dfa_count)]
            compound_ids.sort()
            new_state_id = sha256(''.join(compound_ids).encode()).hexdigest()

            if new_state_id not in product_states:
                is_accept = True # type:ignore
                for st in next_states_tuple:
                    if not st._is_accept:
                        is_accept = False # type:ignore
                        break
                next_product_state = State(new_state_id, next_states_tuple, is_accept)
                product_states[new_state_id] = next_product_state
                worklist.append(next_product_state)
            else:
                next_product_state = product_states[new_state_id]

            product_transitions._table[(product_state._id, sym)] = next_product_state._id

    new_states_set = set(product_states.values())
    return create_dfa(new_states_set, product_transitions, start_id, alphabet)

cdef NFA _automaton_concatenation(Automaton first,Automaton second):
    cdef State from_state,to_state
    cdef str state_id,symbol,f_id,t_id,first_id,second_id,new_from_id,new_to_id
    cdef object state_value
    cdef bint is_accept
    cdef NFA result
    cdef tuple[str,str] transition
    cdef dict[str,State] states_by_id = {}
    cdef dict[tuple[str,str],str] old_to_new_map = {}

    first_id = first.id
    second_id = second.id

    state_id = sha256(f'CONCAT-{first_id}-{second_id}'.encode()).hexdigest()
    result = NFA(state_id,state_id,first.alphabet.union(second.alphabet),first._start_state._is_accept)
    
    states_by_id[state_id] = result._start_state

    # maps the states from first automaton
    for f_id in first._states_by_id:
        state_id = sha256(f'{first_id}-{f_id}'.encode()).hexdigest()
        old_to_new_map[(first_id,f_id)] = state_id
        from_state = first._states_by_id[f_id]
        if isinstance(from_state._value,set):
            state_value = set(from_state._value) # type:ignore
        else:
            state_value = from_state._value
        states_by_id[state_id] = State(state_id,state_value)
    
    # maps the states from second automaton
    for f_id in second._states_by_id:
        state_id = sha256(f'{second_id}-{f_id}'.encode()).hexdigest()
        old_to_new_map[(second_id,f_id)] = state_id
        from_state = second._states_by_id[f_id]
        if isinstance(from_state._value,set):
            state_value = set(from_state._value) # type:ignore
        else:
            state_value = from_state._value
        is_accept = from_state._is_accept
        states_by_id[state_id] = State(state_id,state_value,is_accept)

    # makes a epsilon transition from new start to first start state
    from_state = result._start_state
    to_state = states_by_id[old_to_new_map[(first_id,first._start_state._id)]]

    result.add_epsilon_transition(from_state,to_state)

    # copy transitions from first automaton
    for transition,t_id in first._trans_func._table.items():
        f_id = <str>transition[0]
        symbol = <str>transition[1]
        from_state = states_by_id[old_to_new_map[(first_id,f_id)]]
        to_state = states_by_id[old_to_new_map[(first_id,t_id)]]
        result.add_transition(from_state,to_state,symbol)
    
    # copy epsilons transitions from first automaton
    for f_id in first._epsilons:
        new_from_id = old_to_new_map[(first_id,f_id)]
        if not new_from_id in result._epsilons:
            if not new_from_id in result._states_by_id:
                result._states_by_id[new_from_id] = states_by_id[new_from_id]
            result._epsilons[new_from_id] = set()
        for t_id in first._epsilons[f_id]:
            new_to_id = old_to_new_map[(first_id,t_id)]
            if not new_to_id in result._states_by_id:
                result._states_by_id[new_to_id] = states_by_id[new_to_id]
            result._epsilons[new_from_id].add(new_to_id)
    
    # makes an epsilon transition from every final state of first to second.start_state
    to_state = states_by_id[old_to_new_map[(second_id,second._start_state._id)]]
    for from_state in first.finals:
        f_id = old_to_new_map[(first_id,from_state._id)]
        from_state = states_by_id[f_id]
        result.add_epsilon_transition(from_state,to_state)
    
    # copy transitions from second automaton
    for transition,t_id in second._trans_func._table.items():
        f_id = <str>transition[0]
        symbol = <str>transition[1]
        from_state = states_by_id[old_to_new_map[(second_id,f_id)]]
        to_state = states_by_id[old_to_new_map[(second_id,t_id)]]
        result.add_transition(from_state,to_state,symbol)
    
    # copy epsilons transitions from second automaton
    for f_id in second._epsilons:
        new_from_id = old_to_new_map[(second_id,f_id)]
        if not new_from_id in result._epsilons:
            if not new_from_id in result._states_by_id:
                result._states_by_id[new_from_id] = states_by_id[new_from_id]
            result._epsilons[new_from_id] = set()
        for t_id in second._epsilons[f_id]:
            new_to_id = old_to_new_map[(second_id,t_id)]
            if not new_to_id in result._states_by_id:
                result._states_by_id[new_to_id] = states_by_id[new_to_id]
            result._epsilons[new_from_id].add(new_to_id)

    return result

cdef NFA _automaton_clousure(Automaton automaton, int type_):
    '''
    type_ = 0: Kleene Star clousure
    type_ = 1: Positive Clousure
    type_ = 2: Optional
    '''
    cdef set[State] new_states = set()
    cdef dict[str,State] states_by_id = {}
    cdef str symbol,from_id,to_id
    cdef object state_value
    cdef State state,copy_state
    cdef NFA result
    cdef tuple[str,str] transition
    cdef str aut_id = automaton.id
    
    # copy the states
    for from_id,state in automaton._states_by_id.items():
        state_value = state._value
        if isinstance(state_value,set):
            copy_state = State(from_id,set(state_value),state._is_accept)
        else:
            copy_state = State(from_id,state_value,state._is_accept)
        states_by_id[from_id] = copy_state

    result = NFA(f'{aut_id}-kleene-star',f'{aut_id}-kleene-star',automaton._alphabet,type_ == 0 or type_ == 2) # type:ignore

    # copy transitions
    for transition,to_id in automaton._trans_func._table.items():
        from_id = <str>transition[0]
        symbol = <str>transition[1]
        state = states_by_id[from_id]
        copy_state = states_by_id[to_id]

        result.add_transition(state,copy_state,symbol)
    
    # copy epsilon transitions
    for from_id in automaton._epsilons:
        state = states_by_id[from_id]
        for to_id in automaton._epsilons[from_id]:
            copy_state = states_by_id[to_id]
            result.add_epsilon_transition(state,copy_state)
    
    # makes epsilon transition from result start state to automaton start state
    state = states_by_id[automaton._start_state._id]
    result.add_epsilon_transition(result._start_state,state)

    if not type_ == 2:
        # makes epsilon transition from finals states to the new start
        for state in automaton.finals:
            result.add_epsilon_transition(state,result._start_state)
    
    return result
    
cpdef DFA create_dfa(set[State] states,Table transition_function,str start_id,set[str] alphabet):
    '''
    Args:
        states (Set[State]): the states of the automaton
        transition_function (Table): transition function of the automaton
        start_id (str): id of the initial state of the automaton
        alphabet (Set[str]): alphabet of the automaton
    
    Returns:
        DFA: the just created DFA with the given description
    '''
    cdef State state,start_state

    for state in states:
        if state._id == start_id:
            start_state = state
            break
    
    if not start_state:
        raise ValueError(f'A initial state is needed, not found any state with given id {start_id}')
    
    dfa = DFA(start_id,None,alphabet,start_state._is_accept)
    dfa._start_state = start_state
    dfa._current_state = dfa._start_state
    dfa._states_by_id[start_id] = start_state
    dfa._trans_func = transition_function
    for state in states:
        dfa._states_by_id[state._id] = state
    dfa._is_complete = len(transition_function._table) == len(states) * len(alphabet) # type:ignore
    return dfa