from pylgen.common.types import ASTListView,AST

from .asts import *
from .error_asts import *

def PythonInstruction_BoolExpr_reductor(asts:ASTListView) -> AST:
    return InstructionAST(asts[0])

def Variable_reductor(asts:ASTListView) -> AST:
    return VariableAST(asts[0]) # type: ignore

def Break_reductor(asts:ASTListView) -> AST:
    return BreakAST(asts[0]) # type: ignore

def Continue_redutctor(asts:ASTListView) -> AST:
    return ContinueAST(asts[0]) # type: ignore

def PythonInstruction_return_keyword_BoolExpr_reductor(asts:ASTListView) -> AST:
    return ReturnAST(asts[0],asts[1]) # type: ignore

def PythonInstruction_return_keyword_reductor(asts:ASTListView) -> AST:
    return VoidReturnAST(asts[0]) # type: ignore

def PythonInstruction_Variable_assign_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = AssignAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_plus_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = PlusEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_minus_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = MinusEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_mul_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = MulEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_div_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = DivEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_int_div_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = IntDivEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_power_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = PowEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_mod_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    instruction = ModEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_bit_or_eq_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = BitOrEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def PythonInstruction_Variable_bit_and_eq_BoolExpr_reductor(asts:ASTListView) -> AST:
    instruction = BitAndEqAST(asts[0],asts[2])
    return InstructionAST(instruction)

def MathExpr_minus_UnaryMathExpr_reductor(asts:ASTListView) -> AST:
    return MinusMathExprAST(asts[0],asts[1]) # type: ignore

def UnaryBoolExpr_not_op_UnaryBoolExpr_reductor(asts:ASTListView) -> AST:
    return NotBoolExprAST(asts[0],asts[1]) # type: ignore

def Number_int_number_reductor(asts:ASTListView) -> AST:
    return NumberAST(asts[0],int) # type: ignore

def Number_float_number_reductor(asts:ASTListView) -> AST:
    return NumberAST(asts[0],float) # type: ignore

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def parenthesis_reductor(asts:ASTListView) -> AST:
    asts[1].start_position = asts[0].start_position
    asts[1].end_position = asts[2].end_position
    return asts[1]

def MathExpr_MathExpr_plus_Term1_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String:
        if asts[2].symbol == Boolean or asts[2].symbol == Number:
            return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],plus)
    if asts[2].symbol == String:
        if asts[0].symbol == Boolean or asts[0].symbol == Number:
            return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],plus)
    return PlusAST(asts[0],asts[2])

def MathExpr_MathExpr_minus_Term1_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],minus,sl,sc,el,ec)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],minus,sl,sc,el,ec)
    return MinusAST(asts[0],asts[2])

def BoolExpr_or_op_BoolTerm1_reductor(asts:ASTListView) -> AST:
    return OrAST(asts[0],asts[2])

def BoolTerm1_BoolTerm1_and_op_BoolTerm2_reductor(asts:ASTListView) -> AST:
    return AndAST(asts[0],asts[2])

def BoolExpr_bit_or_BoolTerm1_reductor(asts:ASTListView) -> AST:
    return BitOrAST(asts[0],asts[2])

def BoolTerm1_BoolTerm1_bit_and_BoolTerm2_reductor(asts:ASTListView) -> AST:
    return BitAndAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_le_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],le)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],le)
    return LeAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_leq_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],leq)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],leq)
    return LeqAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_ge_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],ge)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],ge)
    return GeAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_geq_MathExpr_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and (asts[2].symbol == Boolean or asts[2].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],geq)
    if asts[2].symbol == String and (asts[0].symbol == Boolean or asts[0].symbol == Number):
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],geq)
    return GeqAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_eq_MathExpr_reductor(asts:ASTListView) -> AST:
    return EqAST(asts[0],asts[2])

def UnaryBoolExpr1_UnaryBoolExpr1_neq_MathExpr_reductor(asts:ASTListView) -> AST:
    return NeqAST(asts[0],asts[2])

def Boolean_boolean_reductor(asts:ASTListView) -> AST:
    return BooleanAST(asts[0]) # type: ignore

def Term1_Term1_mul_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and asts[2].symbol == String:
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],mul)
    return MulAST(asts[0],asts[2])

def Term1_Term1_mul_minus_Term2_reductor(asts:ASTListView) -> AST:
    if asts[0].symbol == String and asts[3].symbol == String:
        return OperationNotSupportedForTypesErrorAST(asts[0],asts[2],mul)
    right = MinusMathExprAST(asts[2],asts[3]) # type: ignore
    return MulAST(asts[0],right)

