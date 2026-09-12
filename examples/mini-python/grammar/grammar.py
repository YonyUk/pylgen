from pylgen.grammar import AttributedGrammar
from pylgen.parser import ParserBuilder,ParserType

from .symbols import *
from .reductors import *

G = AttributedGrammar(PythonProgram)

G[PythonProgram] += (PythonInstructions,),single_reductor

G[PythonInstructions] += (PythonInstruction,),Instructions_reductor
G[PythonInstructions] += (PythonInstructions,PythonInstruction),Instructions_Instruction_reductor

G[PythonInstruction] += (BoolExpr,jumpline),single_reductor
G[PythonInstruction] += (Variable,assign,BoolExpr,jumpline),PythonInstruction_Variable_assign_BoolExpr_reductor
G[PythonInstruction] += (Variable,plus_eq,MathExpr,jumpline),PythonInstruction_Variable_plus_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,minus_eq,MathExpr,jumpline),PythonInstruction_Variable_minus_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,mul_eq,MathExpr,jumpline),PythonInstruction_Variable_mul_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,div_eq,MathExpr,jumpline),PythonInstruction_Variable_div_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,int_div_eq,MathExpr,jumpline),PythonInstruction_Variable_int_div_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,power_eq,MathExpr,jumpline),PythonInstruction_Variable_power_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,mod_eq,MathExpr,jumpline),PythonInstruction_Variable_mod_eq_MathExpr_reductor
G[PythonInstruction] += (Variable,bit_or_eq,BoolExpr,jumpline),PythonInstruction_Variable_bit_or_eq_BoolExpr_reductor
G[PythonInstruction] += (Variable,bit_and_eq,BoolExpr,jumpline),PythonInstruction_Variable_bit_and_eq_BoolExpr_reductor
G[PythonInstruction] += (return_keyword,BoolExpr,jumpline),PythonInstruction_return_keyword_BoolExpr_reductor
G[PythonInstruction] += (return_keyword,jumpline),PythonInstruction_return_keyword_reductor
G[PythonInstruction] += (break_keyword,jumpline),Break_reductor
G[PythonInstruction] += (continue_keyword,jumpline),Continue_redutctor
G[PythonInstruction] += (IfSmt,),single_reductor
G[PythonInstruction] += (IfElseSmt,),single_reductor
G[PythonInstruction] += (IfElifSmt,),single_reductor
G[PythonInstruction] += (IfElifElseSmt,),single_reductor
G[PythonInstruction] += (WhileSmt,),single_reductor
G[PythonInstruction] += (FuncDef,),single_reductor

G[BoolExpr] += (BoolExpr,or_op,BoolTerm1),BoolExpr_or_op_BoolTerm1_reductor
G[BoolExpr] += (BoolExpr,bit_or,BoolTerm1),BoolExpr_bit_or_BoolTerm1_reductor
G[BoolExpr] += (BoolTerm1,),single_reductor

G[BoolTerm1] += (BoolTerm1,and_op,BoolTerm2),BoolTerm1_BoolTerm1_and_op_BoolTerm2_reductor
G[BoolTerm1] += (BoolTerm1,bit_and,BoolTerm2),BoolTerm1_BoolTerm1_bit_and_BoolTerm2_reductor
G[BoolTerm1] += (BoolTerm2,),single_reductor

G[BoolTerm2] += (UnaryBoolExpr,),single_reductor

G[UnaryBoolExpr] += (not_op,UnaryBoolExpr),UnaryBoolExpr_not_op_UnaryBoolExpr_reductor
G[UnaryBoolExpr] += (UnaryBoolExpr1,),single_reductor

