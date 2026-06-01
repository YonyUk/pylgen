from typing import Tuple,Callable,Any,Iterable

from automaton.automaton cimport Automaton,DFA,State,_automaton_union
from common.types cimport Token,Symbol
from common.enums import TokenType

cdef class LexerNotInitializedException(Exception):
    pass

cdef class LexerNotTokensProvidedException(Exception):
    pass

cdef class BaseLexer:

    def __init__(self,get_symbol_function:Callable[[Any,str],Symbol],ignore_pattern:DFA) -> None:
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
            if self._ignore.accept(list(self._current_token._text)):
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
            return { state._value }
        
        stack = [(0,list(state._value))]

        while stack:
            entered = False # type:ignore
            last_index,current_set = stack[-1] # type:ignore
            for current_index in range(last_index,len(current_set)):
                current_state = current_set[current_index] # type:ignore
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

        for priority in sorted(self._priorites.keys()):
            if self._priorites[priority] in self._types_by_state[self._dfa._current_state._id]:
                symbol = self._get_symbol(self._priorites[priority],text)
                return Token(text,self._priorites[priority],symbol,self._line,self._column) # type:ignore
        return None # type:ignore

    cdef bint _move_next(self):
        cdef tuple[str,str] transition
        cdef str current_symbol
        cdef bint line_jumped = False # type:ignore

        if not self._initialized:
            raise LexerNotInitializedException()
        
        self._current_token = None # type:ignore        
        # restart the pointer and text readed
        self._text_position_pointer = 0
        self._text_readed = ''
        # restart the dfa
        self._dfa.reset()

        while self._current_token is None and self._text_position_pointer < len(self._text):
            
            current_symbol = self._text[self._text_position_pointer]
            # checks for a transition
            transition = (self._dfa._current_state._id,current_symbol)
            while transition in self._dfa._trans_func._table:
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
            self._column += len(self._text_readed)
            if self._text_position_pointer == 0:
                line_jumped = '\n' == self._text[0] # type:ignore
                self._text = self._text[1:]
                self._column += 1
            else:
                line_jumped = '\n' in self._text[:self._text_position_pointer] # type:ignore
                self._text = self._text[self._text_position_pointer:]
            if line_jumped:
                self._line += 1
                self._column = 1
            line_jumped = False # type:ignore
            self._text_position_pointer = 0
            self._text_readed = ''

        return self._current_token is not None # type:ignore

    cdef Token _current(self):
        return self._current_token
    
    cpdef void initialize(self):
        cdef State state
        if len(self._automatons) == 0:
            raise LexerNotTokensProvidedException()
        if not self._initialized:
            self._dfa = _automaton_union(self._automatons).to_deterministic().minimize()
            for state in self._dfa._states_by_id.values():
                self._types_by_state[state._id] = self._get_dfa_state_values(state)
            self._initialized = True # type:ignore

    cdef void _add_token(self,int priority,object type_,Automaton automaton):
        if not issubclass(type(type_),TokenType):
            raise ValueError('type_ must be subclass of TokenType')
        if not type_ in self._priorites.values():
            self._priorites[priority] = type_
            self._automatons.add(automaton)
    
    cpdef void load_text(self,str text):
        self._column = 1
        self._line = 1
        self._text = text
        self._text_position_pointer = 0
        self._text_readed = ''
    
    def __setitem__(self,key:Tuple[int,object],automaton:Automaton):
        self._add_token(key[0],key[1],automaton)