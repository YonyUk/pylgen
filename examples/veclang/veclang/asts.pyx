from pylgen.common.types cimport AST,Symbol,Token,ASTListView
from .lexer import TokenTypeEnum

import numpy as np # type:ignore

# NON-TERMINALS
cdef Symbol VecLangProgram = Symbol('VecLangProgram') # type:ignore
cdef Symbol VecLangInstruction = Symbol('VecLangInstruction') # type:ignore
cdef Symbol VecLangInstructionsSequence = Symbol('VecLangInstructionSequence') # type:ignore
cdef Symbol ArithmeticExpressionLevel1 = Symbol('ArithmeticExpressionLevel1') # type:ignore
cdef Symbol ArithmeticExpressionLevel2 = Symbol('ArithmeticExpressionLevel2') # type:ignore
cdef Symbol ArithmeticExpressionLevel3 = Symbol('ArithmeticExpressionLevel3') # type:ignore
cdef Symbol ArithmeticExpressionLevel4 = Symbol('ArithmeticExpressionLevel4') # type:ignore
cdef Symbol Number = Symbol('Number') # type:ignore
cdef Symbol ComplexNumber = Symbol('ComplexNumber') # type:ignore
cdef Symbol NumberExpression = Symbol('NumberExpression') # type:ignore
cdef Symbol VariableExpression = Symbol('VariableExpression') # type:ignore
cdef Symbol VoidInstruction = Symbol('VoidInstruction') # type:ignore
cdef Symbol Components = Symbol('Components') # type:ignore
cdef Symbol Vector = Symbol('Vector') # type:ignore
cdef Symbol Range = Symbol('Range') # type:ignore
cdef Symbol Indexing = Symbol('Indexing') # type:ignore
cdef Symbol Slicing = Symbol('Slicing') # type:ignore
cdef Symbol FunctionCall = Symbol('FunctionCall') # type:ignore
cdef Symbol FunctionArgs = Symbol('FunctionArgs') # type:ignore
cdef Symbol FunctionDecl = Symbol('FunctionDecl') # type:ignore
cdef Symbol FunctionDeclArgs = Symbol('FunctionDeclArgs') # type:ignore
cdef Symbol Type = Symbol('Type') # type:ignore

# TERMINALS
cdef Symbol new_line = Symbol('new_line',True) # type:ignore
cdef Symbol int_number = Symbol('integer',True) # type:ignore
cdef Symbol float_number = Symbol('float',True) # type:ignore
cdef Symbol variable = Symbol('variable',True) # type:ignore
cdef Symbol plus = Symbol('+',True) # type:ignore
cdef Symbol minus = Symbol('-',True) # type:ignore
cdef Symbol mod = Symbol('%',True) # type:ignore
cdef Symbol div = Symbol('/',True) # type:ignore
cdef Symbol mul = Symbol('*',True) # type:ignore
cdef Symbol exp = Symbol('**',True) # type:ignore
cdef Symbol eq = Symbol('=',True) # type:ignore
cdef Symbol lp = Symbol('(',True) # type:ignore
cdef Symbol rp = Symbol(')',True) # type:ignore
cdef Symbol lc = Symbol('[',True) # type:ignore
cdef Symbol rc = Symbol(']',True) # type:ignore
cdef Symbol com = Symbol(',',True) # type:ignore
cdef Symbol double_dot = Symbol(':',True) # type:ignore
cdef Symbol sum_keyword = Symbol('sum_keyword',True) # type:ignore
cdef Symbol mean_keyword = Symbol('mean_keyword',True) # type:ignore
cdef Symbol dot_keyword = Symbol('dot_keyword',True) # type:ignore
cdef Symbol print_keyword = Symbol('print_keyword',True) # type:ignore
cdef Symbol type_int = Symbol('int_keyword',True) # type:ignore
cdef Symbol type_float = Symbol('float_keyword',True) # type:ignore
cdef Symbol type_complex = Symbol('complex_keyword',True) # type:ignore
cdef Symbol type_vector = Symbol('vector_keyword',True) # type:ignore