def Term1_Term1_div_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],div,sl,sc,el,ec)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],div,sl,sc,el,ec)    
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[2])
    return DivAST(asts[0],asts[2])

def Term1_Term1_div_minus_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[3].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],div,sl,sc,el,ec)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],div,sl,sc,el,ec)    
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[3])
    right_term = MinusMathExprAST(asts[2],asts[3]) # type: ignore
    return DivAST(asts[0],right_term)

def Term1_Term1_int_div_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],int_div,sl,sc,el,ec)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],int_div,sl,sc,el,ec)    
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[2])
    return IntDivAST(asts[0],asts[2])

def Term1_Term1_int_div_minus_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[3].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],int_div,sl,sc,el,ec)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],int_div,sl,sc,el,ec)    
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return DivisionByLiteralZeroErrorAST(asts[0],asts[3])
    right_term = MinusMathExprAST(asts[2],asts[3]) # type: ignore
    return IntDivAST(asts[0],right_term)

def Term1_Term1_mod_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],mod,sl,sc,el,ec)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],mod,sl,sc,el,ec)
    left:NumberAST = asts[0] # type: ignore
    right:NumberAST = asts[2] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return ModuleByLiteralZeroErrorAST(asts[0],asts[2])
    if left.symbol == Number and right.symbol == Number and (left._value_type == complex or right._value_type == complex):
        return ModuleWithComplexErrorAST(asts[0],asts[2])
    return ModAST(asts[0],asts[2])

def Term1_Term1_mod_minus_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[3].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],mod,sl,sc,el,ec)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[3],mod,sl,sc,el,ec)
    left:NumberAST = asts[0] # type: ignore
    right:NumberAST = asts[3] # type: ignore
    if right.symbol == Number and right._value_type(right._value) == 0:
        return ModuleByLiteralZeroErrorAST(asts[0],asts[3])
    if left.symbol == Number and right.symbol == Number and (left._value_type == complex or right._value_type == complex):
        return ModuleWithComplexErrorAST(asts[0],asts[3])
    right_term = MinusMathExprAST(asts[2],asts[3]) # type: ignore
    return ModAST(asts[0],right_term)

def Term2_Term3_power_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],power,sl,sc,el,ec)
    if asts[2].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],power,sl,sc,el,ec)    
    return PowAST(asts[0],asts[2])

def Term2_Term3_power_minus_Term2_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[3].end_position
    if asts[0].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[0],power,sl,sc,el,ec)
    if asts[3].symbol == String:
        return OperationNotSupportedForTypeErrorAST(asts[2],power,sl,sc,el,ec)
    right = MinusMathExprAST(asts[2],asts[3]) # type: ignore
    return PowAST(asts[0],right)

def FuncCall_print_keyword_lparen_FuncCallArgs_rparen_reductor(asts:ASTListView) -> AST:
    func = FuncCallAST(asts[0],asts[2]) # type: ignore
    func.end_position = asts[3].end_position
    return func

def FuncCall_print_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[1].start_position,asts[2].end_position
    args = FuncCallArgsAST([],sl,sc,el,ec)
    func = FuncCallAST(asts[0],args) # type: ignore
    func.end_position = asts[2].end_position
    return func

def FuncCall_clear_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[1].start_position,asts[2].end_position
    args = FuncCallArgsAST([],sl,sc,el,ec)
    func = FuncCallAST(asts[0],args) # type: ignore
    func.end_position = asts[2].end_position
    return func

def FuncCall_exit_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[1].start_position,asts[2].end_position
    args = FuncCallArgsAST([],sl,sc,el,ec)
    func = FuncCallAST(asts[0],args) # type: ignore
    func.end_position = asts[2].end_position
    return func

def FuncCall_input_keyword_lparen_FuncCallArg_rparen_reductor(asts:ASTListView) -> AST:
    func = FuncCallAST(asts[0],asts[2]) # type: ignore
    func.end_position = asts[3].end_position
    return func

def FuncCall_input_keyword_lparen_rparen_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[1].start_position,asts[2].end_position
    args = FuncCallArgsAST([],sl,sc,el,ec)
    func = FuncCallAST(asts[0],args) # type: ignore
    func.end_position = asts[2].end_position
    return func

def FuncCall_identifier_lparen_rparen_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[1].start_position,asts[2].end_position
    args = FuncCallArgsAST([],sl,sc,el,ec)
    func = FuncCallAST(asts[0],args) # type: ignore
    func.end_position = asts[2].end_position
    return func

def FuncCall_identifier_lparen_FuncCallArgs_rparen_reductor(asts:ASTListView) -> AST:
    func = FuncCallAST(asts[0],asts[2]) # type: ignore
    func.end_position = asts[3].end_position
    return func

