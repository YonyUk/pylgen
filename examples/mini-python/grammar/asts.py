from typing import List

from pylgen.common.types import AST, Symbol,Token

from .symbols import *

class VariableAST(AST):

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(Variable,sl,sc,el,ec)
        self._name = token.text
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    def children(self) -> List[AST]:
        return self._children

class UnaryAST(AST):

    def __init__(self, operator:Token,child:AST,symbol: Symbol):
        (sl,sc),(el,ec) = operator.start_position,child.end_position
        super().__init__(symbol, sl,sc,el,ec)
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

    def __init__(self, operator: Token, child: AST):
        super().__init__(operator, child, MathExpr)

class NotBoolExprAST(UnaryAST):

    def __init__(self, operator: Token, child: AST):
        super().__init__(operator, child, BoolExpr)

class BinaryAST(AST):

    def __init__(self, left:AST, right:AST, symbol: Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        super().__init__(symbol, sl,sc,el,ec)
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

    def __init__(self, left: AST, right: AST, symbol: Symbol):
        super().__init__(left, right, symbol)

    @property
    def variable(self) -> VariableAST:
        return self._left # type: ignore

class AssignAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, assign)

    @property
    def target(self) -> VariableAST:
        return self._left # type: ignore

class BitOrAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, bit_or)

class BitAndAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, bit_and)

class OrAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, or_op)

class AndAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, and_op)

class PlusAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, plus)

class MinusAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, minus)

class MulAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, mul)

class DivAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, div)

class IntDivAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, int_div)

class ModAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, mod)

class PowAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, power)

class EqAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, eq)

class NeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, neq)

class LeAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, le)

class GeAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, ge)

class LeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, leq)

class GeqAST(BinaryAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, geq)

class PlusEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, plus_eq)

class MinusEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, minus_eq)

class MulEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, mul_eq)

class DivEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, div_eq)

class IntDivEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, int_div_eq)

class PowEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, power_eq)

class ModEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, mod_eq)

class BitOrEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, bit_or_eq)    

class BitAndEqAST(BinaryAssignAST):

    def __init__(self, left: AST, right: AST):
        super().__init__(left, right, bit_and_eq)

class NumberAST(AST):

    def __init__(self, token:Token, value_type:type):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(Number,sl,sc,el,ec)
        self._value = token.text
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

    def __init__(self, args:List[AST], start_line:int, start_column:int, end_line:int, end_column:int):
        super().__init__(FuncCallArgs,start_line,start_column,end_line,end_column)
        self._args = args

    @property
    def args(self) -> List[AST]:
        return self._args

    def children(self) -> List[AST]:
        return self._args

class FuncCallAST(AST):

    def __init__(self, token:Token, args:FuncCallArgsAST):
        (sl,sc),(el,ec) = token.start_position,args.end_position
        super().__init__(FuncCall, sl,sc,el,ec)
        self._func_name = token.text
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

    def __init__(self, instruction:AST):
        (sl,sc),(el,ec) = instruction.start_position,instruction.end_position
        super().__init__(PythonInstruction,sl,sc,el,ec)
        self._instruction = instruction
        self._children = [instruction]

    @property
    def instruction(self) -> AST:
        return self._instruction

    def children(self) -> List[AST]:
        return self._children

class InstructionsAST(AST):

    def __init__(self, instructions:List[InstructionAST], start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(PythonInstructions, start_line,start_column,end_line,end_column)
        self._instructions = instructions

    @property
    def instructions(self) -> List[InstructionAST]:
        return self._instructions

    def children(self) -> List[AST]:
        return self._instructions # type: ignore

class BooleanAST(AST):

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(Boolean, sl,sc,el,ec)
        self._val = token.text
        self._children = []

    @property
    def val(self) -> str:
        return self._val

    def children(self) -> List[AST]:
        return self._children

class StringAST(AST):

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(String, sl,sc,el,ec)
        self._value = token.text
        self._children = []

    @property
    def value(self) -> str:
        return self._value[1:-1]

    def children(self) -> List[AST]:
        return self._children

class IfBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST]):
        (sl,sc),(el,ec) = instructions[0].start_position,instructions[-1].end_position
        AST.__init__(self,IfBody,sl,sc,el,ec)
        self._instructions = instructions

