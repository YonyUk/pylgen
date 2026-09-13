from pylgen.common.types import ASTListView,AST

from .asts import *
from .error_asts import *

def PythonInstruction_BoolExpr_reductor(asts:ASTListView) -> AST:
    return InstructionAST(asts[0],asts[0].line,asts[0].column)

def Variable_reductor(asts:ASTListView) -> AST:
    token:Token = asts[0] # type: ignore
    return VariableAST(token.text,token.line,token.column)

def Break_reductor(asts:ASTListView) -> AST:
    return BreakAST(asts[0].line,asts[0].column)

def Continue_redutctor(asts:ASTListView) -> AST:
    return ContinueAST(asts[0].line,asts[0].column)

def PythonInstruction_return_keyword_BoolExpr_reductor(asts:ASTListView) -> AST:
    return ReturnAST(asts[1],asts[0].line,asts[0].column)

def PythonInstruction_return_keyword_reductor(asts:ASTListView) -> AST:
    return VoidReturnAST(asts[0].line,asts[0].column)

def PythonInstruction_Variable_assign_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = AssignAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_plus_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = PlusEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_minus_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = MinusEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_mul_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = MulEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_div_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = DivEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_int_div_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = IntDivEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_power_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = PowEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_mod_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = ModEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_bit_or_eq_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = BitOrEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def PythonInstruction_Variable_bit_and_eq_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = BitAndEqAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return InstructionAST(instruction,instruction.line,instruction.column)

def MathExpr_minus_UnaryMathExpr_reductor(asts:ASTListView) -> AST:
    return MinusMathExprAST(asts[0],asts[1],asts[0].line,asts[0].column) # type: ignore

def UnaryBoolExpr_not_op_UnaryBoolExpr_reductor(asts:ASTListView) -> AST:
    return NotBoolExprAST(asts[0],asts[1],asts[0].line,asts[0].column) # type: ignore

def UnaryBoolExpr_lparen_BoolExpr_or_op_BoolTerm1_rparen_reductor(asts:ASTListView) -> AST:
    return OrAST(asts[1],asts[3],asts[2].line,asts[2].column)

def UnaryBoolExpr_lparen_BoolExpr_and_op_BoolTerm1_rparen_reductor(asts:ASTListView) -> AST:
    return AndAST(asts[1],asts[3],asts[2].line,asts[2].column)

def UnaryBoolExpr_lparen_BoolExpr_bit_or_BoolTerm1_rparen_reductor(asts:ASTListView) -> AST:
    return BitOrAST(asts[1],asts[3],asts[2].line,asts[2].column)

def UnaryBoolExpr_lparen_BoolExpr_bit_and_BoolTerm1_rparen_reductor(asts:ASTListView) -> AST:
    return BitAndAST(asts[1],asts[3],asts[2].line,asts[2].column)

def Number_int_number_reductor(asts:ASTListView) -> AST:
    return NumberAST(asts[0].text,int,asts[0].line,asts[0].column) # type: ignore

def Number_float_number_reductor(asts:ASTListView) -> AST:
    return NumberAST(asts[0].text,float,asts[0].line,asts[0].column) # type: ignore

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def parenthesis_reductor(asts:ASTListView) -> AST:
    return asts[1]

def MathExpr_MathExpr_plus_Term1_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        if asts[2].symbol == Boolean or asts[2].symbol == Number:
            return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],plus,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        if asts[0].symbol == Boolean or asts[0].symbol == Number:
            return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],plus,asts[1].line,asts[1].column)
    return PlusAST(asts[0],asts[2],asts[1].line,asts[1].column)

def MathExpr_MathExpr_minus_Term1_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],minus,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],minus,asts[1].line,asts[1].column)
    return MinusAST(asts[0],asts[2],asts[1].line,asts[1].column)

def BoolExpr_or_op_BoolTerm1_reductor(asts:ASTListView) -> AST:
    return OrAST(asts[0],asts[2],asts[1].line,asts[1].column)

def BoolTerm1_BoolTerm1_and_op_BoolTerm2_reductor(asts:ASTListView) -> AST:
    return AndAST(asts[0],asts[2],asts[1].line,asts[1].column)

def BoolExpr_bit_or_BoolTerm1_reductor(asts:ASTListView) -> AST:
    return BitOrAST(asts[0],asts[2],asts[1].line,asts[1].column)

def BoolTerm1_BoolTerm1_bit_and_BoolTerm2_reductor(asts:ASTListView) -> AST:
    return BitAndAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_le_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],le,asts[1].line,asts[1].column)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],le,asts[1].line,asts[1].column)
    return LeAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_leq_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],leq,asts[1].line,asts[1].column)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],leq,asts[1].line,asts[1].column)
    return LeqAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_ge_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],ge,asts[1].line,asts[1].column)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],ge,asts[1].line,asts[1].column)
    return GeAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_geq_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],geq,asts[1].line,asts[1].column)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],geq,asts[1].line,asts[1].column)
    return GeqAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    return EqAST(asts[0],asts[2],asts[1].line,asts[1].column)

