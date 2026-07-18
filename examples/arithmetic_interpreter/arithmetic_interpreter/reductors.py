from typing import List

from pylgen.common.types import AST,ASTListView
from .grammar_symbols import (
    minus,
    plus,
    mul,
    div,
    exp,
    mod,
    eq
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
    AssigmentAST,
    ExitAST
)

def binary_reductor(asts:ASTListView) -> AST:
    ast_type:type = None  # type: ignore
    if asts[1].symbol == plus:
        ast_type = PlusAST
    if asts[1].symbol == minus:
        ast_type = MinusAST
    if asts[1].symbol == mul:
        ast_type = MulAST
    if asts[1].symbol == div:
        ast_type = DivAST
    if asts[1].symbol == exp:
        ast_type = ExpAST
    if asts[1].symbol == mod:
        ast_type = ModAST
    if asts[1].symbol == eq:
        ast_type = AssigmentAST
    return ast_type(asts[0],asts[2],asts[1].line,asts[1].column)

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def parenthesis_reductor(asts:ASTListView) -> AST:
    return asts[1]

def variable_reductor(asts:ASTListView) -> AST:
    return VarAST(asts[0].text,asts[0].line,asts[0].column) # type: ignore

def exit_reductor(asts:ASTListView) -> AST:
    return ExitAST(asts[0].line,asts[0].column)

def clear_reductor(asts:ASTListView) -> AST:
    return ClearAST(asts[0].line,asts[0].column)