from pylgen.common.types import Symbol

######################################################################################
# EXTRAS
######################################################################################
jumpline = Symbol('jumpline',True)
indent = Symbol('INDENT',True)
dedent = Symbol('DEDENT',True)
identifier = Symbol('identifier',True)

######################################################################################
# primitive types
######################################################################################
int_number = Symbol('int_number',True)
float_number = Symbol('float_number',True)
boolean = Symbol('boolean',True)
string = Symbol('string',True)

######################################################################################
# operators
######################################################################################
plus = Symbol('+',True)
minus = Symbol('-',True)
mul = Symbol('*',True)
div = Symbol('/',True)
int_div = Symbol('//',True)
mod = Symbol('%',True)
power = Symbol('**',True)
eq = Symbol('==',True)
or_op = Symbol('or',True)
bit_or = Symbol('|',True)
bit_and = Symbol('&',True)
and_op = Symbol('and',True)
not_op = Symbol('not',True)
assign = Symbol('=',True)
neq = Symbol('!=',True)
le = Symbol('<',True)
ge = Symbol('>',True)
leq = Symbol('<=',True)
geq = Symbol('>=',True)
plus_eq = Symbol('+=',True)
minus_eq = Symbol('-=',True)
mul_eq = Symbol('*=',True)
div_eq = Symbol('/=',True)
int_div_eq = Symbol('//=',True)
power_eq = Symbol('**=',True)
mod_eq = Symbol('%=',True)
bit_or_eq = Symbol('|=',True)
bit_and_eq = Symbol('&=',True)

######################################################################################
# symbols
######################################################################################
lparen = Symbol('(',True)
rparen = Symbol(')',True)
comma = Symbol(',',True)
colon = Symbol(':',True)

######################################################################################
# keywords
######################################################################################
print_keyword = Symbol('print',True)
input_keyword = Symbol('input',True)
clear_keyword = Symbol('clear',True)
exit_keyword = Symbol('exit',True)
if_keyword = Symbol('if',True)
elif_keyword = Symbol('elif',True)
else_keyword = Symbol('else',True)
while_keyword = Symbol('while',True)
for_keyword = Symbol('for',True)
def_keyword = Symbol('def',True)
return_keyword = Symbol('return',True)
break_keyword = Symbol('break',True)
continue_keyword = Symbol('continue',True)

######################################################################################
# NON-TERMINALS
######################################################################################

PythonProgram = Symbol('PythonProgram')
PythonInstruction = Symbol('PythonInstruction')
PythonInstructions = Symbol('PythonInstructions')
BoolExpr = Symbol('BoolExpr')
UnaryBoolExpr = Symbol('UnaryBoolExpr')
UnaryBoolExpr1 = Symbol('UnaryBoolExpr1')
MathExpr = Symbol('MathExpr')
StringExpr = Symbol('StringExpr')
UnaryMathExpr = Symbol('UnaryMathExpr')
Term1 = Symbol('Term1')
BoolTerm1 = Symbol('BoolTerm1')
BoolTerm2 = Symbol('BoolTerm2')
Term2 = Symbol('Term2')
Term3 = Symbol('Term3')
Number = Symbol('Number')
Boolean = Symbol('Boolean')
String = Symbol('String')
Variable = Symbol('Variable')

FuncCallArgs = Symbol('FuncCallArgs')
FuncCallArg = Symbol('FuncCallArg')
FuncCall = Symbol('FuncCall')

IfSmt = Symbol('IfSmt')
InnerIfSmt = Symbol('InnerIfSmt')
IfElseSmt = Symbol('IfElseSmt')
IfBody = Symbol('IfBody')
ElseBody = Symbol('ElseBody')
IfElifSmt = Symbol('IfElifSmt')
IfElifElseSmt = Symbol('IfElifElseSmt')

WhileSmt = Symbol('WhileSmt')
WhileBody = Symbol('WhileBody')
ForSmt = Symbol('ForSmt')

FuncDef = Symbol('FuncDef')
FuncBody = Symbol('FuncBody')
FuncArg = Symbol('FuncArg')
FuncArgs = Symbol('FuncArgs')

ReturnSmt = Symbol('ReturnSmt')
VoidReturnSmt = Symbol('VoidReturnSmt')