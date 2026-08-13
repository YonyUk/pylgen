from typing import List

from pylgen.analysis.error import SemanticError
from pylgen.common.types import AST,Symbol,ErrorAST
from .grammar_symbols import (
    clear,
    plus,
    minus,
    mul,
    mod,
    div,
    exp,
    eq,
    variable,
    exit
)

div_error = Symbol('Division SemanticError')
mod_error = Symbol('Module SemanticError')

class BinaryAST(AST):

    def __init__(self, left:AST,right:AST,symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
        self._left:AST = left
        self._right:AST = right

    @property
    def left(self) -> AST:
        return self._left # type:ignore

    @property
    def right(self) -> AST:
        return self._right # type: ignore

    def children(self) -> List[AST]:
        return [self._left,self._right]

class PlusAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,plus, line, column)

class MinusAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,minus, line, column)

class ModAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,mod, line, column)

class ModuleByZeroErrorAST(ErrorAST):

    def __init__(self, line: int, column: int,left:AST,right:AST):
        errors = {SemanticError('module by zero not allowed',line,column)}
        super().__init__(mod_error, line, column, errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]

class ModuleByNotIntegerErrorAST(ErrorAST):

    def __init__(self, line: int, column: int,left:AST,right:AST):
        errors = {SemanticError('module by a non-integer not allowed',line,column)}
        super().__init__(mod_error, line, column, errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]


class MulAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,mul, line, column)

class DivAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,div, line, column)

class DivisionByZeroErrorAST(ErrorAST):

    def __init__(self,line: int, column: int,left:AST,right:AST):
        errors = {SemanticError('division by zero not allowed',line,column)}
        super().__init__(div_error, line, column, errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]

class ExpAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,exp, line, column)

class AssignmentAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, eq, line, column)

    def children(self) -> List[AST]:
        return [self._right]

class VarAST(AST):

    def __init__(self,name:str,line:int,column:int):
        super().__init__(variable,line,column)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def children(self) -> List[AST]:
        return []

class ExitAST(AST):

    def __init__(self,line: int, column: int):
        super().__init__(exit, line, column)

    def children(self) -> List[AST]:
        return []

class ClearAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(clear, line, column)

    def children(self) -> List[AST]:
        return []