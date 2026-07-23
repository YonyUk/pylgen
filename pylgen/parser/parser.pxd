from ..common.types cimport Token,AST,Symbol,ASTListView
from ..grammar.grammar cimport Production
from ..analysis.error cimport SyntaxError

cdef class ParsingException(Exception):
    pass

cdef class ParseTreeNode:
    cdef Symbol _symbol
    cdef int _line,_column
    cdef list[ParseTreeNode] _childrens

cdef class Parser:
    cdef AST _ast
    cdef bint _parsed
    cdef bint _draw_parse_tree
    cdef ParseTreeNode _parse_tree
    cdef list[ParseTreeNode] _parse_tree_nodes
    cdef list[SyntaxError] _errors

    cdef void _try_parse(self,Token token)
    cpdef void reset(self)
    cpdef void set_draw_parse_tree_flag(self,bint flag)

cdef class BottomUpParser(Parser):
    cdef dict[int,object] _reductor_by_production
    cdef dict[tuple[str,Symbol],str] _goto_table
    cdef dict[tuple[str,Symbol],tuple[str,object]] _action_table
    cdef dict[long long,int] _goto_table_optimized
    cdef dict[long long,tuple[str,object]] _action_table_optimized
    cdef list[Symbol] _stack
    cdef list[AST] _stack_ast
    cdef list[int] _stack_states
    cdef str _start_state
    cdef set[Symbol] _current_syncronization_set
    cdef bint _panic_mode
    cdef ASTListView _view
    cdef int _stack_top
    cdef int _stack_len
    cdef int _stack_ast_top
    cdef int _stack_ast_len
    cdef int _stack_states_top
    cdef int _stack_states_len

    cdef void _start_recovery_mode(self,Symbol symbol,int line,int column)
    cdef void _end_recovery_mode(self,Symbol symbol)
    cdef void _set_reductor(self,Production production,object reductor)