cdef class TypeAST(AST):

    def __init__(self, str type_name, int line, int column):
        super().__init__(Type, line, column) # type:ignore
        self._type = type_name
        self._childs = []
    
    @property
    def type_name(self) -> str:
        return self._type
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionDeclArgsAST(AST):

    def __init__(self, dict[VariableExpressionAST,str] args, int line, int column):
        super().__init__(FunctionDeclArgs, line, column) # type:ignore
        self._args = args
        self._childs = list(args.keys())
    
    @property
    def type_vars(self) -> dict[VariableExpressionAST,str]:
        return self._args.copy()
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionDeclAST(AST):

    def __init__(self, str func_name, FunctionDeclArgsAST args, AST body,int line, int column):
        super().__init__(FunctionDecl, line, column) # type:ignore
        self._name = func_name
        self._args = args
        self._body = body
        self._childs = [args,body]
    
    @property
    def func_name(self) -> str:
        return self._name
    
    @property
    def args(self) -> FunctionDeclArgsAST:
        return self._args
    
    @property
    def body(self) -> AST:
        return self._body
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionCallAST(AST):

    def __init__(self, str function_name, FunctionArgsAST args, int line, int column):
        super().__init__(FunctionCall, line, column) # type:ignore
        self._function_name = function_name
        self._args = args
        self._childs = [args]
    
    @property
    def function_name(self) -> str:
        return self._function_name
    
    @property
    def args(self) -> FunctionArgsAST:
        return self._args
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionArgsAST(AST):

    def __init__(self, list[AST] args, int line, int column):
        super().__init__(FunctionArgs, line, column) # type:ignore
        self._args = args.copy()
    
    @property
    def args(self) -> list[AST]:
        return self._args.copy()
    
    cpdef list[AST] children(self):
        return self._args

cdef class SlicingAST(AST):

    def __init__(self, AST target, RangeAST range_, int line, int column):
        super().__init__(Slicing, line, column) # type:ignore
        self._target = target
        self._range = range_
        self._childs = [target,range_]
    
    @property
    def range(self) -> RangeAST:
        return self._range
    
    @property
    def target(self) -> AST:
        return self._target

    cpdef list[AST] children(self):
        return self._childs

cdef class IndexingAST(AST):

    def __init__(self, AST target, int index, int line, int column):
        super().__init__(Indexing, line, column) # type:ignore
        self._target = target
        self._index = index
        self._childs = [target]
    
    @property
    def target(self) -> AST:
        return self._target
    
    @property
    def index(self) -> int:
        return self._index
    
    cpdef list[AST] children(self):
        return self._childs

cdef class RangeAST(AST):

    def __init__(self, int min_,int max_, int line, int column):
        super().__init__(Range, line, column) # type:ignore
        self._max = max_
        self._min = min_
        self._childs = []
    
    @property
    def min(self) -> int:
        return self._min
    
    @property
    def max(self) -> int:
        return self._max
    
    cpdef list[AST] children(self):
        return self._childs

cdef class VectorAST(AST):

    def __init__(self, VectorComponentsAST components, int line, int column):
        super().__init__(Vector, line, column) # type:ignore
        self._components = components
        self._childs = [components]

    @property
    def length(self) -> int:
        return len(self._components._components)
    
    cpdef list[AST] children(self):
        return self._childs

cdef class VectorComponentsAST(AST):

    def __init__(self, list[AST] components, int line, int column):
        super().__init__(Components, line, column) # type:ignore
        self._components = components
    
    cpdef list[AST] children(self):
        return self._components

cdef class VoidInstructionAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(VoidInstruction, line, column) # type:ignore
        self._childs = []

    cpdef list[AST] children(self):
        return self._childs

cdef class VariableExpressionAST(AST):
    
    def __init__(self, str name, int line, int column):
        super().__init__(VariableExpression, line, column) # type:ignore
        self._name = name
        self._index = -1
        self._childs = []
    
    @property
    def name(self) -> str:
        return self._name
    
    cpdef list[AST] children(self):
        return self._childs

