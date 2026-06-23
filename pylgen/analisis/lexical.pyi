from .error import LexicError
from ..common.types import Token

class LexicRule:
    
    def __init__(self,msg:str) -> None: ...

    def _check(self, text:str): ...

    def check(self,token:Token) -> LexicError: ...