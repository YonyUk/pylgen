from pylgen.common.types import AST,ASTListView,Token
from .grammar_symbols import (
    minus,
    plus,
    mul,
    div,
    exp,
    mod,
    eq,
    variable,
    number
)
from .asts import (
    ClearAST,
    PlusAST,
    MinusAST,
    MulAST,
    DivAST,
    ExpAST,
    ModAST,
    VarAST,
    AssignmentAST,
    ExitAST,
    DivisionByZeroErrorAST,
    ModuleByNotIntegerErrorAST,
    ModuleByZeroErrorAST
)

def binary_reductor(asts:ASTListView) -> AST:
    ast_type:type = None  # type: ignore
    if asts[1].symbol == plus:
        ast_type = PlusAST
    elif asts[1].symbol == minus:
        ast_type = MinusAST
    elif asts[1].symbol == mul:
        ast_type = MulAST
    elif asts[1].symbol == div:
        right = asts[2]
        if isinstance(right,Token) and float(right.text) == 0:
            return DivisionByZeroErrorAST(asts[0],asts[2])
        ast_type = DivAST
    elif asts[1].symbol == exp:
        ast_type = ExpAST
    elif asts[1].symbol == mod:
        right = asts[2]
        if isinstance(right,Token):
            if float(right.text) == 0:
                return ModuleByZeroErrorAST(asts[0],asts[2])
            if '.' in right.text:
                return ModuleByNotIntegerErrorAST(asts[0],asts[2])
        ast_type = ModAST
    elif asts[1].symbol == eq:
        ast_type = AssignmentAST
    else:
        raise ValueError()
    return ast_type(asts[0],asts[2])

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def parenthesis_reductor(asts:ASTListView) -> AST:
    asts[1].start_position = asts[0].start_position
    asts[1].end_position = asts[2].end_position
    return asts[1]

def variable_reductor(asts:ASTListView) -> AST:
    return VarAST(asts[0]) # type: ignore

def exit_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    return ExitAST(sl,sc,el,ec)

def clear_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    return ClearAST(sl,sc,el,ec)