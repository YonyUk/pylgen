# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
from typing import Callable,Any,Tuple,Iterable,Set

from ..common.types cimport Symbol,Token
from ..automaton.automaton cimport DFA,State
from ..regex.engine cimport _parse
from ..analysis.lexical cimport LexicalRule
from ..analysis.error cimport LexicalError
from ..regex.engine import RegexParsingException
from .base_lexer cimport BaseLexer

cdef class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: str,check_annotation:bool=True) -> None:
        cdef DFA ignore_dfa
        try:
            ignore_dfa = _parse(ignore_pattern)
        except RegexParsingException:
            raise
        except ValueError:
            raise ValueError('invalid regex provided')
        except Exception:
            raise
        super().__init__(get_symbol_function, ignore_dfa,check_annotation)
        self._rules = {}
        self._errors = set()
        self._eof = None # type:ignore
    
    @property
    def errors(self) -> Set[LexicalError]:
        return self._errors.copy()

    @property
    def tokens(self) -> Iterable[Token]:
        cdef int line,column
        line = 1
        column = 1
        self.initialize()
        while self._move_next():
            yield self._current()
            line = self._current_token._line
            column = self._current_token._column
        if self._eof:
            self._eof._line = line
            self._eof._column = column + 1
            yield self._eof

    cdef bint _move_next(self):
        cdef bint continue_ = True # type:ignore

        while continue_:
            if not BaseLexer._move_next(self):
                return False # type:ignore
            continue_ = not self._ignore._is_stuck and self._ignore._current_state._is_accept # type:ignore
        
        return True # type:ignore
    
    cdef Token _current(self):
        cdef LexicalRule rule
        cdef LexicalError error
        # cdef int line,column

        if self._current_token._type in self._rules:
            for rule in self._rules[self._current_token._type]:
                error = rule.check(self._current_token)
                if not error is None:
                    self._errors.add(error)
        
        if self._current_token._type == self._enum_type.INVALID_TOKEN: # type:ignore
            error = LexicalError("Invalid token",self._current_token._line,self._current_token._column) # type:ignore
            self._errors.add(error)
        
        return self._current_token

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
    
    cpdef void add_rule(self,object type_,LexicalRule rule):
        self._rules[type_].add(rule)

cdef class IdentedLexer(Lexer):

    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: str, check_annotation: bool = True) -> None:
        super().__init__(get_symbol_function, ignore_pattern, check_annotation)
        self._ident_counter = 0
        self._last_ident_value = 0
        self._sanitaze_function = None
    
    cpdef void set_ident(self,object ident_type):
        if not isinstance(ident_type,self._enum_type): # type:ignore
            raise ValueError(f'ident_type must be a member of {self._enum_type}')
        self._ident_type = ident_type
    
    cpdef void set_indent_symbol(self,Symbol symbol):
        self._indent_symbol = symbol

    cpdef void set_dedent_symbol(self,Symbol symbol):
        self._dedent_symbol = symbol
    
    cpdef void set_text_sanitize_function(self,object sanitaze_function):
        self._sanitaze_function = sanitaze_function
    
    cpdef void load_text(self,str text):
        BaseLexer.load_text(self,text)
        if self._sanitaze_function:
            self._text = self._sanitaze_function(text) # type:ignore

    @property
    def tokens(self) -> Iterable[Token]:
        cdef int line,column
        cdef Token current_token,last_token
        cdef list[Token] idents = []
        cdef int idx

        line = 1
        column = 1

        self.initialize()
        last_token = None # type:ignore
        while self._move_next():
            self._ident_counter = 0
            idents.clear()
            current_token = self._current()
            line = self._current_token._line
            column = self._current_token._column

            if current_token._text == ' ' and current_token._column > 1:
                continue

            if current_token._type == self._ident_type:
                
                if current_token._column > 1:
                    continue
                    
                while current_token._type == self._ident_type and self._move_next():
                    idents.append(current_token)
                    self._ident_counter += 1
                    current_token = self._current()            
                    line = self._current_token._line
                    column = self._current_token._column

                while self._last_ident_value < self._ident_counter:
                    idx = len(idents) + self._last_ident_value - self._ident_counter
                    yield Token('IDENT',self._ident_type,self._indent_symbol,(<Token>idents[idx])._line,(<Token>idents[idx])._column) # type:ignore
                    self._last_ident_value += 1
                
                while self._last_ident_value > self._ident_counter:
                    yield Token('DEDENT',self._ident_type,self._dedent_symbol,current_token._line,current_token._column) # type:ignore
                    self._last_ident_value -= 1
                
                yield current_token
                last_token = current_token
            else:
                if last_token and line > last_token._line:
                    while self._ident_counter < self._last_ident_value:
                        yield Token('DEDENT',self._ident_type,self._dedent_symbol,current_token._line,current_token._column) # type:ignore
                        self._last_ident_value -= 1

                yield current_token
                last_token = current_token         

        while self._last_ident_value > 0:
            yield Token('DEDENT',self._ident_type,self._dedent_symbol,line,column) # type:ignore
            self._last_ident_value -= 1

        if self._eof:
            self._eof._line = line
            self._eof._column = column + 1
            yield self._eof