G[UnaryBoolExpr1] += (UnaryBoolExpr1,eq,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_eq_MathExpr_reductor
G[UnaryBoolExpr1] += (UnaryBoolExpr1,neq,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_neq_MathExpr_reductor
G[UnaryBoolExpr1] += (UnaryBoolExpr1,le,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_le_MathExpr_reductor
G[UnaryBoolExpr1] += (UnaryBoolExpr1,leq,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_leq_MathExpr_reductor
G[UnaryBoolExpr1] += (UnaryBoolExpr1,ge,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_ge_MathExpr_reductor
G[UnaryBoolExpr1] += (UnaryBoolExpr1,geq,MathExpr),UnaryBoolExpr1_UnaryBoolExpr1_geq_MathExpr_reductor
G[UnaryBoolExpr1] += (MathExpr,),single_reductor

G[MathExpr] += (minus,UnaryMathExpr),MathExpr_minus_UnaryMathExpr_reductor
G[MathExpr] += (UnaryMathExpr,),single_reductor

G[UnaryMathExpr] += (UnaryMathExpr,plus,Term1),MathExpr_MathExpr_plus_Term1_reductor
G[UnaryMathExpr] += (UnaryMathExpr,minus,Term1),MathExpr_MathExpr_minus_Term1_reductor
G[UnaryMathExpr] += (Term1,),single_reductor

G[Term1] += (Term1,mul,Term2),Term1_Term1_mul_Term2_reductor
G[Term1] += (Term1,div,Term2),Term1_Term1_div_Term2_reductor
G[Term1] += (Term1,int_div,Term2),Term1_Term1_int_div_Term2_reductor
G[Term1] += (Term1,mod,Term2),Term1_Term1_mod_Term2_reductor
G[Term1] += (Term2,),single_reductor

G[Term2] += (Term2,power,Term3),Term2_Term2_power_Term3_reductor
G[Term2] += (Term3,),single_reductor

G[Term3] += (Number,),single_reductor
G[Term3] += (Boolean,),single_reductor
G[Term3] += (String,),single_reductor
G[Term3] += (FuncCall,),single_reductor
G[Term3] += (Variable,),single_reductor
G[Term3] += (lparen,BoolExpr,rparen),parenthesis_reductor

G[Number] += (int_number,),Number_int_number_reductor
G[Number] += (float_number,),Number_float_number_reductor

G[Boolean] += (boolean,),Boolean_boolean_reductor

G[String] += (string,),String_reductor

G[FuncCall] += (print_keyword,lparen,FuncCallArgs,rparen),FuncCall_print_keyword_lparen_FuncCallArgs_rparen_reductor
G[FuncCall] += (print_keyword,lparen,rparen),FuncCall_print_keyword_lparen_rparen_reductor
G[FuncCall] += (clear_keyword,lparen,rparen),FuncCall_clear_keyword_lparen_rparen_reductor
G[FuncCall] += (exit_keyword,lparen,rparen),FuncCall_exit_keyword_lparen_rparen_reductor
G[FuncCall] += (input_keyword,lparen,FuncCallArg,rparen),FuncCall_input_keyword_lparen_FuncCallArg_rparen_reductor
G[FuncCall] += (input_keyword,lparen,rparen),FuncCall_input_keyword_lparen_rparen_reductor
G[FuncCall] += (identifier,lparen,rparen),FuncCall_identifier_lparen_rparen_reductor
G[FuncCall] += (identifier,lparen,FuncCallArgs,rparen),FuncCall_identifier_lparen_FuncCallArgs_rparen_reductor

G[FuncCallArgs] += (FuncCallArg,),single_reductor
G[FuncCallArgs] += (FuncCallArgs,comma,FuncCallArg),FuncCallArgs_FuncCallArgs_comma_FuncCallArg_reductor

G[FuncCallArg] += (BoolExpr,),FuncCallArg_reductor

G[Variable] += (identifier,),Variable_reductor

G[IfSmt] += (if_keyword,BoolExpr,colon,jumpline,indent,PythonInstructions,dedent),IfSmt_reductor

G[IfElseSmt] += (IfSmt,else_keyword,colon,jumpline,indent,PythonInstructions,dedent),IfElseSmt_reductor
G[IfElifSmt] += (IfSmt,elif_keyword,BoolExpr,colon,jumpline,indent,PythonInstructions,dedent),IfElifSmt_reductor
G[IfElifSmt] += (IfElifSmt,elif_keyword,BoolExpr,colon,jumpline,indent,PythonInstructions,dedent),IfElifSmt_IfElifSmt_reductor

G[IfElifElseSmt] += (IfElifSmt,else_keyword,colon,jumpline,indent,PythonInstructions,dedent),IfElifElseSmt_reductor

G[WhileSmt] += (while_keyword,BoolExpr,colon,jumpline,indent,PythonInstructions,dedent),WhileSmt_reductor

G[FuncDef] += (def_keyword,identifier,lparen,rparen,colon,jumpline,indent,PythonInstructions,dedent),FuncDef_reductor
G[FuncDef] += (def_keyword,identifier,lparen,FuncArgs,rparen,colon,jumpline,indent,PythonInstructions,dedent),FuncDef_args_reductor

G[FuncArg] += (Variable,),single_reductor

G[FuncArgs] += (FuncArg,),FuncArgs_reductor
G[FuncArgs] += (FuncArgs,comma,FuncArg),FuncArgs_FuncArgs_comma_FuncArg_reductor

print('building parsing tables...')
PythonParser = ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1)
print('done')