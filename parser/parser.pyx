import inspect
from typing import Iterable,Callable,List,Tuple,Dict
from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production
from parser.bottom_up_parser_actions import BottomUpParserAction
from analisis.error cimport SintaxError

cdef class ParsingException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
            if len(self._errors) > 0:
                raise ParsingException('The parsing ended with errors')
            return self._ast
        raise ParsingException('Nothing parsed')

    cdef void _try_parse(self,Token token):
        raise NotImplementedError()
    
    @property
    def parse_tree(self) -> ParseTreeNode:
        '''
        Returns:
            ParseTree: the current parse tree if parsing was successfully
        '''
        if self._parsed:
            if len(self._errors) > 0:
                raise ParsingException('The parsing ended with errors')
            return self._parse_tree
        raise ParsingException('Nothing parsed')
    
    @property
    def errors(self) -> set[SintaxError]:
        return self._errors

    cpdef void reset(self):
        raise NotImplementedError()

cdef class BottomUpParser(Parser):

    def __init__(self,str start_state,dict[tuple[str,Symbol],str] goto_table,dict[tuple[str,Symbol],tuple[str,object]] action_table,dict[Symbol,set[Symbol]] follows):
        '''
        Args:
            start_state (str): id of the start state for this parser
            goto_table (Dict[Tuple[str,Symbol],str]): GOTO table for the parser
            action_table (Dict[Tuple[str,Symbol],tuple[str,str | Production]]): ACTION table for the parser
            follows (Dict[Symbol,Set[Symbol]]): dict of FOLLOW set by non-terminal
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
        self._errors = set()
        self._follows = follows
        self._panic_mode = False # type:ignore
        self._current_syncronization_set = set()

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor

    cdef void _start_recovery_mode(self,Symbol symbol,int line, int column):
        cdef Symbol stack_symbol,follow_symbol
        cdef bint started = False # type:ignore
        cdef tuple[str,Symbol] key
        cdef set[Symbol] expected_symbols = set()
        cdef SintaxError error

        for key in self._action_table:
            if key[0] == self._stack_states[-1]:
                follow_symbol = key[1] # type:ignore
                if follow_symbol._is_terminal:
                    expected_symbols.add(follow_symbol)

        error = SintaxError(f'Unexpected symbol "{symbol}"; expected {expected_symbols}',line,column) # type:ignore
        self._errors.add(error)
        self._panic_mode = True # type:ignore
        self._current_syncronization_set = set()

        for stack_symbol in self._stack:
            if not stack_symbol._is_terminal:
                for follow_symbol in self._follows[stack_symbol]:
                    if follow_symbol != symbol:
                        self._current_syncronization_set.add(follow_symbol)
        
        while self._stack_states:
            for follow_symbol in self._current_syncronization_set:
                key = (self._stack[-1],follow_symbol)
                if key in self._action_table and self._action_table[key][0] != BottomUpParserAction.SHIFT:
                    started = True # type:ignore
                    self._recovery_symbol = follow_symbol
                    break
            self._stack_states.pop()
        
        if not self._stack_states:
            self._stack_states = [self._start_state]
            self._current_syncronization_set = set()
            for key in self._action_table:
                if key[0] == self._stack_states[-1]:
                    self._current_syncronization_set.add(key[1]) # type:ignore
    
    cdef void _end_recovery_mode(self):
        self._current_syncronization_set = set()
        self._panic_mode = False # type:ignore

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef str state = self._stack_states[-1]
        cdef tuple[str,Symbol] key = (state,token._symbol)
        cdef AST new_ast
        cdef ParseTreeNode new_node
        cdef list[ParseTreeNode] childrens

        if self._parsed:
            raise ValueError('EOF token already readed')
        
        if not key in self._action_table:
            self._start_recovery_mode(token._symbol,token._line,token._column)
        
        if self._panic_mode:
            if token._symbol == self._recovery_symbol:
                self._end_recovery_mode()
            elif len(self._stack_states) == 1 and token._symbol in self._current_syncronization_set:
                self._end_recovery_mode()
            else:
                return # type:ignore

        current_action = self._action_table[key]
        # while the action is reduce
        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            if len(self._errors) == 0:
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
            if len(self._errors) == 0:
                # update the stack of ast
                self._stack_ast = self._stack_ast[:-1*len(p._production)] + [new_ast]
            # sets the current state
            state = self._stack_states[-1]
            key = (state,self._stack[-1])
            # checks for an action
            if not key in self._action_table:
                self._start_recovery_mode(self._stack[-1],new_ast._line,new_ast._column)
                break
            current_action = self._action_table[key]
            # checks if the action is shift, due to reductions only may occur at top of the stack
            if current_action[0] != BottomUpParserAction.SHIFT:
                self._start_recovery_mode(self._stack[-1],new_ast._line,new_ast._column)
                break
            # sets the state by the GOTO table and put it at stack of states top
            state = self._goto_table[key]
            self._stack_states.append(state)
            # checks for an action with the current state and the current token
            key = (state,token._symbol)
            if not key in self._action_table:
                self._start_recovery_mode(token._symbol,token._line,token._column)
                break
            # updates the current action
            current_action = self._action_table[key]
        if not self._panic_mode and current_action[0] == BottomUpParserAction.SHIFT:
            state = self._goto_table[key]
            if len(self._errors):
                # adds a new parse tree node to the parse tree
                new_node = ParseTreeNode(token._symbol,token._line,token._column)
                self._parse_tree_nodes.append(new_node)
            # push the symbol in the stack
            self._stack.append(token._symbol)
            if len(self._errors) == 0:
                # push the ast in the stack
                self._stack_ast.append(token)
            # push the state in the stack
            self._stack_states.append(state)
        if not self._panic_mode and current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            if len(self._errors) == 0:
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
        self._errors.clear()
        self._panic_mode = False # type:ignore
        self._current_syncronization_set.clear()
        
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