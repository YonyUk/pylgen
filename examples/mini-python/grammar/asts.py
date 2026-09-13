from typing import List

from pylgen.common.types import AST, Symbol,Token

from .symbols import *

class VariableAST(AST):

    def __init__(self, name:str, line: int, column: int):
        super().__init__(Variable, line, column)
        self._name = name
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    def children(self) -> List[AST]:
        return self._children

class UnaryAST(AST):

    def __init__(self, operator:Token,child:AST,symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
        self._child = child
        self._operator = operator
        self._children = [child]

    @property
    def child(self) -> AST:
        return self._child

    @property
    def operator(self) -> Token:
        return self._operator

    @property
    def operator_token(self) -> str:
        return self._operator.text

    def children(self) -> List[AST]:
        return self._children

class MinusMathExprAST(UnaryAST):

    def __init__(self, operator: Token, child: AST, line: int, column: int):
        super().__init__(operator, child, MathExpr, line, column)

class NotBoolExprAST(UnaryAST):

    def __init__(self, operator: Token, child: AST, line: int, column: int):
        super().__init__(operator, child, BoolExpr, line, column)

class BinaryAST(AST):

    def __init__(self, left:AST, right:AST, symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
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

class BinaryAssignAST(BinaryAST):

    def __init__(self, left: AST, right: AST, symbol: Symbol, line: int, column: int):
        super().__init__(left, right, symbol, line, column)

    @property
    def variable(self) -> VariableAST:
        return self._left # type: ignore

class AssignAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, assign, line, column)

    @property
    def target(self) -> VariableAST:
        return self._left # type: ignore

class BitOrAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, bit_or, line, column)

class BitAndAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, bit_and, line, column)

class OrAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, or_op, line, column)

class AndAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, and_op, line, column)

class PlusAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, plus, line, column)

class MinusAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, minus, line, column)

class MulAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, mul, line, column)

class DivAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, div, line, column)

class IntDivAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, int_div, line, column)

class ModAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, mod, line, column)

class PowAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, power, line, column)

class EqAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, eq, line, column)

class NeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, neq, line, column)

class LeAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, le, line, column)

class GeAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, ge, line, column)

class LeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, leq, line, column)

class GeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, geq, line, column)

class PlusEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, plus_eq, line, column)

class MinusEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, minus_eq, line, column)

class MulEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, mul_eq, line, column)

class DivEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, div_eq, line, column)

class IntDivEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, int_div_eq, line, column)

class PowEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, power_eq, line, column)

class ModEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, mod_eq, line, column)

class BitOrEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, bit_or_eq, line, column)    

class BitAndEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, bit_and_eq, line, column)

class NumberAST(AST):

    def __init__(self, value:str, value_type:type, line: int, column: int):
        super().__init__(Number, line, column)
        self._value = value
        self._value_type = value_type
        self._children = []

    @property
    def value(self) -> str:
        return self._value

    @property
    def type(self) -> type:
        return self._value_type

    def children(self) -> List[AST]:
        return self._children

class FuncCallArgsAST(AST):

    def __init__(self, args:List[AST], line: int, column: int):
        super().__init__(FuncCallArgs, line, column)
        self._args = args

    @property
    def args(self) -> List[AST]:
        return self._args

    def children(self) -> List[AST]:
        return self._args

class FuncCallAST(AST):

    def __init__(self, func_name:str, args:FuncCallArgsAST, line: int, column: int):
        super().__init__(FuncCall, line, column)
        self._func_name = func_name
        self._args = args
        self._children = [self._args]

    @property
    def func_name(self) -> str:
        return self._func_name

    @property
    def args(self) -> FuncCallArgsAST:
        return self._args

    def children(self) -> List[AST]:
        return self._children # type: ignore

class InstructionAST(AST):

    def __init__(self, instruction:AST, line: int, column: int):
        super().__init__(PythonInstruction, line, column)
        self._instruction = instruction
        self._children = [instruction]

    @property
    def instruction(self) -> AST:
        return self._instruction

    def children(self) -> List[AST]:
        return self._children

class InstructionsAST(AST):

    def __init__(self, instructions:List[InstructionAST], line: int, column: int):
        super().__init__(PythonInstructions, line, column)
        self._instructions = instructions

    @property
    def instructions(self) -> List[InstructionAST]:
        return self._instructions

    def children(self) -> List[AST]:
        return self._instructions # type: ignore

class BooleanAST(AST):

    def __init__(self, val:str, line: int, column: int):
        super().__init__(Boolean, line, column)
        self._val = val
        self._children = []

    @property
    def val(self) -> str:
        return self._val

    def children(self) -> List[AST]:
        return self._children

