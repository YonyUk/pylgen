from typing import List

from pylgen.common.types import AST,Symbol,ErrorAST,SemanticError, Token
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

    def __init__(self, left:AST,right:AST,symbol: Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        super().__init__(symbol,sl,sc,el,ec)
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

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,plus)

class MinusAST(BinaryAST):

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,minus)

class ModAST(BinaryAST):

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,mod)

class ModuleByZeroErrorAST(ErrorAST):

    def __init__(self,left:AST,right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        errors = {SemanticError('module by zero not allowed',sl,sc,el,ec)}
        super().__init__(mod_error,sl,sc,el,ec,errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]

class ModuleByNotIntegerErrorAST(ErrorAST):

    def __init__(self,left:AST,right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position 
        errors = {SemanticError('module by a non-integer not allowed',sl,sc,el,ec)}
        super().__init__(mod_error,sl,sc,el,ec,errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]


class MulAST(BinaryAST):

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,mul)

class DivAST(BinaryAST):

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,div)

class DivisionByZeroErrorAST(ErrorAST):

    def __init__(self,left:AST,right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        errors = {SemanticError('division by zero not allowed',sl,sc,el,ec)}
        super().__init__(div_error,sl,sc,el,ec,errors)
        self._left = left
        self._right = right

    def children(self) -> List[AST]:
        return [self._left,self._right]

class ExpAST(BinaryAST):

    def __init__(self, left:AST,right:AST):
        super().__init__(left,right,exp)

class AssignmentAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, eq)

    def children(self) -> List[AST]:
        return [self._right]

class VarAST(AST):

    def __init__(self,token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(variable,sl,sc,el,ec)
        self._name = token.text

    @property
    def name(self) -> str:
        return self._name

    def children(self) -> List[AST]:
        return []

class ExitAST(AST):

    def __init__(self,start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(exit, start_line,start_column,end_line,end_column)

    def children(self) -> List[AST]:
        return []

class ClearAST(AST):

    def __init__(self,start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(clear, start_line,start_column,end_line,end_column)

    def children(self) -> List[AST]:
        return []