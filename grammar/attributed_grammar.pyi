from typing import List,Callable

from common.types import Symbol

class AttributedProduction:

    def __init__(self,head:Symbol,production:List[Symbol],reductor:Callable): ...
    
    @property
    def head(self) -> Symbol: ...
    
    @property
    def production(self) -> List[Symbol]: ...
    
    @property
    def reductor(self) -> Callable: ...
    
    def __str__(self) -> str: ...
    
    def __repr__(self) -> str: ...