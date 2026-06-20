from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production
from analisis.error cimport SintaxError

cdef class ParsingException(Exception):
    pass

cdef class ParseTreeNode:
    cdef Symbol _symbol
    cdef int _line,_column
    cdef list[ParseTreeNode] _childrens

cdef class Parser:
    cdef AST _ast
    cdef bint _parsed
    cdef ParseTreeNode _parse_tree
    cdef list[ParseTreeNode] _parse_tree_nodes
    cdef set[SintaxError] _errors

    cdef void _try_parse(self,Token token)
    cpdef void reset(self)

cdef class BottomUpParser(Parser):
    cdef dict[Production,object] _reductor_by_production
    cdef dict[tuple[str,Symbol],str] _goto_table
    cdef dict[tuple[str,Symbol],tuple[str,object]] _action_table
    cdef list[Symbol] _stack
    cdef list[AST] _stack_ast
    cdef list[str] _stack_states
    cdef str _start_state
    cdef dict[Symbol,set[Symbol]] _follows
    cdef set[Symbol] _current_syncronization_set
    cdef bint _panic_mode
    cdef Symbol _recovery_symbol

    cdef void _start_recovery_mode(self,Symbol symbol,int line,int column)
    cdef void _end_recovery_mode(self)
    cdef void _set_reductor(self,Production production,object reductor)