from typing import Tuple,Callable,Any

from automaton.automaton cimport Automaton,DFA,State,_automaton_union
from common.types cimport Token,Symbol
from common.enums import TokenType

cdef class LexerNotInitializedException(Exception):
    pass

cdef class LexerNotTokensProvidedException(Exception):
    pass

cdef class BaseLexer:

    def __init__(self,get_symbol_function:Callable[[Any,str],Symbol]) -> None:
        self._column = 0
        self._line = 0
        self._priorites = {}
        self._text = ''
        self._text_position_pointer = 0
        self._text_readed = ''
        self._initialized = False # type:ignore
        self._automatons = set()
        self._get_symbol_function = get_symbol_function
        self._types_by_state = {}
    
    @property
    def dfa(self) -> DFA:
        if not self._initialized:
            raise LexerNotInitializedException()
        return self._dfa
    
    cdef set[object] _get_dfa_state_values(self,State state):
        cdef list[tuple[int,list[object]]] stack
        cdef list[object] current_set
        cdef int last_index,current_index
        cdef bint entered = False # type:ignore
        cdef set[object] result = set()

        if not isinstance(state._value,set):
            return { state._value }
        
        stack = [(0,list(state._value))]

        while stack:
            last_index,current_set = stack[-1] # type:ignore

            for current_index in range(last_index,len(current_set)):
                if isinstance(current_set[current_index],set):
                    entered = True # type:ignore
                    stack[-1] = (current_index + 1,current_set)
                    stack.append((0,list(current_set[current_index]))) # type:ignore
                    break
                else:
                    result.add(current_set[current_index])
            if not entered:
                stack.pop()
        
        return result

    cdef Symbol _get_symbol(self,object type_,str text):
        return self._get_symbol_function(type_,text) # type:ignore

    cdef Token _get_token(self,str text,int line,int column):
        cdef object type_ = None
        cdef int priority
        cdef Symbol symbol

        for priority in sorted(self._priorites.keys()):
            if self._priorites[priority] in self._types_by_state[self._dfa._current_state._id]:
                symbol = self._get_symbol(self._priorites[priority],text)
                return Token(text,self._priorites[priority],symbol,self._line,self._column) # type:ignore
        
        return Token('',TokenType.GARBAGE,Symbol('GARBAGE'),-1,-1) # type:ignore
    
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
        if not type_ in self._priorites.values():
            self._priorites[priority] = type_
            self._automatons.add(automaton)
    
    cpdef void load_text(self,str text):
        self._column = 1
        self._line = 1
        self._text = text
        self._text_position_pointer = 0
        self._text_readed = ''