from typing import Callable,Any,Tuple

from common.types cimport Symbol
from automaton.automaton cimport DFA,State
from regex.engine cimport _parse
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA) -> None:
        super().__init__(get_symbol_function, ignore_pattern)
    
    def __setitem__(self, key: Tuple[int, object], re:str):
        cdef DFA dfa = _parse(re)
        cdef State state

        for state in dfa._states_by_id.values():
            if state._is_accept:
                state._value = key[1]
        
        self._add_token(key[0],key[1],dfa)