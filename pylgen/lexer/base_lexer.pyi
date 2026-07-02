from typing import Any, Callable, Iterable, Tuple

from ..automaton.automaton import Automaton,DFA
from ..common.types import Symbol, Token

class LexerNotInitializedException(Exception):
    pass

class LexerNotTokensProvidedException(Exception):
    pass

class BaseLexer:

    def __init__(self,get_symbol_function:Callable[[Any,str],Symbol],ignore_pattern:DFA,check_annotation:bool=True) -> None: ...

    @property
    def dfa(self) -> DFA: ...
    @property
    def tokens(self) -> Iterable[Token]: ...
    
    def load_text(self,text:str): ...

    def initialize(self): ...

    def __setitem__(self,key:Tuple[int,object],automaton:Automaton): ...