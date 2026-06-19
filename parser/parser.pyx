import inspect
from typing import Iterable,Callable,List,Tuple,Dict
from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production
from parser.bottom_up_parser_actions import BottomUpParserAction
from analisis.error cimport SintaxError

cdef class ParseTreeNode:

    def __init__(self,Symbol symbol,int line,int column,list[ParseTreeNode] childrens=[]):
        self._symbol = symbol
        self._line = line
        self._column = column
        self._childrens = childrens
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol
    
    @property
    def line(self) -> int:
        return self._line
    
    @property
    def column(self) -> int:
        return self._column
    
    @property
    def childrens(self) -> List[ParseTreeNode]:
        return self._childrens

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
    def parse_tree(self) -> ParseTreeNode:
        '''
        Returns:
            ParseTree: the current parse tree if parsing was successfully
        '''
        if self._parsed:
            return self._parse_tree
        raise ValueError('Nothing parsed yet')
    
    @property
    def errors(self) -> set[SintaxError]:
        return self._errors

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
        self._parse_tree_nodes = []

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef str state = self._stack_states[-1]
        cdef tuple[str,Symbol] key = (state,token._symbol)
        cdef AST new_ast
        cdef ParseTreeNode new_node
        cdef list[ParseTreeNode] childrens

        if self._parsed:
            raise ValueError('Parsing error')
        
        if not key in self._action_table:
            raise ValueError('Parsing error')
        
        current_action = self._action_table[key]
        # while the action is reduce
        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            new_ast = self._reductor_by_production[p](self._stack_ast[-1*len(p._production):]) # type:ignore
            # build the parse tree
            childrens = self._parse_tree_nodes[-1*len(p._production):]
            new_node = ParseTreeNode(p._head,new_ast._line,new_ast._column,childrens)
            # updates the stack of parse tree nodes
            self._parse_tree_nodes = self._parse_tree_nodes[:-1*len(p._production)] + [new_node]
            # update the stack of symbols
            self._stack = self._stack[:-1*len(p._production)] + [p._head]
            # update the stack of states
            self._stack_states = self._stack_states[:-1*len(p._production)]
            # update the stack of ast
            self._stack_ast = self._stack_ast[:-1*len(p._production)] + [new_ast]
            # sets the current state
            state = self._stack_states[-1]
            key = (state,self._stack[-1])
            # checks for an action
            if not key in self._action_table:
                raise ValueError('Parsing error')
            current_action = self._action_table[key]
            # checks if the action is shift, due to reductions only may occur at top of the stack
            if current_action[0] != BottomUpParserAction.SHIFT:
                raise ValueError('Parsing error')
            # sets the state by the GOTO table and put it at stack of states top
            state = self._goto_table[key]
            self._stack_states.append(state)
            # checks for an action with the current state and the current token
            key = (state,token._symbol)
            if not key in self._action_table:
                raise ValueError('Parsing error')
            # updates the current action
            current_action = self._action_table[key]
        if current_action[0] == BottomUpParserAction.SHIFT:
            state = self._goto_table[key]
            # adds a new parse tree node to the parse tree
            new_node = ParseTreeNode(token._symbol,token._line,token._column)
            self._parse_tree_nodes.append(new_node)
            # push the symbol in the stack
            self._stack.append(token._symbol)
            # push the ast in the stack
            self._stack_ast.append(token)
            # push the state in the stack
            self._stack_states.append(state)
        if current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            self._ast = self._stack_ast[-1]
            self._parse_tree = self._parse_tree_nodes[-1]

    cpdef void reset(self):
        '''
        Description:
            reset the parser to it's initial state to parse tokens again 
        '''
        self._parsed = False # type:ignore
        self._parse_tree = None # type:ignore
        self._ast = None # type:ignore
        self._stack.clear()
        self._stack_ast.clear()
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