def UnaryBoolExpr1_UnaryBoolExpr1_neq_MathExpr_reductor(asts:ASTListView) -> AST:
    return NeqAST(asts[0],asts[2],asts[1].line,asts[1].column)

def BoolTerm1_lparen_UnaryBoolExpr_eq_BoolTerm1_rparen_reductor(asts:ASTListView) -> AST:
    return EqAST(asts[1],asts[3],asts[2].line,asts[2].column)

def Boolean_boolean_reductor(asts:ASTListView) -> AST:
    token:Token = asts[0] # type: ignore
    return BooleanAST(token.text,token.line,token.column)

def Term1_Term1_mul_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and asts[2].symbol == String:
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],mul,asts[1].line,asts[1].column)
    return MulAST(asts[0],asts[2],asts[1].line,asts[1].column)

def Term1_Term1_mul_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and asts[3].symbol == String:
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],mul,asts[1].line,asts[1].column)
    right = MinusMathExprAST(asts[2],asts[3],asts[2].line,asts[2].column) # type: ignore
    return MulAST(asts[0],right,asts[1].line,asts[1].column)

def Term1_Term1_div_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],div,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],div,asts[1].line,asts[1].column)    
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return DivAST(asts[0],asts[2],asts[1].line,asts[1].column)

def Term1_Term1_div_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],div,asts[1].line,asts[1].column)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],div,asts[1].line,asts[1].column)    
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[3],asts[1].line,asts[1].column)
    right_term = MinusMathExprAST(asts[2],asts[3],asts[2].line,asts[2].column) # type: ignore
    return DivAST(asts[0],right_term,asts[1].line,asts[1].column)

def Term1_Term1_int_div_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],int_div,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],int_div,asts[1].line,asts[1].column)    
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return IntDivAST(asts[0],asts[2],asts[1].line,asts[1].column)

def Term1_Term1_int_div_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],int_div,asts[1].line,asts[1].column)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],int_div,asts[1].line,asts[1].column)    
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[3],asts[1].line,asts[1].column)
    right_term = MinusMathExprAST(asts[2],asts[3],asts[2].line,asts[2].column) # type: ignore
    return IntDivAST(asts[0],right_term,asts[1].line,asts[1].column)

def Term1_Term1_mod_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],mod,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],mod,asts[1].line,asts[1].column)
    left:NumberAST = asts[0] # type: ignore
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return ModuleByLiteralZeroErrorAST(asts[0],asts[2],asts[1].line,asts[1].column)
    if left.symbol == Number and right.symbol == Number and (left._value_type == complex or right._value_type == complex):
        return ModuleWithComplexErrorAST(asts[0],asts[2],asts[1].line,asts[1].column)
    return ModAST(asts[0],asts[2],asts[1].line,asts[1].column)

def Term1_Term1_mod_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],mod,asts[1].line,asts[1].column)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],mod,asts[1].line,asts[1].column)
    left:NumberAST = asts[0] # type: ignore
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return ModuleByLiteralZeroErrorAST(asts[0],asts[3],asts[1].line,asts[1].column)
    if left.symbol == Number and right.symbol == Number and (left._value_type == complex or right._value_type == complex):
        return ModuleWithComplexErrorAST(asts[0],asts[3],asts[1].line,asts[1].column)
    right_term = MinusMathExprAST(asts[2],asts[3],asts[2].line,asts[2].column) # type: ignore
    return ModAST(asts[0],right_term,asts[1].line,asts[1].column)

def Term2_Term3_power_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],power,asts[1].line,asts[1].column)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],power,asts[1].line,asts[1].column)    
    return PowAST(asts[0],asts[2],asts[1].line,asts[1].column)

def Term2_Term3_power_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],power,asts[1].line,asts[1].column)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],power,asts[1].line,asts[1].column)
    right = MinusMathExprAST(asts[2],asts[3],asts[2].line,asts[2].column) # type: ignore
    return PowAST(asts[0],right,asts[1].line,asts[1].column)

def FuncCall_print_keyword_lparen_FuncCallArgs_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('print',asts[2],asts[0].line,asts[0].column) # type: ignore

def FuncCall_print_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('print',FuncCallArgsAST([],asts[1].line,asts[1].column),asts[0].line,asts[0].column) # type: ignore

def FuncCall_clear_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('clear',FuncCallArgsAST([],asts[1].line,asts[1].column),asts[0].line,asts[0].column)

def FuncCall_exit_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('exit',FuncCallArgsAST([],asts[1].line,asts[1].column),asts[0].line,asts[0].column)

def FuncCall_input_keyword_lparen_FuncCallArg_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('input',asts[2],asts[0].line,asts[0].column) # type: ignore

def FuncCall_input_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    return FuncCallAST('input',FuncCallArgsAST([],asts[1].line,asts[1].column),asts[0].line,asts[0].column)