cdef class VecLangInstructionsSequenceAST(AST):

    def __init__(self, list[AST] instructions, int line, int column):
        super().__init__(VecLangInstructionsSequence, line, column) # type:ignore
        self._instructions = instructions
    
    cpdef list[AST] children(self):
        return self._instructions

cdef class NumberAST(AST):

    def __init__(self, str value, type _type, int line, int column):
        super().__init__(NumberExpression, line, column) # type:ignore
        self._value = value
        self._type = _type
        self._childs = []
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def type(self) -> type:
        return self._type
    
    cpdef list[AST] children(self):
        return self._childs

cdef class BinaryAST(AST):

    def __init__(self, Symbol symbol, AST left, AST right, int line, int column):
        super().__init__(symbol, line, column) # type:ignore
        self._left = left
        self._right = right
        self._childs = [left,right]
    
    @property
    def left(self) -> AST:
        return self._left
    
    @property
    def right(self) -> AST:
        return self._right
    
    cpdef list[AST] children(self):
        return self._childs

cdef class PlusAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(plus, left, right, line, column)

cdef class MinusAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(minus, left, right, line, column)

cdef class ModAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(mod, left, right, line, column)

cdef class MulAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(mul, left, right, line, column)

cdef class DivAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(div, left, right, line, column)

cdef class ExpAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(exp, left, right, line, column)

cdef class AssigmentAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(eq, left, right, line, column)

asts_by_symbol = {
    plus:PlusAST,
    minus:MinusAST,
    mod:ModAST,
    mul:MulAST,
    div:DivAST,
    exp:ExpAST,
    eq:AssigmentAST
}

cdef AST single_reductor(ASTListView asts):
    return asts._get(0)

cdef AST plus_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return PlusAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST minus_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return MinusAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST mul_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return MulAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST div_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return DivAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST mod_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return ModAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST exp_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return ExpAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST assigment_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return AssigmentAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST extractor_reductor(ASTListView asts):
    return asts._get(1)

cdef AST instructions_sequence_reductor(ASTListView asts):
    cdef VecLangInstructionsSequenceAST pre
    cdef AST instruction
    if asts._size() == 1:
        instruction = asts._get(0)
        return VecLangInstructionsSequenceAST([instruction],instruction._line,instruction._column) # type:ignore
    elif asts._size() == 2:
        return asts._get(0)
    else:
        pre = asts._get(0) # type:ignore
        instruction = asts._get(2)
        pre._instructions.append(instruction)
        return pre

cdef AST void_reductor(ASTListView asts):
    cdef AST ast = asts._get(0)
    return VoidInstructionAST(ast._line,ast._column)

cdef AST number_reductor(ASTListView asts):
    cdef Token operator,number
    cdef NumberAST ast
    
    if asts._size() == 1:
        number = asts._get(0) # type:ignore
        if number._type == TokenTypeEnum.INTEGER:
            ast = NumberAST(number._text,np.int64,number._line,number._column)
        elif number._type == TokenTypeEnum.FLOAT:
            ast = NumberAST(number._text,np.float64,number._line,number._column)
    else:
        operator = asts._get(0) # type:ignore
        number = asts._get(1) # type:ignore
        if number._type == TokenTypeEnum.INTEGER:
            ast = NumberAST(f'{operator._text}{number._text}',np.int64,number._line,number._column)
        elif number._type == TokenTypeEnum.FLOAT:
            ast = NumberAST(f'{operator._text}{number._text}',np.float64,number._line,number._column)
    return ast

cdef AST variable_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    return VariableExpressionAST(token._text,token._line,token._column)

cdef AST complex_number_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    cdef NumberAST real,img
    cdef complex _value

    real = asts._get(2) # type:ignore
    img = asts._get(4) # type:ignore

    _value = np.complex128(real._type(real._value),img._type(img._value))

    return NumberAST(str(_value),np.complex128,token._line,token._column)
    
cdef AST vector_reductor(ASTListView asts):
    cdef Token star = asts._get(0) # type:ignore
    cdef VectorComponentsAST components = asts._get(1) # type:ignore
    return VectorAST(components,star._line,star._column)

