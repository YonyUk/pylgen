from typing import List, Set

from pylgen.analysis.error import SemanticError
from pylgen.common.types import ErrorAST,AST, Symbol
from errors.errors import *

from .symbols import div,mod

class OperationNotSupportedForTypesErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST, symbol: Symbol, line: int, column: int):
        error = OperationNotSupportedForTypesError(left.symbol.symbol,right.symbol.symbol,symbol.symbol,line,column)
        super().__init__(symbol, line, column, {error})
        self._left = left
        self._right = right

    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

class OperationNotSupportedForTypeErrorAST(ErrorAST):

    def __init__(self, target:AST, symbol: Symbol, line: int, column: int):
        error = OperationNotSupportedForTypeError(target.symbol.symbol,symbol.symbol,line,column)
        super().__init__(symbol, line, column, {error})
        self._target = target

    @property
    def target(self) -> AST:
        return self._target

class DivisionByLiteralZeroErrorAST(ErrorAST):

    def __init__(self, left:AST, right:AST, line: int, column: int):
        super().__init__(div, line, column, {DivisionByZeroError(line,column)})
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

    def __init__(self, left:AST, right:AST, line: int, column: int):
        super().__init__(mod, line, column, {ModuleByZeroError(line,column)})
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

    def __init__(self, left:AST, right:AST, line: int, column: int):
        super().__init__(mod, line, column, {ModuleWithComplexError(line,column)})
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