from typing import List

from pylgen.common.types import AST

from .grammar_symbols import (
    Config,
    ConfigSequence,
    Section,
    ConfigAtom
)

class ConfigsAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(Config, start_line, start_column,end_line,end_column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSequenceAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigSequence, start_line,start_column,end_line,end_column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSectionAST(AST):

    def __init__(self, section_name:str,start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(Section, start_line,start_column,end_line,end_column)
        self._name = section_name
        self._configs = []

    @property
    def section_name(self) -> str:
        return self._name
    
    def children(self) -> List[AST]:
        return self._configs

class SectionConfigSequenceAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigSequence, start_line,start_column,end_line,end_column)
        self._configs = []

class AtomConfigAST(AST):

    def __init__(self, name:str,value:str | float | bool,start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigAtom, start_line,start_column,end_line,end_column)
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str | float | bool:
        return self._value

    def children(self) -> List[AST]:
        return []