# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
import inspect
from typing import Iterable,Callable,List
from ..common.types cimport Token,AST,Symbol,ASTListView,ErrorAST
from ..grammar.grammar cimport Production
from ..analysis.error cimport SyntaxError,SemanticError
from .bottom_up_parser_actions import BottomUpParserAction

_offset:int = 32

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
            return self._ast
        return None # type:ignore

    cdef void _try_parse(self,Token token):
        raise NotImplementedError()
    
    @property
    def parse_tree(self) -> ParseTreeNode:
        '''
        Returns:
            ParseTree: the current parse tree if parsing was successfully
        '''
        if self._parsed:
            if self._syntax_error:
                raise ParsingException('The parsing ended with errors')
            return self._parse_tree
        raise ParsingException('Nothing parsed')
    
    @property
    def errors(self) -> List[Error]:
        return list(self._errors)

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
        cdef unsigned int symbol_id
        cdef long long key,state_id
        cdef tuple[str,Symbol] table_key
        self._action_table = action_table
        self._goto_table = goto_table
        self._action_table_optimized = {}
        self._goto_table_optimized = {}
        self._view = ASTListView()

        for table_key in goto_table:
            state_id = int(table_key[0][1:])
            symbol_id = (<Symbol>table_key[1])._hash & 0xFFFFFFFF
            key = (state_id << _offset ) | symbol_id
            self._goto_table_optimized[key] = int(goto_table[table_key][1:])

        for table_key in action_table:
            state_id = int(table_key[0][1:])
            symbol_id = (<Symbol>table_key[1])._hash & 0xFFFFFFFF
            key = (state_id << _offset ) | symbol_id
            self._action_table_optimized[key] = action_table[table_key]

        self._reductor_by_production = {}
        self._stack_states = [int(start_state[1:])]
        self._stack = []
        self._stack_ast = []
        self._start_state = start_state
        self._parsed = False # type:ignore
        self._parse_tree_nodes = []
        self._errors = set()
        self._panic_mode = False # type:ignore
        self._current_syncronization_set = set()
        self._draw_parse_tree = False # type:ignore
        self._view._data = self._stack_ast
        self._stack_top = 0
        self._stack_len = 0
        self._stack_ast_len = 0
        self._stack_ast_top = 0
        self._stack_states_len = 1
        self._stack_states_top = 1
        self._syntax_error = False # type:ignore

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[(<Production>production)._hash] = reductor

    cdef void _start_recovery_mode(self,Symbol symbol,int line, int column):
        cdef Symbol stack_symbol,follow_symbol
        cdef tuple[str,Symbol] key
        cdef set[Symbol] expected_symbols = set()
        cdef SyntaxError error
        cdef int state
        cdef int idx

        self._syntax_error = True # type:ignore

        for key in self._action_table:
            if int(key[0][1:]) == self._stack_states[self._stack_states_top - 1]:
                follow_symbol = key[1] # type:ignore
                if follow_symbol._is_terminal:
                    expected_symbols.add(follow_symbol)

        error = SyntaxError(f'Unexpected symbol "{symbol}"; expected {expected_symbols}',line,column) # type:ignore
        self._errors.add(error)
        self._panic_mode = True # type:ignore
        self._current_syncronization_set = set()
        
        for idx in range(self._stack_states_top):
            state = self._stack_states[idx]
            for key in self._action_table: # type:ignore
                if not (<Symbol>key[1])._is_terminal: continue
                if int(key[0][1:]) == state and self._action_table[key][0] == BottomUpParserAction.SHIFT: # type:ignore
                    self._current_syncronization_set.add(key[1]) # type:ignore
        
    cdef void _end_recovery_mode(self,Symbol symbol):
        cdef bint started = False # type:ignore
        cdef tuple[str,Symbol] key

        self._current_syncronization_set = set()
        self._panic_mode = False # type:ignore
        while self._stack_states_top > 0:
            key = (f'I{self._stack_states[self._stack_states_top - 1]}',symbol)
            if key in self._action_table and self._action_table[key][0] == BottomUpParserAction.SHIFT:
                started = True # type:ignore
                break
            if started:
                break
            self._stack_states_top -= 1
            self._stack_ast_top -= 1
            self._stack_top -= 1

    cdef void _try_parse(self,Token token):
        cdef tuple[str,object] current_action
        cdef long long state
        cdef long long key
        cdef AST new_ast
        cdef ParseTreeNode new_node
        cdef list[ParseTreeNode] childrens
        cdef int production_len
        # local references for micro-optimizations
        cdef unsigned int symbol_id
        cdef set[SemanticError] errors
        cdef Symbol token_symbol = token._symbol
        cdef Symbol stack_top_symbol

        if self._parsed:
            raise ValueError('EOF token already readed')
        
        if self._panic_mode:
            if token._symbol in self._current_syncronization_set:
                self._end_recovery_mode(token._symbol)
            else:
                return # type:ignore

        state = self._stack_states[self._stack_states_top - 1]
        symbol_id = token_symbol._hash & 0xFFFFFFFF

        key = (state << _offset) | symbol_id

        current_action = self._action_table_optimized.get(key,None)
        if current_action is None:
            self._start_recovery_mode(token._symbol,token._line,token._column)
            return # type:ignore

        # while the action is reduce
        while current_action[0] == BottomUpParserAction.REDUCE:
            p:Production = current_action[1] # type:ignore
            production_len = len(p._production)
            self._view._end = self._stack_ast_top
            self._view._start = self._stack_ast_top - production_len
            new_ast = self._reductor_by_production[p._hash](self._view) # type:ignore
            if new_ast._is_error:
                errors = (<ErrorAST>new_ast)._errors
                self._errors.update(errors)
            if not self._syntax_error and self._draw_parse_tree:
                # build the parse tree
                childrens = self._parse_tree_nodes[-1*production_len:]
                new_node = ParseTreeNode(p._head,new_ast._line,new_ast._column,childrens)
                # updates the stack of parse tree nodes
                del self._parse_tree_nodes[-1*production_len:]
                self._parse_tree_nodes.append(new_node)
            
            # update the stack of symbols
            self._stack_top -= production_len
            self._stack[self._stack_top] = p._head
            self._stack_top += 1

            # update the stack of states
            self._stack_states_top -= production_len
            # update the stack of ast
            self._stack_ast_top -= production_len
            self._stack_ast[self._stack_ast_top] = new_ast
            self._stack_ast_top += 1

            # sets the current state
            state = self._stack_states[self._stack_states_top - 1]
            stack_top_symbol = self._stack[self._stack_top - 1]
            symbol_id = stack_top_symbol._hash & 0xFFFFFFFF

            key = (state << _offset) | symbol_id
            current_action = self._action_table_optimized.get(key,None)
            
            # checks for an action
            if not current_action:
                self._stack_states_top = self._stack_states_top
                self._stack_ast_top = self._stack_ast_top
                self._stack_top = self._stack_top
                self._start_recovery_mode(self._stack[self._stack_top - 1],new_ast._line,new_ast._column)
                break
            
            # checks if the action is shift, due to reductions only may occur at top of the stack
            if current_action[0] != BottomUpParserAction.SHIFT:
                self._stack_states_top = self._stack_states_top
                self._stack_ast_top = self._stack_ast_top
                self._stack_top = self._stack_top
                self._start_recovery_mode(self._stack[self._stack_top - 1],new_ast._line,new_ast._column)
                break
            # sets the state by the GOTO table and put it at stack of states top
            state = self._goto_table_optimized[key]
            self._stack_states[self._stack_states_top] = state
            self._stack_states_top += 1
            symbol_id = token_symbol._hash & 0xFFFFFFFF
            # checks for an action with the current state and the current token
            key = (state << _offset ) | symbol_id
            current_action = self._action_table_optimized.get(key,None)
            if not current_action:
                self._stack_states_top = self._stack_states_top
                self._stack_ast_top = self._stack_ast_top
                self._stack_top = self._stack_top
                self._start_recovery_mode(token._symbol,token._line,token._column)
                break
            
        
        if not self._panic_mode and current_action[0] == BottomUpParserAction.SHIFT:
            state = self._goto_table_optimized[key]
            if not self._syntax_error and self._draw_parse_tree:
                # adds a new parse tree node to the parse tree
                new_node = ParseTreeNode(token._symbol,token._line,token._column)
                self._parse_tree_nodes.append(new_node)
            # push the symbol in the stack
            if self._stack_top >= self._stack_len:
                self._stack.append(token._symbol)
                self._stack_len += 1
            else:
                self._stack[self._stack_top] = token._symbol
            self._stack_top += 1
            # push the ast in the stack
            if self._stack_ast_top >= self._stack_ast_len:
                self._stack_ast.append(token)
                self._stack_ast_len += 1
            else:
                self._stack_ast[self._stack_ast_top] = token
            self._stack_ast_top += 1
            # push the state in the stack
            if self._stack_states_top >= self._stack_states_len:
                self._stack_states.append(state)
                self._stack_states_len += 1
            else:
                self._stack_states[self._stack_states_top] = state
            self._stack_states_top += 1
        
        if not self._panic_mode and current_action[0] == BottomUpParserAction.ACCEPT:
            self._parsed = True # type:ignore
            if not self._syntax_error:
                self._ast = self._stack_ast[self._stack_ast_top - 1]
                if self._draw_parse_tree:
                    self._parse_tree = self._parse_tree_nodes[len(self._parse_tree_nodes) - 1]

    cpdef void reset(self):
        '''
        Description:
            reset the parser to it's initial state to parse tokens again 
        '''
        self._parsed = False # type:ignore
        self._parse_tree = None # type:ignore
        self._ast = None # type:ignore
        self._stack_top = 0
        self._stack_ast_top = 0
        self._stack_states_top = 1
        self._stack_states[0] = int(self._start_state[1:])
        self._errors.clear()
        self._panic_mode = False # type:ignore
        self._current_syncronization_set.clear()
        self._syntax_error = False # type:ignore
        
    def __setitem__(self,production:Production,reductor:Callable[[ASTListView],AST]):
        sig = inspect.signature(reductor)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise ValueError('invalid reductor function signature')
        if not params[0].annotation is inspect.Parameter.empty and params[0].annotation != ASTListView:
            raise ValueError('invalid reductor function signature')
        if sig.return_annotation != AST:
            raise ValueError('invalid reductor function signature')
        self._set_reductor(production,reductor)