from typing import Callable, Dict, Iterable, List, Tuple
from common.types import Token,AST,Symbol
from grammar.grammar import Production

class Parser:

    def parse(self,tokens:Iterable[Token]) -> AST: ...

class BottomUpParser(Parser):

    def __init__(self,start_state:str,goto_table:Dict[Tuple[str,Symbol],str],action_table:Dict[Tuple[str,Symbol],tuple[str,str | Production]]): ...

    def reset(self) -> None: ...

    def __setitem__(self,production:Production,reductor:Callable[[List[AST]],AST]): ...