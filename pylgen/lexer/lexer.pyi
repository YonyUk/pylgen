from typing import Callable,Any,Tuple,Set

from ..common.types import Symbol
from ..automaton.automaton import DFA
from ..analysis.lexical import LexicalRule
from ..analysis.error import LexicalError
from .base_lexer import BaseLexer

class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA,check_annotation:bool=True) -> None: ...

    @property
    def errors(self) -> Set[LexicalError]: ...

    def __setitem__(self, key: Tuple[int, object], re:str): ... # type:ignore

    def add_rule(self,type_:Any,rule:LexicalRule): ...

    def clear_errors(self) -> None: ...

    def set_eof_token(self,symbol:str,type_:object) -> None: ...