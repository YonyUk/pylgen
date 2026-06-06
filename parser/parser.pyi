from typing import Callable, Dict, Iterable, List, Tuple
from common.types import Token,AST,Symbol
from grammar.grammar import Production

class ParseTreeNode:

    def __init__(self,symbol:Symbol,line:int,column:int,childrens:List[ParseTreeNode]=[]): ...
    
    @property
    def symbol(self) -> Symbol: ...
    
    @property
    def line(self) -> int: ...
    
    @property
    def column(self) -> int: ...

    @property
    def childrens(self) -> List[ParseTreeNode]: ...

class Parser:

    def parse(self,tokens:Iterable[Token]) -> AST: ...

    @property
    def parse_tree(self) -> ParseTreeNode: ...

class BottomUpParser(Parser):

    def __init__(self,start_state:str,goto_table:Dict[Tuple[str,Symbol],str],action_table:Dict[Tuple[str,Symbol],tuple[str,str | Production]]): ...

    def reset(self) -> None: ...

    def __setitem__(self,production:Production,reductor:Callable[[List[AST]],AST]): ...