class StringAST(AST):

    def __init__(self, value:str, line: int, column: int):
        super().__init__(String, line, column)
        self._value = value
        self._children = []

    @property
    def value(self) -> str:
        return self._value[1:-1]

    def children(self) -> List[AST]:
        return self._children

class IfBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST], line: int, column: int):
        AST.__init__(self,IfBody,line,column)
        self._instructions = instructions

class ElseBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST], line: int, column: int):
        AST.__init__(self,ElseBody,line,column)
        self._instructions = instructions

class IfAST(AST):

    def __init__(self, condition:AST, body:IfBodyAST, line: int, column: int):
        super().__init__(IfSmt, line, column)
        self._condition = condition
        self._body = body
        self._children = [condition,body]

    @property
    def condition(self) -> AST:
        return self._condition

    @property
    def body(self) -> IfBodyAST:
        return self._body

    def children(self) -> List[AST]:
        return self._children

class InnerIfAST(IfAST):

    def __init__(self, condition: AST, body: IfBodyAST, line: int, column: int):
        AST.__init__(self,InnerIfSmt,line,column)
        self._condition = condition
        self._body = body
        self._children = [condition,body]

class IfElifAST(AST):

    def __init__(self, conditionals:List[InnerIfAST], line: int, column: int):
        super().__init__(IfElifSmt, line, column)
        self._conditionals = conditionals

    @property
    def conditionals(self) -> List[InnerIfAST]:
        return self._conditionals

    def children(self) -> List[AST]:
        return self._conditionals # type: ignore

class IfElseAST(AST):

    def __init__(self, condition:AST, ifbody:IfBodyAST, elsebody:ElseBodyAST, line: int, column: int):
        super().__init__(IfElseSmt, line, column)
        self._condition = condition
        self._if_body = ifbody
        self._else_body = elsebody
        self._children = [condition,ifbody,elsebody]

    @property
    def condition(self) -> AST:
        return self._condition

    @property
    def if_body(self) -> IfBodyAST:
        return self._if_body

    @property
    def else_body(self) -> ElseBodyAST:
        return self._else_body

    def children(self) -> List[AST]:
        return self._children

class IfElifElseAST(IfElifAST):

    def __init__(self, conditionals: List[InnerIfAST],elsebody:ElseBodyAST, line: int, column: int):
        AST.__init__(self,IfElifElseSmt,line,column)
        self._conditionals = conditionals
        self._else_body = elsebody
        self._children = []
        self._children.extend(conditionals)
        self._children.append(elsebody)

    @property
    def else_body(self) -> ElseBodyAST:
        return self._else_body

    def children(self) -> List[AST]:
        return self._children

class WhileBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST], line: int, column: int):
        AST.__init__(self,WhileBody,line,column)
        self._instructions = instructions

class WhileAST(AST):

    def __init__(self, condition:AST, instructions:WhileBodyAST, line: int, column: int):
        super().__init__(WhileSmt, line, column)
        self._condition = condition
        self._instructions = instructions
        self._children = [condition,instructions]

    @property
    def condition(self) -> AST:
        return self._condition

    @property
    def instructions(self) -> WhileBodyAST:
        return self._instructions

    def children(self) -> List[AST]:
        return self._children

class FuncBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST], line: int, column: int):
        AST.__init__(self,FuncBody,line,column)
        self._instructions = instructions

class FuncArgsAST(AST):

    def __init__(self, args:List[VariableAST], line: int, column: int):
        super().__init__(FuncArgs, line, column)
        self._args = args

    @property
    def args(self) -> List[VariableAST]:
        return self._args

    def children(self) -> List[AST]:
        return self._args # type: ignore

class FuncDefAST(AST):

    def __init__(self, func_name:str,args:FuncArgsAST,body:FuncBodyAST, line: int, column: int):
        super().__init__(FuncDef, line, column)
        self._func_name = func_name
        self._body = body
        self._children = [args,body]
        self._args = args

    @property
    def args(self) -> FuncArgsAST:
        return self._args # type: ignore

    @property
    def func_name(self) -> str:
        return self._func_name

    @property
    def body(self) -> FuncBodyAST:
        return self._body

    def children(self) -> List[AST]:
        return self._children # type: ignore

class VoidReturnAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(VoidReturnSmt, line, column)
        self._children = []

    def children(self) -> List[AST]:
        return self._children

class ReturnAST(VoidReturnAST):

    def __init__(self, instruction:AST, line: int, column: int):
        AST.__init__(self,ReturnSmt,line,column)
        self._instruction = instruction
        self._children = [instruction]

    @property
    def instruction(self) -> AST:
        return self._instruction

    def children(self) -> List[AST]:
        return self._children

class BreakAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(break_keyword, line, column)
        self._children = []

    def children(self) -> List[AST]:
        return self._children

class ContinueAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(continue_keyword, line, column)
        self._children = []

    def children(self) -> List[AST]:
        return self._children