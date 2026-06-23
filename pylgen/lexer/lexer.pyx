from typing import Callable,Any,Tuple,Iterable,Set

from ..common.types cimport Symbol,Token
from ..automaton.automaton cimport DFA,State
from ..regex.engine cimport _parse
from ..analisis.lexical cimport LexicRule
from ..analisis.error cimport LexicError
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA) -> None:
        super().__init__(get_symbol_function, ignore_pattern)
        self._rules = {}
        self._errors = set()
    
    @property
    def errors(self) -> Set[LexicError]:
        return self._errors.copy()

    @property
    def tokens(self) -> Iterable[Token]:
        cdef LexicError error
        cdef LexicRule rule
        self.initialize()
        while self._move_next():
            if self._ignore.accept(list(self._current_token._text)):
                continue
            if self._current_token._type in self._rules:
                for rule in self._rules[self._current_token._type]:
                    error = rule.check(self._current_token)
                    if not error is None:
                        self._errors.add(error)
            yield self._current_token

    cpdef void clear_errors(self):
        self._errors.clear()

    def __setitem__(self, key: Tuple[int, object], re:str):
        cdef DFA dfa = _parse(re)
        cdef State state

        for state in dfa._states_by_id.values():
            if state._is_accept:
                state._value = key[1]
        
        self._add_token(key[0],key[1],dfa)
        if not key[1] in self._rules:
            self._rules[key[1]] = set()
    
    cpdef void add_rule(self,object type_,LexicRule rule):
        self._rules[type_].add(rule)