from typing import List

from pylgen.common.types import ErrorAST,AST, Symbol
from errors.errors import *

from .symbols import div,mod

class OperationNotSupportedForTypesErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST, symbol: Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        error = OperationNotSupportedForTypesError(left.symbol.symbol,right.symbol.symbol,symbol.symbol,sl,sc,el,ec)
        super().__init__(symbol, sl,sc,el,ec, {error})
        self._left = left
        self._right = right

    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

class OperationNotSupportedForTypeErrorAST(ErrorAST):

    def __init__(self, target:AST, symbol: Symbol, start_line: int, start_column: int, end_line:int,end_column:int):
        error = OperationNotSupportedForTypeError(target.symbol.symbol,symbol.symbol,start_line,start_column,end_line,end_column)
        super().__init__(symbol, start_line,start_column,end_line,end_column, {error})
        self._target = target

    @property
    def target(self) -> AST:
        return self._target

class DivisionByLiteralZeroErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        error = DivisionByZeroError(sl,sc,el,ec)
        super().__init__(div, sl,sc,el,ec, {error})
        self._left = left
        self._right = right
        self._children = [left,right]

    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

    def children(self) -> List[AST]:
        return self._children

class ModuleByLiteralZeroErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        error = ModuleByZeroError(sl,sc,el,ec)
        super().__init__(mod,sl,sc,el,ec, {error})
        self._left = left
        self._right = right
        self._children = [left,right]

    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

    def children(self) -> List[AST]:
        return self._children

class ModuleWithComplexErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        error = ModuleWithComplexError(sl,sc,el,ec)
        super().__init__(mod, sl,sc,el,ec, {error})
        self._left = left
        self._right = right
        self._children = [left,right]

    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

    def children(self) -> List[AST]:
        return self._children