def FuncCallArgs_FuncCallArgs_comma_FuncCallArg_reductor(asts:ASTListView) -> AST:
    args:FuncCallArgsAST = asts[0] # type: ignore
    args._args.extend(asts[2]._args) # type: ignore
    args.end_position = asts[2].end_position
    return args

def FuncCallArg_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    return FuncCallArgsAST([asts[0]],sl,sc,el,ec)

def Instructions_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    return InstructionsAST([asts[0]],sl,sc,el,ec) # type: ignore

def Instructions_Instruction_reductor(asts:ASTListView) -> AST:
    instructions: InstructionsAST = asts[0] # type: ignore
    instructions._instructions.append(asts[1]) # type: ignore
    instructions.end_position = asts[1].end_position
    return instructions

def String_reductor(asts:ASTListView) -> AST:
    return StringAST(asts[0]) # type: ignore

def IfSmt_reductor(asts:ASTListView) -> AST:
    instrucions:InstructionsAST = asts[5] # type: ignore
    body = IfBodyAST(instrucions.instructions)
    (sl,sc),(el,ec) = asts[0].start_position,body.end_position
    return IfAST(asts[1],body,sl,sc,el,ec)

def IfElseSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[5] # type: ignore
    ifsmt:IfAST = asts[0] # type: ignore
    else_body = ElseBodyAST(instructions.instructions)
    (sl,sc),(el,ec) = asts[0].start_position,else_body.end_position
    return IfElseAST(ifsmt.condition,ifsmt.body,else_body,sl,sc,el,ec)

def IfElifSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[6] # type: ignore
    if_block:IfAST = asts[0] # type: ignore
    elif_condition = asts[2]
    elif_body = IfBodyAST(instructions.instructions)
    (sl,sc) = asts[0].start_position
    inner_if = InnerIfAST(if_block.condition,if_block.body,sl,sc,if_block.body.end_position[0],if_block.body.end_position[1])
    conditionals = [inner_if,InnerIfAST(elif_condition,elif_body,asts[1].start_position[0],asts[1].start_position[1],elif_body.end_position[0],elif_body.end_position[1])]
    return IfElifAST(conditionals)

def IfElifSmt_IfElifSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[6] # type: ignore
    ifelifsmt:IfElifAST = asts[0] # type: ignore
    elif_condition = asts[2]
    elif_body = IfBodyAST(instructions.instructions)
    (sl,sc),(el,ec) = asts[1].start_position,elif_body.end_position
    ifelifsmt._conditionals.append(InnerIfAST(elif_condition,elif_body,sl,sc,el,ec))
    return ifelifsmt

def IfElifElseSmt_reductor(asts:ASTListView) -> AST:
    ifelifsmt:IfElifAST = asts[0] # type: ignore
    instructions:InstructionsAST = asts[5] # type: ignore
    else_body = ElseBodyAST(instructions.instructions)
    return IfElifElseAST(ifelifsmt.conditionals,else_body)

def WhileSmt_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[5] # type: ignore
    while_body = WhileBodyAST(instructions.instructions)
    (sl,sc),(el,ec) = asts[0].start_position,while_body.end_position
    return WhileAST(asts[1],while_body,sl,sc,el,ec)

def FuncDef_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[7] # type: ignore
    identifier:Token = asts[1] # type: ignore
    (sl,sc),(el,ec) = asts[2].start_position,asts[3].end_position
    args = FuncArgsAST([],sl,sc,el,ec)
    body = FuncBodyAST(instructions.instructions)
    (sl,sc),(el,ec) = asts[0].start_position,body.end_position
    return FuncDefAST(identifier.text,args,body,sl,sc,el,ec)

def FuncDef_args_reductor(asts:ASTListView) -> AST:
    instructions:InstructionsAST = asts[8] # type: ignore
    identifier:Token = asts[1] # type: ignore
    args:FuncArgsAST = asts[3] # type: ignore
    body = FuncBodyAST(instructions.instructions)
    (sl,sc),(el,ec) = asts[0].start_position,body.end_position
    return FuncDefAST(identifier.text,args,body,sl,sc,el,ec)

def FuncArgs_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    func_args = FuncArgsAST([asts[0]],sl,sc,el,ec) # type: ignore
    return func_args

def FuncArgs_FuncArgs_comma_FuncArg_reductor(asts:ASTListView) -> AST:
    args:FuncArgsAST = asts[0] # type: ignore
    args._args.append(asts[2]) # type: ignore
    args.end_position = asts[2].end_position
    return args