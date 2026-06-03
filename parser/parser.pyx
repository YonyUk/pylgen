import inspect
from typing import Iterable,Callable,List
from common.types cimport Token,AST,Symbol
from grammar.grammar cimport Production

cdef class Parser:

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
        
        return self._ast

    cdef void _try_parse(self,Token token):
        raise NotImplementedError()

cdef class BottomUpParser(Parser):

    def __init__(self,dict[tuple[str,Symbol],str] goto_table,dict[tuple[str,Symbol],tuple[str,object]] action_table):
        self._action_table = action_table
        self._goto_table = goto_table
        self._reductor_by_production = {}

    cdef void _set_reductor(self,Production production,object reductor): # type:ignore
        self._reductor_by_production[production] = reductor
    
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