def FuncCall_identifier_lparen_rparen_reductor(asts:ASTListView) -> AST:
    identifier:Token = asts[0] # type: ignore
    args = FuncCallArgsAST([],asts[1].line,asts[1].column)
    return FuncCallAST(identifier.text,args,asts[0].line,asts[0].column)

def FuncCall_identifier_lparen_FuncCallArgs_rparen_reductor(asts:ASTListView) -> AST:
    identifier:Token = asts[0] # type: ignore
    args:FuncCallArgsAST = asts[2] # type: ignore
    return FuncCallAST(identifier.text,args,asts[0].line,asts[0].column)

def FuncCallArgs_FuncCallArgs_comma_FuncCallArg_reductor(asts:ASTListView) -> AST:
    args:FuncCallArgsAST = asts[0] # type: ignore
    args._args.extend(asts[2]._args) # type: ignore
    return args

def FuncCallArg_reductor(asts:ASTListView) -> AST:
    return FuncCallArgsAST([asts[0]],asts[0].line,asts[0].column)

def Instructions_reductor(asts:ASTListView) -> AST:
    return InstructionsAST([asts[0]],asts[0].line,asts[0].column) # type: ignore

def Instructions_Instruction_reductor(asts:ASTListView) -> AST:
    instructions: InstructionsAST = asts[0] # type: ignore
    instructions._instructions.append(asts[1]) # type: ignore
    return instructions

def StringExpr_plus_String_reductor(asts:ASTListView) -> AST:
    return PlusAST(asts[0],asts[2],asts[1].line,asts[1].column)

def String_reductor(asts:ASTListView) -> AST:
    token:Token = asts[0] # type: ignore
    return StringAST(token.text,token.line,token.column)

def IfSmt_reductor(asts:ASTListView) -> AST:
    instrucions:InstructionsAST = asts[5] # type: ignore
    body = IfBodyAST(instrucions.instructions,instrucions.line,instrucions.column)
    return IfAST(asts[1],body,asts[0].line,asts[0].column) # type: ignore

def IfElseSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[5] # type: ignore
    ifsmt:IfAST = asts[0] # type: ignore
    else_body = ElseBodyAST(instructions.instructions,instructions.line,instructions.column)
    return IfElseAST(ifsmt.condition,ifsmt.body,else_body,ifsmt.line,ifsmt.column)

def IfElifSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[6] # type: ignore
    if_block:IfAST = asts[0] # type: ignore
    elif_condition = asts[2]
    elif_body = IfBodyAST(instructions.instructions,instructions.line,instructions.column)
    inner_if = InnerIfAST(if_block.condition,if_block.body,if_block.line,if_block.column)
    conditionals = [inner_if,InnerIfAST(elif_condition,elif_body,elif_condition.line,elif_condition.column)]
    return IfElifAST(conditionals,asts[0].line,asts[0].column)

def IfElifSmt_IfElifSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[6] # type: ignore
    ifelifsmt:IfElifAST = asts[0] # type: ignore
    elif_condition = asts[2]
    elif_body = IfBodyAST(instructions.instructions,instructions.line,instructions.column)
    ifelifsmt._conditionals.append(InnerIfAST(elif_condition,elif_body,elif_condition.line,elif_condition.column))
    return ifelifsmt

def IfElifElseSmt_reductor(asts:ASTListView) -> AST:
    ifelifsmt:IfElifAST = asts[0] # type: ignore
    instructions:InstructionsAST = asts[5] # type: ignore
    else_body = ElseBodyAST(instructions.instructions,instructions.line,instructions.column)
    return IfElifElseAST(ifelifsmt.conditionals,else_body,ifelifsmt.line,ifelifsmt.column)

def WhileSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[5] # type: ignore
    while_body = WhileBodyAST(instructions.instructions,instructions.line,instructions.column)
    return WhileAST(asts[1],while_body,asts[0].line,asts[0].column)

def FuncDef_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[7] # type: ignore
    identifier:Token = asts[1] # type: ignore
    args = FuncArgsAST([],asts[1].line,asts[1].column)
    body = FuncBodyAST(instructions.instructions,instructions.line,instructions.column)
    return FuncDefAST(identifier.text,args,body,asts[0].line,asts[0].column)

def FuncDef_args_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[8] # type: ignore
    identifier:Token = asts[1] # type: ignore
    args:FuncArgsAST = asts[3] # type: ignore
    body = FuncBodyAST(instructions.instructions,instructions.line,instructions.column)
    return FuncDefAST(identifier.text,args,body,asts[0].line,asts[0].column)

def FuncArgs_reductor(asts:ASTListView) -> AST:
    func_args = FuncArgsAST([asts[0]],asts[0].line,asts[0].column) # type: ignore
    return func_args

def FuncArgs_FuncArgs_comma_FuncArg_reductor(asts:ASTListView) -> AST:
    args:FuncArgsAST = asts[0] # type: ignore
    args._args.append(asts[2]) # type: ignore
    return args