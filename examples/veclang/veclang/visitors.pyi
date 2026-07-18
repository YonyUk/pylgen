from typing import Any, Tuple,List

from pylgen.analisis.visitor import ASTWalker
from pylgen.analisis.error import RuntimeError
from pylgen.analisis.context import Context
from pylgen.common.types import AST

class VecLangContext(Context):

    def __init__(self) -> None: ...

    def get_runtime_errors(self) -> List[RuntimeError]: ...
    
    def clear_runtime_errors(self) -> None: ...

def build_walkers() -> Tuple[VecLangContext,ASTWalker,ASTWalker,ASTWalker]: ...

def get_ast_value(ast:AST, context:VecLangContext) -> Any: ...