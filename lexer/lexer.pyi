from typing import Callable,Any,Tuple

from common.types import Symbol
from automaton.automaton import DFA,State
from .base_lexer import BaseLexer

class Lexer(BaseLexer):
    
    def __init__(self, get_symbol_function: Callable[[Any, str], Symbol], ignore_pattern: DFA) -> None: ...

    def __setitem__(self, key: Tuple[int, object], re:str): ... # type:ignore