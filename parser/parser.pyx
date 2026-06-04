import inspect
from typing import Iterable,Callable,List
from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production
from parser.bottom_up_parser_actions import BottomUpParserAction

cdef class Parser:
    '''
    Base class for a parser
    '''

    def __init__(self) -> None:
        raise ValueError('Can not instance this class')

    def parse(self,tokens:Iterable[Token]) -> AST:
        '''
        Args:
            tokens (Iterable[Token])
        
        Returns:
            AST: the ast of the given sequence of tokens
        '''
        cdef Token token
        for token in tokens:
            self._try_parse(token)
        if self._parsed:
            return self._ast
        raise ValueError('Parsing error')

    cdef void _try_parse(self,Token token):
        raise NotImplementedError()
    
    cpdef void reset(self):
        raise NotImplementedError()

cdef class BottomUpParser(Parser):

    def __init__(self,str start_state,dict[tuple[str,Symbol],str] goto_table,dict[tuple[str,Symbol],tuple[str,object]] action_table):
        '''
        Args:
            start_state (str): id of the start state for this parser
            goto_table (Dict[Tuple[str,Symbol],str]): GOTO table for the parser
            action_table (Dict[Tuple[str,Symbol],tuple[str,str | Production]]): ACTION table for the parser
        '''
        self._action_table = action_table
        self._goto_table = goto_table
        self._reductor_by_production = {}
        self._stack_states = [start_state]
        self._stack = []
        self._start_state = start_state
        self._parsed = False # type:ignore

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef str state = self._stack_states[-1]
        cdef tuple[str,Symbol] key = (state,token._symbol)
        cdef AST new_ast

        if self._parsed:
            raise ValueError('Parsing error')

        if not key in self._action_table:
            raise ValueError('Parsing error')
        
        current_action = self._action_table[key]

        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            new_ast = self._reductor_by_production[p](self._stack[-1*len(p._production):]) # type:ignore
            self._stack = self._stack[:-1*len(p._production)] + [new_ast]
            self._stack_states = self._stack_states[:-1*len(p._production)]
            state = self._stack_states[-1]
            key = (state,(<AST>self._stack[-1])._symbol)
            if not key in self._action_table:
                raise ValueError('Parsing error')
            current_action = self._action_table[key]
            if current_action[0] != BottomUpParserAction.SHIFT:
                raise ValueError('Parsing error')
            state = self._goto_table[key]
            self._stack_states.append(state)
            key = (state,token._symbol)
            if not key in self._action_table:
                raise ValueError('Parsing error')
            current_action = self._action_table[key]
        if current_action[0] == BottomUpParserAction.SHIFT:
            state = self._goto_table[key]
            self._stack.append(token)
            self._stack_states.append(state)
        if current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            self._ast = self._stack[-1]

    cpdef void reset(self):
        self._parsed = False # type:ignore
        self._stack = []
        self._stack_states = [self._start_state]

    def __setitem__(self,production:Production,reductor:Callable[[List[AST]],AST]):
        sig = inspect.signature(reductor)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise ValueError('invalid reductor function signature')
        if not params[0].annotation is inspect.Parameter.empty and params[0].annotation != List[AST]:
            raise ValueError('invalid reductor function signature')
        if sig.return_annotation != AST:
            raise ValueError('invalid reductor function signature')
        self._set_reductor(production,reductor)