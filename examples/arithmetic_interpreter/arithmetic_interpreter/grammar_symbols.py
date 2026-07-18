from pylgen.common.types import Symbol

END_SYMBOL = '$'

ArithmeticExpression = Symbol('ArithmeticExpression')
E = Symbol('E')
T = Symbol('T')
F = Symbol('F')
P = Symbol('P')
VAR = Symbol('VAR')

plus = Symbol('+',True)
minus = Symbol('-',True)
mod = Symbol('%',True)
mul = Symbol('*',True)
div = Symbol('/',True)
exp = Symbol('**',True)
number = Symbol('number',True)
lp = Symbol('(',True)
rp = Symbol(')',True)
eq = Symbol('=',True)
variable = Symbol('variable',True)
exit = Symbol('exit',True)
clear = Symbol('clear',True)