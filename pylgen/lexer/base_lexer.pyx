from typing import Tuple,Callable,Any,Iterable,get_type_hints
import inspect

from ..automaton.automaton cimport Automaton,DFA,NFA,State,_automaton_union
from ..common.types cimport Token,Symbol
from ..common.enums import TokenType

cdef class LexerNotInitializedException(Exception):
    pass

cdef class LexerNotTokensProvidedException(Exception):
    pass

cdef class BaseLexer:

    def __init__(self,get_symbol_function:Callable[[Any,str],Symbol],ignore_pattern:DFA,check_annotation:bool=True) -> None:
        self._column = 0
        self._line = 0
        self._priorites = {}
        self._text = ''
        self._text_position_pointer = 0
        self._text_readed = ''
        self._initialized = False # type:ignore
        self._automatons = set()

        if not get_symbol_function:
            raise ValueError('get_symbol_function can not be None')
        
        if check_annotation:
            sig = inspect.signature(get_symbol_function)
            try:
                hints = get_type_hints(get_symbol_function)
            except Exception as ex:
                hints = {}
            params = list(sig.parameters.values())
            if len(params) != 2:
                raise ValueError('Invalid signature of function get_symbol_function')
            param0 = params[0]
            if param0.annotation is inspect.Parameter.empty:
                raise ValueError('Invalid signature of function get_symbol_function')

            token_type_annot = hints.get(param0.name,param0.annotation)
            # if token_type_annot is an string
            if isinstance(token_type_annot,str):
                try:
                    resolved = eval(token_type_annot,get_symbol_function.__globals__)
                except NameError:
                    raise ValueError('couldn\'t resolve type annotation for first parameter of get_symbol_function')
                token_type_annot = resolved

            if not issubclass(token_type_annot,TokenType):
                raise ValueError('Invalid signature of function get_symbol_function')

            param1 = params[1]
            if param1.annotation is not inspect.Parameter.empty:
                annot = hints.get(param1.name,param1.annotation)
                if isinstance(annot,str):
                    try:
                        resolved = eval(annot,get_symbol_function.__globals__)
                    except NameError:
                        raise ValueError('couldn\'t resolve type annotation for second parameter of get_symbol_function')
                    annot = resolved
                if annot != str:
                    raise ValueError('Invalid signature of function get_symbol_function')
            else:
                raise ValueError('Invalid signature of function get_symbol_function')
            self._enum_type = token_type_annot

            ret_annotation = sig.return_annotation
            if isinstance(ret_annotation,str):
                try:
                    resolved = eval(ret_annotation,get_symbol_function.__globals__)
                except NameError:
                    raise ValueError('couldn\'t resolve type annotation for return type of get_symbol_function')
                ret_annotation = resolved
            if ret_annotation != Symbol:
                raise ValueError('Invalid signature of function get_symbol_function')
        
        self._get_symbol_function = get_symbol_function
        self._types_by_state = {}
        self._ignore = ignore_pattern
    
    @property
    def dfa(self) -> DFA:
        if not self._initialized:
            raise LexerNotInitializedException()
        return self._dfa
    
    @property
    def tokens(self) -> Iterable[Token]:
        self.initialize()
        while self._move_next():
            if not self._ignore._is_stuck and self._ignore._current_state._is_accept:
                continue
            yield self._current_token
    
    cdef set[object] _get_dfa_state_values(self,State state):
        cdef list[tuple[int,list[object]]] stack
        cdef list[object] current_set
        cdef int last_index,current_index
        cdef bint entered = False # type:ignore
        cdef set[object] result = set()
        cdef State current_state

        if not isinstance(state._value,set):
            if issubclass(type(state._value),TokenType) and state._is_accept:
                return { state._value }
            return set()
        
        stack = [(0,list(state._value))]

        while stack:
            entered = False # type:ignore
            last_index,current_set = stack[-1] # type:ignore
            for current_index in range(last_index,len(current_set)):
                current_state = current_set[current_index] # type:ignore
                if not current_state._is_accept:
                    continue
                if isinstance(current_state._value,set):
                    entered = True # type:ignore
                    stack[-1] = (current_index + 1,current_set)
                    stack.append((0,list(current_state._value))) # type:ignore
                    break
                elif issubclass(type(current_state._value),TokenType):
                    result.add(current_state._value)
            if not entered:
                stack.pop()
        
        return result

    cdef Symbol _get_symbol(self,object type_,str text):
        if not issubclass(type(type_),TokenType):
            raise ValueError('type_ must be a subclass of TokenType')
        return self._get_symbol_function(type_,text) # type:ignore

    cdef Token _get_token(self,str text,int line,int column):
        cdef object type_ = None
        cdef int priority
        cdef Symbol symbol

        for priority in self._priorities_sorted:
            if self._priorites[priority] in self._types_by_state[self._dfa._current_state._id]:
                symbol = self._get_symbol(self._priorites[priority],text)
                return Token(text,self._priorites[priority],symbol,self._line,self._column) # type:ignore
        return None # type:ignore

    cdef bint _move_next(self):
        cdef tuple[str,str] transition
        cdef str current_symbol

        if not self._initialized:
            raise LexerNotInitializedException()
        
        self._current_token = None # type:ignore        
        # restart the pointer and text readed
        self._text_readed = ''
        # restart the dfa
        self._dfa.reset()
        # restart the ignore dfa

        while self._current_token is None and self._text_position_pointer < len(self._text):
            self._ignore.reset()
            current_symbol = self._text[self._text_position_pointer]
            # checks for a transition
            transition = (self._dfa._current_state._id,current_symbol)
            while transition in self._dfa_transition_function and (not self._fault_state or self._dfa._trans_func._table[transition] != self._fault_state._id):
                # input(f'readed: {self._text_readed}')
                # input(f'pointer {self._text_position_pointer}')
                # advance the ignore_dfa one step
                self._ignore.walk(current_symbol)
                # advance the dfa one step
                self._dfa.walk(current_symbol)
                # updates the text readed
                self._text_readed += current_symbol
                # updates the pointer
                self._text_position_pointer += 1
                # if the text has been ended
                if self._text_position_pointer >= len(self._text):
                    break
                # updates the current symbol
                current_symbol = self._text[self._text_position_pointer]
                # updates last symbol seen
                # updates the transition to check
                transition = (self._dfa._current_state._id,current_symbol)
    
            self._current_token = self._get_token(self._text_readed,self._line,self._column)
            if not self._current_token:
                if self._text[self._text_position_pointer] == '\n':
                    self._line += 1
                    self._column = 1
                else:
                    self._column += 1
                self._text_position_pointer += 1
            else:
                self._column += len(self._text_readed)
            if '\n' in self._text_readed:
                self._line += self._text_readed.count('\n')
                self._column = len(self._text_readed[self._text_readed.rindex('\n'):])
            self._text_readed = ''
        return self._current_token is not None # type:ignore

    cdef Token _current(self):
        return self._current_token
    
    cdef bint _is_fault_state(self,State state):
        cdef tuple[str,str] key
        cdef str from_state_id,to_state_id

        if state._is_accept:
            return False # type:ignore
        for key,to_state_id in self._dfa._trans_func._table.items():
            from_state_id = <str> key[0]
            if from_state_id == state._id and to_state_id != state._id:
                return False # type:ignore
        
        return True # type:ignore

    cpdef void initialize(self):
        cdef State state
        cdef DFA dfa
        cdef list[set[State]] initial_partition = []
        cdef set[State] not_finals = set()
        cdef State inner_state1,inner_state2
        cdef dict[tuple,set[State]] states_by_type_value = {}
        cdef set state_value_key
        cdef tuple key
        cdef set[State] state_set

        if len(self._automatons) == 0:
            raise LexerNotTokensProvidedException()
        if not self._initialized:
            # creates the dfa
            dfa = _automaton_union(self._automatons).to_deterministic()
            # make it complete
            dfa.make_complete()
            # creates the initial_partition
            for state in dfa._states_by_id.values():
                # if is an accepting state
                if state._is_accept:
                    # for the key of the dictionary
                    state_value_key = set()
                    # looks for each token type in the state
                    for inner_state1 in state._value: # type:ignore
                        if isinstance(inner_state1._value,set):
                            for inner_state2 in inner_state1._value:
                                if isinstance(inner_state2._value,self._enum_type): # type:ignore
                                    state_value_key.add(inner_state2._value)
                        elif isinstance(inner_state1._value,self._enum_type): # type:ignore
                            state_value_key.add(inner_state1._value)
                    # sets all the states with the same token types inside into the
                    # same set of states, this leads to a more refined partition, due
                    # to the fact that the states with the same token types set, are essentially
                    # equals
                    key = tuple(state_value_key)
                    if not key in states_by_type_value:
                        states_by_type_value[key] = set()
                    states_by_type_value[key].add(state)
                else:
                    not_finals.add(state)
            
            for state_set in states_by_type_value.values():
                initial_partition.append(state_set)
            initial_partition.append(not_finals)
            # minimize the dfa
            self._dfa = dfa.minimize(initial_partition)
            for state in self._dfa._states_by_id.values():
                self._types_by_state[state._id] = self._get_dfa_state_values(state)
                if not self._fault_state and  self._is_fault_state(state):
                    self._fault_state = state
            self._priorities_sorted = sorted(self._priorites.keys())
            self._dfa_transition_function = self._dfa._trans_func._table
            self._initialized = True # type:ignore

    cdef void _add_token(self,int priority,object type_,Automaton automaton):
        if not isinstance(type_,self._enum_type): # type:ignore
            raise ValueError(f'type_ must be a member of {self._enum_type}')
        if not type_ in self._priorites.values():
            self._priorites[priority] = type_
            if isinstance(automaton,NFA):
                self._automatons.add(automaton.to_deterministic())
            elif isinstance(automaton,DFA):
                self._automatons.add(automaton)
    
    cpdef void load_text(self,str text):
        self._column = 1
        self._line = 1
        self._text = text
        self._text_position_pointer = 0
        self._text_readed = ''
    
    def __setitem__(self,key:Tuple[int,object],automaton:Automaton):
        self._add_token(key[0],key[1],automaton)