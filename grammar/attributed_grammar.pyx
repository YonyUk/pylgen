from typing import List,Callable

from common.types cimport Symbol

cdef class AttributedProduction:
    '''
    class that represents an attributed production from an attributed grammar
    '''

    def __init__(self,Symbol head,list[Symbol] production,object reductor):
        '''
        Args:
            head (Symbol): symbol that produces the given production
            production (List[Symbol]):
            reductor (Callable): attribute of the production
        
        Raises:
            ValueError("head symbol can't be a terminal symbol")
        '''
        if head._is_terminal:
            raise ValueError("head symbol can't be a terminal symbol")
        self._head = head
        self._production = production
        self._reductor = reductor
    
    @property
    def head(self) -> Symbol:
        return self._head
    
    @property
    def production(self) -> List[Symbol]:
        return self._production
    
    @property
    def reductor(self) -> Callable:
        return self._reductor # type:ignore
    
    def __str__(self) -> str:
        cdef Symbol symbol
        cdef list[str] production = [symbol._symbol for symbol in self._production]
        return f'{self._head} -> {",".join(production)}'
    
    def __repr__(self) -> str:
        return str(self)