import inspect
from typing import Iterable,Callable,List,Tuple,Dict
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
    
    @property
    def parse_tree_data(self) -> Tuple[List[Tuple[str,str]],Dict[str,Symbol]]:
        '''
        Returns:
            Tuple[List[Tuple[str,str]],Dict[str,Symbol]]: the necessary data to build the parse tree
        '''
        if self._parsed:
            return self._parse_tree_edges,self._symbol_by_parse_tree_node
        raise ValueError('Nothing parsed yet')

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
        self._stack_ast = []
        self._start_state = start_state
        self._parsed = False # type:ignore
        self._parse_tree_edges = []
        self._symbol_by_parse_tree_node = {}

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef str state = self._stack_states[-1]
        cdef tuple[str,Symbol] key = (state,token._symbol)
        cdef AST new_ast,loop_ast
        cdef str parse_tree_node_id_from,parse_tree_node_id_to
        cdef tuple[str,str] parse_tree_node_edge
        cdef int idx

        if self._parsed:
            raise ValueError('Parsing error')

        if not key in self._action_table:
            raise ValueError('Parsing error')
        
        current_action = self._action_table[key]

        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            new_ast = self._reductor_by_production[p](self._stack_ast[-1*len(p._production):]) # type:ignore
            # build the parse tree
            parse_tree_node_id_from = f'{p._head}-{new_ast._line}-{new_ast._column}'
            for idx in range(len(p._production)):
                loop_ast = self._stack_ast[idx - len(p._production)]
                # adds the edge from the new symbol to 
                parse_tree_node_id_to = f'{self._stack[idx - len(p._production)]}-{loop_ast._line}-{loop_ast._column}'
                parse_tree_node_edge = (parse_tree_node_id_from,parse_tree_node_id_to)
                self._parse_tree_edges.append(parse_tree_node_edge)
            # adds the symbol of the origin node for the new edge
            self._symbol_by_parse_tree_node[parse_tree_node_id_from] = new_ast._symbol
            
            self._stack = self._stack[:-1*len(p._production)] + [p._head]
            self._stack_states = self._stack_states[:-1*len(p._production)]
            self._stack_ast = self._stack_ast[:-1*len(p._production)] + [new_ast]
            state = self._stack_states[-1]
            key = (state,self._stack[-1])
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
            # adds a new symbol node to the parse tree
            parse_tree_node_id_from = f'{token._symbol}-{token._line}-{token._column}'
            self._symbol_by_parse_tree_node[parse_tree_node_id_from] = token._symbol
            self._stack.append(token._symbol)
            self._stack_ast.append(token)
            self._stack_states.append(state)
        if current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            self._ast = self._stack_ast[-1]

    cpdef void reset(self):
        '''
        Description:
            reset the parser to it's initial state to parse tokens again 
        '''
        self._parsed = False # type:ignore
        self._stack.clear()
        self._stack_ast.clear()
        self._stack_states = [self._start_state]
        self._symbol_by_parse_tree_node.clear()
        self._parse_tree_edges.clear()

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