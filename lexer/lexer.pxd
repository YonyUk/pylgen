from automaton.automaton cimport DFA,Automaton,State
from common.types cimport Token,Symbol

cdef class LexerNotInitializedException(Exception):
    pass

cdef class LexerNotTokensProvidedException(Exception):
    pass

cdef class BaseLexer:
    cdef str _text
    cdef str _text_readed
    cdef int _text_position_pointer
    cdef int _line
    cdef int _column
    cdef set[Automaton] _automatons
    cdef bint _initialized
    cdef dict[int,object] _priorites
    cdef DFA _dfa
    cdef object _get_symbol_function
    cdef dict[str,set[object]] _types_by_state

    cdef Token _get_token(self,str text,int line,int column)
    cdef void _add_token(self,int priority,object type_,Automaton automaton)
    cdef Symbol _get_symbol(self,object type_,str text)
    cdef set[object] _get_dfa_state_values(self,State state)

    cpdef void initialize(self)
    cpdef void load_text(self,str text)