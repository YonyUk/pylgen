from typing import Callable,Any,Tuple,Set

from common.types import Symbol
from automaton.automaton import DFA,State
from .base_lexer import BaseLexer
from analisis.lexical import LexicRule
from analisis.error import LexicError

class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA) -> None: ...

    @property
    def errors(self) -> Set[LexicError]: ...

    def __setitem__(self, key: Tuple[int, object], re:str): ... # type:ignore

    def add_rule(self,type_:Any,rule:LexicRule): ...