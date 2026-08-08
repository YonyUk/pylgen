from pylgen.grammar.grammar import Grammar
from pylgen.common.types import Symbol
from pylgen.visual import draw_lalr1_propagation_edges,set_cache_file

set_cache_file('cache')

VecLangProgram = Symbol('VecLangProgram')
VecLangInstruction = Symbol('VecLangInstruction')
VecLangInstructionsSequence = Symbol('VecLangInstructionSequence')
ArithmeticExpressionLevel1 = Symbol('ArithmeticExpressionLevel1')
ArithmeticExpressionLevel2 = Symbol('ArithmeticExpressionLevel2')
ArithmeticExpressionLevel3 = Symbol('ArithmeticExpressionLevel3')
ArithmeticExpressionLevel4 = Symbol('ArithmeticExpressionLevel4')
Number = Symbol('Number')
ComplexNumber = Symbol('ComplexNumber')
NumberExpression = Symbol('NumberExpression')
VariableExpression = Symbol('VariableExpression')
VoidInstruction = Symbol('VoidInstruction')
Components = Symbol('Components')
Vector = Symbol('Vector')
Range = Symbol('Range')
Indexing = Symbol('Indexing')
Slicing = Symbol('Slicing')
FunctionCall = Symbol('FunctionCall')
FunctionArgs = Symbol('FunctionArgs')
FunctionDecl = Symbol('FunctionDecl')
FunctionDeclArgs = Symbol('FunctionDeclArgs')
Type = Symbol('Type')

# TERMINALS
new_line = Symbol('new_line',True)
int_number = Symbol('integer',True)
float_number = Symbol('float',True)
variable = Symbol('variable',True)
plus = Symbol('+',True)
minus = Symbol('-',True)
mod = Symbol('%',True)
div = Symbol('/',True)
mul = Symbol('*',True)
exp = Symbol('**',True)
eq = Symbol('=',True)
lp = Symbol('(',True)
rp = Symbol(')',True)
lc = Symbol('[',True)
rc = Symbol(']',True)
com = Symbol(',',True)
double_dot = Symbol(':',True)
sum_keyword = Symbol('sum_keyword',True)
mean_keyword = Symbol('mean_keyword',True)
dot_keyword = Symbol('dot_keyword',True)
print_keyword = Symbol('print_keyword',True)
type_int = Symbol('int_keyword',True)
type_float = Symbol('float_keyword',True)
type_complex = Symbol('complex_keyword',True)
type_vector = Symbol('vector_keyword',True)

VecLangGrammar = Grammar(VecLangProgram,'$')

VecLangGrammar[VecLangProgram] += VecLangInstructionsSequence,

VecLangGrammar[VecLangInstructionsSequence] += VecLangInstructionsSequence,new_line,VecLangInstruction
VecLangGrammar[VecLangInstructionsSequence] += VecLangInstructionsSequence,new_line
VecLangGrammar[VecLangInstructionsSequence] += VecLangInstruction,

VecLangGrammar[VecLangInstruction] += ArithmeticExpressionLevel1,
VecLangGrammar[VecLangInstruction] += FunctionDecl,
VecLangGrammar[VecLangInstruction] += VariableExpression,eq,ArithmeticExpressionLevel1
VecLangGrammar[VecLangInstruction] += print_keyword,lp,FunctionArgs,rp

VecLangGrammar[ArithmeticExpressionLevel1] += ArithmeticExpressionLevel1,plus,ArithmeticExpressionLevel2
VecLangGrammar[ArithmeticExpressionLevel1] += ArithmeticExpressionLevel1,minus,ArithmeticExpressionLevel2
VecLangGrammar[ArithmeticExpressionLevel1] += ArithmeticExpressionLevel2,