class ElseBodyAST(InstructionsAST):

    def __init__(self, instructions: List[InstructionAST]):
        (sl,sc),(el,ec) = instructions[0].start_position,instructions[-1].end_position
        AST.__init__(self,ElseBody,sl,sc,el,ec)
        self._instructions = instructions

class IfAST(AST):

    def __init__(self, condition:AST, body:IfBodyAST, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(IfSmt, start_line,start_column,end_line,end_column)
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

    def __init__(self, condition: AST, body: IfBodyAST, start_line: int, start_column: int, end_line:int, end_column:int):
        AST.__init__(self,InnerIfSmt,start_line,start_column,end_line,end_column)
        self._condition = condition
        self._body = body
        self._children = [condition,body]

class IfElifAST(AST):

    def __init__(self, conditionals:List[InnerIfAST]):
        (sl,sc),(el,ec) = conditionals[0].start_position,conditionals[-1].end_position
        super().__init__(IfElifSmt,sl,sc,el,ec)
        self._conditionals = conditionals

    @property
    def conditionals(self) -> List[InnerIfAST]:
        return self._conditionals

    def children(self) -> List[AST]:
        return self._conditionals # type: ignore

class IfElseAST(AST):

    def __init__(self, condition:AST, ifbody:IfBodyAST, elsebody:ElseBodyAST,start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(IfElseSmt,start_line,start_column,end_line,end_column)
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

    def __init__(self, conditionals: List[InnerIfAST],elsebody:ElseBodyAST):
        (sl,sc),(el,ec) = conditionals[0].start_position,elsebody.end_position
        AST.__init__(self,IfElifElseSmt,sl,sc,el,ec)
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

    def __init__(self, instructions: List[InstructionAST]):
        (sl,sc),(el,ec) = instructions[0].start_position,instructions[-1].end_position
        AST.__init__(self,WhileBody,sl,sc,el,ec)
        self._instructions = instructions

class WhileAST(AST):

    def __init__(self, condition:AST, instructions:WhileBodyAST, start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(WhileSmt,start_line,start_column,end_line,end_column)
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

    def __init__(self, instructions: List[InstructionAST]):
        (sl,sc),(el,ec) = instructions[0].start_position,instructions[-1].end_position
        AST.__init__(self,FuncBody,sl,sc,el,ec)
        self._instructions = instructions

class FuncArgsAST(AST):

    def __init__(self, args:List[VariableAST],start_line:int,start_column:int,end_line:int,end_column:int):
        super().__init__(FuncArgs, start_line,start_column,end_line,end_column)
        self._args = args

    @property
    def args(self) -> List[VariableAST]:
        return self._args

    def children(self) -> List[AST]:
        return self._args # type: ignore

class FuncDefAST(AST):

    def __init__(self, func_name:str,args:FuncArgsAST,body:FuncBodyAST, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(FuncDef, start_line,start_column,end_line,end_column)
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

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(VoidReturnSmt, sl,sc,el,ec)
        self._children = []

    def children(self) -> List[AST]:
        return self._children

class ReturnAST(VoidReturnAST):

    def __init__(self, token:Token,instruction:AST):
        (sl,sc),(el,ec) = token.start_position,instruction.end_position
        AST.__init__(self,ReturnSmt,sl,sc,el,ec)
        self._instruction = instruction
        self._children = [instruction]

    @property
    def instruction(self) -> AST:
        return self._instruction

    def children(self) -> List[AST]:
        return self._children

class BreakAST(AST):

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(break_keyword, sl,sc,el,ec)
        self._children = []

    def children(self) -> List[AST]:
        return self._children

class ContinueAST(AST):

    def __init__(self, token:Token):
        (sl,sc),(el,ec) = token.start_position,token.end_position
        super().__init__(continue_keyword, sl,sc,el,ec)
        self._children = []

    def children(self) -> List[AST]:
        return self._children