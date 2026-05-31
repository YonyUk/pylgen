from typing import Any, Callable, Tuple

from automaton.automaton import Automaton,DFA
from common.types import Symbol, Token
from common.enums import TokenType

class LexerNotInitializedException(Exception):
    pass

class LexerNotTokensProvidedException(Exception):
    pass

class BaseLexer:

    def __init__(self,get_symbol_function:Callable[[Any,str],Symbol]) -> None: ...

    @property
    def dfa(self) -> DFA: ...

    def load_text(self,text:str): ...

    def initialize(self): ...