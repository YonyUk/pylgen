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
        self._eof = None # type:ignore
    
    @property
    def errors(self) -> Set[LexicError]:
        return self._errors.copy()

    @property
    def tokens(self) -> Iterable[Token]:
        cdef LexicError error
        cdef LexicRule rule
        cdef int line,column
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
            line = self._current_token._line
            column = self._current_token._column
        if self._eof:
            self._eof._line = line
            self._eof._column = column
            yield self._eof

    cpdef void clear_errors(self):
        self._errors.clear()
    
    cpdef void set_eof_token(self,str symbol,object type_):
        if not isinstance(type_,self._enum_type): # type:ignore
            raise ValueError(f'type_ must be a member of {self._enum_type}')
        self._eof = Token(symbol,type_,Symbol(symbol,True),0,0) # type:ignore

    cpdef void add_token_regex(self,int priority,object type_,str re):
        cdef DFA dfa = _parse(re)
        cdef State state

        for state in dfa._states_by_id.values():
            if state._is_accept:
                state._value = type_
        
        self._add_token(priority,type_,dfa)
        if not type_ in self._rules:
            self._rules[type_] = set()

    def __setitem__(self, key: Tuple[int, object], re:str):
        self.add_token_regex(key[0],key[1],re)
    
    cpdef void add_rule(self,object type_,LexicRule rule):
        self._rules[type_].add(rule)