cdef AST vector_components_reductor(ASTListView asts):
    cdef VectorComponentsAST components
    cdef AST ast

    if asts._size() == 1:
        ast = asts._get(0)
        components = VectorComponentsAST([ast],ast._line,ast._column)
    else:
        components = asts._get(0) # type:ignore
        ast = asts._get(2)
        components._components.append(ast)
    return components

cdef AST range_reductor(ASTListView asts):
    cdef Token min_,max_
    
    min_ = asts._get(0) # type:ignore
    max_ = asts._get(2) # type:ignore
    return RangeAST(int(min_._text),int(max_._text),min_._line,min_._column)

cdef AST range_reductor_1(ASTListView asts):
    cdef Token min_,max_,_minus

    _minus = asts._get(0) # type:ignore
    min_ = asts._get(1) # type:ignore
    max_ = asts._get(3) # type:ignore
    return RangeAST(int(f'{_minus._text}{min_._text}'),int(max_._text),min_._line,min_._column)

cdef AST range_reductor_2(ASTListView asts):
    cdef Token min_,max_,_minus

    min_ = asts._get(0) # type:ignore
    _minus = asts._get(2) # type:ignore
    max_ = asts._get(3) # type:ignore
    return RangeAST(int(min_._text),int(f'{_minus._text}{max_._text}'),min_._line,min_._column)

cdef AST range_reductor_3(ASTListView asts):
    cdef Token min_,max_,_minus1,_minus2

    _minus1 = asts._get(0) # type:ignore
    min_ = asts._get(1) # type:ignore
    _minus2 = asts._get(3) # type:ignore
    max_ = asts._get(4) # type:ignore
    return RangeAST(int(f'{_minus1._text}{min_._text}'),int(f'{_minus2._text}{max_._text}'),min_._line,min_._column)


cdef AST indexing_reductor(ASTListView asts):
    cdef Token index = asts._get(2) # type:ignore
    cdef AST target = asts._get(0)
    return IndexingAST(target,int(index._text),target._line,target._column)

cdef AST slicing_reductor(ASTListView asts):
    cdef AST target = asts._get(0)
    cdef RangeAST _range = asts._get(2) # type:ignore

    return SlicingAST(target,_range,target._line,target._column)

cdef AST function_call_reductor(ASTListView asts):
    cdef VariableExpressionAST function_name = asts._get(0) # type:ignore
    cdef FunctionArgsAST args = asts._get(2) # type:ignore
    return FunctionCallAST(function_name._name,args,function_name._line,function_name._column)

cdef AST built_in_function_call_reductor(ASTListView asts):
    cdef Token keyword = asts._get(0) # type:ignore
    cdef FunctionArgsAST args = asts._get(2) # type:ignore
    return FunctionCallAST(keyword._text,args,keyword._line,keyword._column)

cdef AST function_args_reductor(ASTListView asts):
    cdef FunctionArgsAST args
    cdef AST arg

    if asts._size() == 1:
        arg = asts._get(0)
        args = FunctionArgsAST([arg],arg._line,arg._column)
    else:
        args = asts._get(0) # type:ignore
        arg = asts._get(2)
        args._args.append(arg)
    
    return args

cdef AST function_declare_reductor(ASTListView asts):
    cdef VariableExpressionAST var = asts._get(0) # type:ignore
    cdef FunctionDeclArgsAST args = asts._get(2) # type:ignore
    cdef AST body = asts._get(5)

    return FunctionDeclAST(var._name,args,body,var._line,var._column)

cdef AST function_declare_args_reductor(ASTListView asts):
    cdef FunctionDeclArgsAST args
    cdef VariableExpressionAST var
    cdef TypeAST type_
    
    if asts._size() == 3:
        var = asts._get(0) # type:ignore
        type_ = asts._get(2) # type:ignore
        args = FunctionDeclArgsAST({var:type_._type},var._line,var._column)
    else:
        args = asts._get(0) # type:ignore
        var = asts._get(2) # type:ignore
        type_ = asts._get(4) # type:ignore
        args._args[var] = type_._type
        args._childs.append(var)
    
    return args

cdef AST type_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    return TypeAST(token._text,token._line,token._column)