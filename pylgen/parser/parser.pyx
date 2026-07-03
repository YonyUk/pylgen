import inspect
from typing import Iterable,Callable,List,Tuple,Dict
from ..common.types cimport Token,AST,Symbol
from ..grammar.grammar cimport Production
from ..analisis.error cimport SintaxError
from .bottom_up_parser_actions import BottomUpParserAction

_offset:int = 20

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
    def errors(self) -> List[SintaxError]:
        return self._errors

    cpdef void reset(self):
        raise NotImplementedError()
    
    cpdef void set_draw_parse_tree_flag(self,bint flag):
        self._draw_parse_tree = flag

cdef class BottomUpParser(Parser):

    def __init__(self,str start_state,dict[tuple[str,Symbol],str] goto_table,dict[tuple[str,Symbol],tuple[str,object]] action_table):
        '''
        Args:
            start_state (str): id of the start state for this parser
            goto_table (Dict[Tuple[str,Symbol],str]): GOTO table for the parser
            action_table (Dict[Tuple[str,Symbol],tuple[str,str | Production]]): ACTION table for the parser
            follows (Dict[Symbol,Set[Symbol]]): dict of FOLLOW set by non-terminal
        '''
        cdef int key,state_id,symbol_id
        cdef tuple[str,Symbol] table_key
        self._action_table = action_table
        self._goto_table = goto_table
        self._action_table_optimized = {}
        self._goto_table_optimized = {}
        self._symbols_id = {}

        for table_key in goto_table:
            state_id = int(table_key[0][1:])
            symbol_id = (<Symbol>table_key[1])._hash
            if not symbol_id in self._symbols_id:
                self._symbols_id[symbol_id] = len(self._symbols_id)
                symbol_id = self._symbols_id[symbol_id]
            else:
                symbol_id = self._symbols_id[symbol_id]
            key = (state_id << _offset ) | symbol_id
            self._goto_table_optimized[key] = goto_table[table_key]

        for table_key in action_table:
            state_id = int(table_key[0][1:])
            symbol_id = (<Symbol>table_key[1])._hash
            if not symbol_id in self._symbols_id:
                self._symbols_id[symbol_id] = len(self._symbols_id)
                symbol_id = self._symbols_id[symbol_id]
            else:
                symbol_id = self._symbols_id[symbol_id]
            key = (state_id << _offset ) | symbol_id
            self._action_table_optimized[key] = action_table[table_key]

        self._reductor_by_production = {}
        self._stack_states = [start_state]
        self._stack = []
        self._stack_ast = []
        self._start_state = start_state
        self._parsed = False # type:ignore
        self._parse_tree_nodes = []
        self._errors = []
        self._panic_mode = False # type:ignore
        self._current_syncronization_set = set()
        self._draw_parse_tree = False # type:ignore

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor

    cdef void _start_recovery_mode(self,Symbol symbol,int line, int column):
        cdef Symbol stack_symbol,follow_symbol
        cdef tuple[str,Symbol] key
        cdef set[Symbol] expected_symbols = set()
        cdef SintaxError error
        cdef str state

        for key in self._action_table:
            if key[0] == self._stack_states[-1]:
                follow_symbol = key[1] # type:ignore
                if follow_symbol._is_terminal:
                    expected_symbols.add(follow_symbol)

        error = SintaxError(f'Unexpected symbol "{symbol}"; expected {expected_symbols}',line,column) # type:ignore
        self._errors.append(error)
        self._panic_mode = True # type:ignore
        self._current_syncronization_set = set()
        
        for state in self._stack_states:
            for key in self._action_table:
                if not (<Symbol>key[1])._is_terminal: continue
                if key[0] == state and self._action_table[key][0] == BottomUpParserAction.SHIFT:
                    self._current_syncronization_set.add(key[1]) # type:ignore
        
    cdef void _end_recovery_mode(self,Symbol symbol):
        cdef bint started = False # type:ignore
        self._current_syncronization_set = set()
        self._panic_mode = False # type:ignore
        while self._stack_states:
            key = (self._stack_states[-1],symbol)
            if key in self._action_table and self._action_table[key][0] == BottomUpParserAction.SHIFT:
                started = True # type:ignore
                break
            if started:
                break
            self._stack_states.pop()
            self._stack_ast.pop()
            self._stack.pop()

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef str state
        cdef int key
        cdef AST new_ast
        cdef ParseTreeNode new_node
        cdef list[ParseTreeNode] childrens
        cdef int production_len
        # local references for micro-optimizations
        cdef list[str] local_stack_states = self._stack_states
        cdef dict[int,tuple[str,object]] local_action_table = self._action_table_optimized
        cdef dict[Production,object] local_reductor_by_production = self._reductor_by_production
        cdef list[Symbol] local_stack = self._stack
        cdef list[AST] local_stack_ast = self._stack_ast
        cdef dict[int,str] local_goto_table = self._goto_table_optimized
        cdef list[ParseTreeNode] local_parse_tree_nodes = self._parse_tree_nodes
        cdef bint draw_parse_tree_flag = self._draw_parse_tree
        cdef bint errors = len(self._errors) > 0 # type:ignore
        cdef dict[int,int] local_symbols_ids = self._symbols_id
        cdef int symbol_id

        if self._parsed:
            raise ValueError('EOF token already readed')
        
        if self._panic_mode:
            if token._symbol in self._current_syncronization_set:
                self._end_recovery_mode(token._symbol)
            else:
                return # type:ignore
        
        state = local_stack_states[-1]
        symbol_id = local_symbols_ids[(<Symbol>token._symbol)._hash]

        key = (int(state[1:]) << _offset) | symbol_id

        current_action = local_action_table.get(key,('',None))
        # input(current_action)
        if current_action == ('',None):
            self._start_recovery_mode(token._symbol,token._line,token._column)
            return # type:ignore

        # while the action is reduce
        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            production_len = len(p._production)
            new_ast = local_reductor_by_production[p](local_stack_ast[-1*production_len:]) # type:ignore
            if not errors and draw_parse_tree_flag:
                # build the parse tree
                childrens = local_parse_tree_nodes[-1*production_len:]
                new_node = ParseTreeNode(p._head,new_ast._line,new_ast._column,childrens)
                # updates the stack of parse tree nodes
                del local_parse_tree_nodes[-1*production_len:]
                local_parse_tree_nodes.append(new_node)
            # update the stack of symbols
            del local_stack[-1*production_len:]
            local_stack.append(p._head)
            # update the stack of states
            del local_stack_states[-1*production_len:]
            # update the stack of ast
            del local_stack_ast[-1*production_len:]
            local_stack_ast.append(new_ast)
            # sets the current state
            state = local_stack_states[-1]
            symbol_id = local_symbols_ids[(<Symbol>local_stack[-1])._hash]

            key = (int(state[1:]) << _offset) | symbol_id
            current_action = local_action_table.get(key,('',None))
            # checks for an action
            if current_action == ('',None):
                self._start_recovery_mode(local_stack[-1],new_ast._line,new_ast._column)
                break
            # checks if the action is shift, due to reductions only may occur at top of the stack
            if current_action[0] != BottomUpParserAction.SHIFT:
                self._start_recovery_mode(local_stack[-1],new_ast._line,new_ast._column)
                break
            # sets the state by the GOTO table and put it at stack of states top
            state = local_goto_table[key]
            local_stack_states.append(state)
            symbol_id = local_symbols_ids[(<Symbol>token._symbol)._hash]
            # checks for an action with the current state and the current token
            key = (int(state[1:]) << _offset ) | symbol_id
            current_action = local_action_table.get(key,('',None))
            if current_action == ('',None):
                self._start_recovery_mode(token._symbol,token._line,token._column)
                break
        if not self._panic_mode and current_action[0] == BottomUpParserAction.SHIFT:
            state = local_goto_table[key]
            if not errors and draw_parse_tree_flag:
                # adds a new parse tree node to the parse tree
                new_node = ParseTreeNode(token._symbol,token._line,token._column)
                local_parse_tree_nodes.append(new_node)
            # push the symbol in the stack
            local_stack.append(token._symbol)
            # push the ast in the stack
            local_stack_ast.append(token)
            # push the state in the stack
            local_stack_states.append(state)
        if not self._panic_mode and current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            if not errors:
                self._ast = local_stack_ast[-1]
                if draw_parse_tree_flag:
                    self._parse_tree = local_parse_tree_nodes[-1]
        self._stack = local_stack
        self._stack_states = local_stack_states
        self._stack_ast = local_stack_ast
        self._parse_tree_nodes = local_parse_tree_nodes

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