VecLangGrammar[ArithmeticExpressionLevel2] += ArithmeticExpressionLevel2,mul,ArithmeticExpressionLevel3
VecLangGrammar[ArithmeticExpressionLevel2] += ArithmeticExpressionLevel2,div,ArithmeticExpressionLevel3
VecLangGrammar[ArithmeticExpressionLevel2] += ArithmeticExpressionLevel2,mod,ArithmeticExpressionLevel3
VecLangGrammar[ArithmeticExpressionLevel2] += ArithmeticExpressionLevel3,

VecLangGrammar[ArithmeticExpressionLevel3] += ArithmeticExpressionLevel3,exp,ArithmeticExpressionLevel4
VecLangGrammar[ArithmeticExpressionLevel3] += ArithmeticExpressionLevel4,

VecLangGrammar[ArithmeticExpressionLevel4] += NumberExpression,
VecLangGrammar[ArithmeticExpressionLevel4] += VariableExpression,
VecLangGrammar[ArithmeticExpressionLevel4] += Vector,
VecLangGrammar[ArithmeticExpressionLevel4] += Indexing,
VecLangGrammar[ArithmeticExpressionLevel4] += FunctionCall,
VecLangGrammar[ArithmeticExpressionLevel4] += lp,ArithmeticExpressionLevel1,rp

VecLangGrammar[NumberExpression] += Number,
VecLangGrammar[NumberExpression] += ComplexNumber,

VecLangGrammar[Number] += int_number,
VecLangGrammar[Number] += float_number,
VecLangGrammar[Number] += plus,int_number
VecLangGrammar[Number] += minus,int_number
VecLangGrammar[Number] += plus,float_number
VecLangGrammar[Number] += minus,float_number

VecLangGrammar[ComplexNumber] += type_complex,lp,Number,com,Number,rp

VecLangGrammar[VariableExpression] += variable,

VecLangGrammar[Vector] += lc,Components,rc
VecLangGrammar[Vector] += lc,Range,rc
VecLangGrammar[Vector] += Slicing,

VecLangGrammar[Components] += ArithmeticExpressionLevel1,
VecLangGrammar[Components] += Components,com,ArithmeticExpressionLevel1

VecLangGrammar[Range] += int_number,double_dot,int_number
VecLangGrammar[Range] += minus,int_number,double_dot,int_number
VecLangGrammar[Range] += int_number,double_dot,minus,int_number
VecLangGrammar[Range] += minus,int_number,double_dot,minus,int_number

VecLangGrammar[Indexing] += VariableExpression,lc,int_number,rc
VecLangGrammar[Indexing] += Vector,lc,int_number,rc

VecLangGrammar[Slicing] += VariableExpression,lc,Range,rc
VecLangGrammar[Slicing] += Vector,lc,Range,rc

VecLangGrammar[FunctionCall] += VariableExpression,lp,FunctionArgs,rp
VecLangGrammar[FunctionCall] += sum_keyword,lp,FunctionArgs,rp
VecLangGrammar[FunctionCall] += mean_keyword,lp,FunctionArgs,rp
VecLangGrammar[FunctionCall] += dot_keyword,lp,FunctionArgs,rp

VecLangGrammar[FunctionArgs] += ArithmeticExpressionLevel1,
VecLangGrammar[FunctionArgs] += FunctionArgs,com,ArithmeticExpressionLevel1

VecLangGrammar[FunctionDecl] += VariableExpression,lp,FunctionDeclArgs,rp,eq,ArithmeticExpressionLevel1

VecLangGrammar[FunctionDeclArgs] += VariableExpression,double_dot,Type
VecLangGrammar[FunctionDeclArgs] += FunctionDeclArgs,com,VariableExpression,double_dot,Type

VecLangGrammar[Type] += type_complex,
VecLangGrammar[Type] += type_float,
VecLangGrammar[Type] += type_int,
VecLangGrammar[Type] += type_vector,

draw_lalr1_propagation_edges(VecLangGrammar,filename='edges',show=True,cache=True,physics=True,filter_menu=True)