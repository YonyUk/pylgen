from pylgen.common.types cimport AST,Symbol,Token,ASTListView,ErrorAST,Error,SemanticError

from .tokens_enum import TokenTypeEnum

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

cdef Symbol div_error = Symbol('Division Error')
cdef Symbol mod_error = Symbol('Module Error')
cdef Symbol int_too_large_error = Symbol('Integer Too Large Error')
cdef Symbol range_error = Symbol('Range Error')
cdef Symbol complex_error = Symbol('Complex Error')

cdef class TypeAST(AST):

    def __init__(self, str type_name, int line, int column):
        super().__init__(Type, line, column,line,column + len(type_name)) # type:ignore
        self._type = type_name
        self._childs = []
    
    @property
    def type_name(self) -> str:
        return self._type
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionDeclArgsAST(AST):

    def __init__(self, dict[VariableExpressionAST,str] args, int start_line, int start_column, int end_line, int end_column):
        super().__init__(FunctionDeclArgs, start_line,start_column,end_line,end_column)
        self._args = args
        self._childs = list(args.keys())
    
    @property
    def type_vars(self) -> dict[VariableExpressionAST,str]:
        return self._args.copy()
    
    cpdef list[AST] children(self):
        return self._childs

cdef class FunctionDeclAST(AST):

    def __init__(self, str func_name, FunctionDeclArgsAST args, AST body,int line, int column):
        super().__init__(FunctionDecl, line, column,body._end_line,body._end_column) # type:ignore
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

    def __init__(self, str function_name, FunctionArgsAST args, int start_line, int start_column, int end_line, int end_column):
        super().__init__(FunctionCall, start_line, start_column, end_line, end_column) # type:ignore
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

    def __init__(self, list[AST] args, int start_line, int start_column, int end_line, int end_column):
        super().__init__(FunctionArgs, start_line, start_column, end_line, end_column) # type:ignore
        self._args = args.copy()
    
    @property
    def args(self) -> list[AST]:
        return self._args.copy()
    
    cpdef list[AST] children(self):
        return self._args

cdef class SlicingAST(AST):

    def __init__(self, AST target, RangeAST range_, int start_line, int start_column, int end_line, int end_column):
        super().__init__(Slicing, start_line, start_column, end_line, end_column) # type:ignore
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

    def __init__(self, AST target, int index, int start_line, int start_column, int end_line, int end_column):
        super().__init__(Indexing, start_line, start_column, end_line, end_column) # type:ignore
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

    def __init__(self, int min_,int max_, int start_line, int start_column, int end_line, int end_column):
        super().__init__(Range, start_line, start_column, end_line, end_column) # type:ignore
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

    def __init__(self, VectorComponentsAST components):
        super().__init__(Vector, components._start_line, components._start_column, components._end_line, components._end_column) # type:ignore
        self._components = components
        self._childs = [components]

    @property
    def length(self) -> int:
        return len(self._components._components)
    
    cpdef list[AST] children(self):
        return self._childs

cdef class VectorComponentsAST(AST):

    def __init__(self, list[AST] components, int start_line, int start_column, int end_line, int end_column):
        super().__init__(Components, start_line, start_column, end_line, end_column) # type:ignore
        self._components = components
    
    cpdef list[AST] children(self):
        return self._components

cdef class VoidInstructionAST(AST):

    def __init__(self, int start_line, int start_column, int end_line, int end_column):
        super().__init__(VoidInstruction, start_line, start_column, end_line, end_column) # type:ignore
        self._childs = []

    cpdef list[AST] children(self):
        return self._childs

cdef class VariableExpressionAST(AST):
    
    def __init__(self, str name, int line, int column):
        super().__init__(VariableExpression, line, column,line,column + len(name)) # type:ignore
        self._name = name
        self._index = -1
        self._childs = []
    
    @property
    def name(self) -> str:
        return self._name
    
    cpdef list[AST] children(self):
        return self._childs

cdef class VecLangInstructionsSequenceAST(AST):

    def __init__(self, list[AST] instructions, int start_line, int start_column, int end_line, int end_column):
        super().__init__(VecLangInstructionsSequence, start_line, start_column, end_line, end_column) # type:ignore
        self._instructions = instructions
    
    cpdef list[AST] children(self):
        return self._instructions

cdef class NumberAST(AST):

    def __init__(self, str value, type _type, int line, int column):
        super().__init__(NumberExpression, line, column,line, column + len(value)) # type:ignore
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

    def __init__(self, Symbol symbol, AST left, AST right):
        super().__init__(symbol, left._start_line, left._start_column, right._end_line, right._end_column) # type:ignore
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

    def __init__(self, AST left, AST right):
        super().__init__(plus, left, right)

cdef class MinusAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(minus, left, right)

cdef class ModAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(mod, left, right)

cdef class MulAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(mul, left, right)

cdef class DivAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(div, left, right)

cdef class DivisionByZeroErrorAST(ErrorAST):
    
    def __init__(self, AST left,AST right):
        cdef SemanticError error = SemanticError('division by zero not allowed',left._start_line,left._start_column, right._end_line, right._end_column)
        super().__init__(div_error,left._start_line,left._start_column,right._end_line,right._end_column,{error})
        self._left = left
        self._right = right
    
    cpdef list[AST] children(self):
        return [self._left,self._right]

cdef class ModuleErrorAST(ErrorAST):

    def __init__(self, AST left, AST right,set[SemanticError] errors) -> None:
        super().__init__(mod_error,left._start_line,left._start_column,right._end_line,right._end_column,errors)
        self._left = left
        self._right = right
    
    cpdef list[AST] children(self):
        return [self._left,self._right]

cdef class ValueTooLargeForIntegerErrorAST(ErrorAST):

    def __init__(self, int line, int column,str text) -> None:
        cdef SemanticError error = SemanticError('Integer too large for 64 bits',line,column,line,column + len(text))
        super().__init__(int_too_large_error,line,column,line,column + len(text),{error})
        self._text = text
    
    @property
    def text(self) -> str:
        return self._text

    cpdef list[AST] children(self):
        return []

cdef class RangeErrorAST(ErrorAST):

    def __init__(self, int start_line, int start_column, int end_line, int end_column, set[SemanticError] errors) -> None:
        super().__init__(range_error,start_line,start_column,end_line,end_column,errors)
    
    cpdef list[AST] children(self):
        return []

cdef class ComplexNumberErrorAST(ErrorAST):

    def __init__(self, int start_line, int start_column, int end_line, int end_column,NumberAST coef, Token token) -> None:
        cdef SemanticError error = SemanticError(f'Unexpected expression "{coef._value}{token._text}", maybe you meant "{coef._value}j"?',start_line,start_column,end_line,end_column)
        super().__init__(complex_error,start_line,start_column,end_line,end_column,{error})
        self._coef = coef
        self._variable = token
    
    cpdef list[AST] children(self):
        return [self._coef,self._variable]

cdef class ExpAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(exp, left, right)

cdef class AssignmentAST(BinaryAST):

    def __init__(self, AST left, AST right):
        super().__init__(eq, left, right)

cdef inline AST single_reductor(ASTListView asts):
    return asts._get(0)

cdef inline AST plus_reductor(ASTListView asts):
    return PlusAST(asts._get(0),asts._get(2))

cdef inline AST minus_reductor(ASTListView asts):
    return MinusAST(asts._get(0),asts._get(2))

cdef inline AST mul_reductor(ASTListView asts):
    return MulAST(asts._get(0),asts._get(2))

cdef inline AST div_reductor(ASTListView asts):
    cdef NumberAST right
    if asts._get(2)._symbol._hash == NumberExpression._hash:
        right = asts._get(2)
        if right._type(right._value) == 0:
            return DivisionByZeroErrorAST(asts._get(0),right)
    return DivAST(asts._get(0),asts._get(2))

cdef inline AST mod_reductor(ASTListView asts):
    cdef NumberAST right,left
    cdef set[SemanticError] errors = set()

    if asts._get(2)._symbol._hash == NumberExpression._hash:
        right = asts._get(2)
        if right._type(right._value) == 0:
            errors.add(SemanticError("module by zero not allowed",asts._get(0)._start_line,asts._get(0)._start_column,right._end_line,right._end_column))
        if right._type == np.complex128:
            errors.add(SemanticError("module with complex numbers not allowed",asts._get(0)._start_line,asts._get(0)._start_column,right._end_line,right._end_column))
        if right._type != np.int64:
            errors.add(SemanticError("module by a non-integer not allowed",asts._get(0)._start_line,asts._get(0)._start_column,right._end_line,right._end_column))
    if asts._get(0)._symbol._hash == NumberExpression._hash:
        left = asts._get(0)
        if left._type == np.complex128:
            errors.add(SemanticError("module with complex numbers not allowed",left._start_line,left._start_column,asts._get(2)._end_line,asts._get(2)._end_column))
    if errors:
        return ModuleErrorAST(asts._get(0),asts._get(2),errors)
    return ModAST(asts._get(0),asts._get(2))

cdef inline AST exp_reductor(ASTListView asts):
    return ExpAST(asts._get(0),asts._get(2))

cdef inline AST assignment_reductor(ASTListView asts):
    return AssignmentAST(asts._get(0),asts._get(2))

cdef inline AST extractor_reductor(ASTListView asts):
    asts._get(1)._start_line = asts._get(0)._start_line
    asts._get(1)._start_column = asts._get(0)._start_column
    asts._get(1)._end_line = asts._get(2)._end_line
    asts._get(1)._end_column = asts._get(2)._end_column
    return asts._get(1)

cdef inline AST instructions_sequence_reductor(ASTListView asts):
    cdef VecLangInstructionsSequenceAST pre
    cdef AST instruction
    if asts._size() == 1:
        instruction = asts._get(0)
        return VecLangInstructionsSequenceAST([instruction],instruction._start_line,instruction._start_column,instruction._end_line,instruction._end_column) # type:ignore
    elif asts._size() == 2:
        return asts._get(0)
    else:
        pre = asts._get(0) # type:ignore
        instruction = asts._get(2)
        pre._instructions.append(instruction)
        pre._end_line = instruction._end_line
        pre._end_column = instruction._end_column
        return pre

cdef inline AST void_reductor(ASTListView asts):
    cdef AST ast = asts._get(0)
    return VoidInstructionAST(ast._start_line,ast._start_column,ast._end_line,ast._end_column)

cdef inline AST number_reductor(ASTListView asts):
    cdef Token operator,number
    cdef NumberAST ast
    
    if asts._size() == 1:
        number = asts._get(0) # type:ignore
        if number._type == TokenTypeEnum.INTEGER:
            if int(number._text).bit_length() >= 64:
                return ValueTooLargeForIntegerErrorAST(number._start_line,number._start_column,number._text)
            ast = NumberAST(number._text,np.int64,number._start_line,number._start_column)
        elif number._type == TokenTypeEnum.FLOAT:
            ast = NumberAST(number._text,np.float64,number._start_line,number._start_column)
    else:
        operator = asts._get(0) # type:ignore
        number = asts._get(1) # type:ignore
        if number._type == TokenTypeEnum.INTEGER:
            ast = NumberAST(f'{operator._text}{number._text}',np.int64,number._start_line,number._start_column)
        elif number._type == TokenTypeEnum.FLOAT:
            ast = NumberAST(f'{operator._text}{number._text}',np.float64,number._start_line,number._start_column)
    return ast

cdef inline AST variable_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    return VariableExpressionAST(token._text,token._start_line,token._start_column)

cdef inline AST complex_number_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    cdef NumberAST real,img
    cdef complex _value

    real = asts._get(2) # type:ignore
    img = asts._get(4) # type:ignore

    _value = np.complex128(real._type(real._value),img._type(img._value))

    return NumberAST(str(_value),np.complex128,token._start_line,token._start_column)

cdef inline AST complex_number_reductor_1(ASTListView asts):
    cdef Token token = asts._get(1)
    cdef NumberAST img = asts._get(0)
    cdef Error error
    cdef complex _value = np.complex128(0,img._type(img._value))

    if token._text != 'j':
        return ComplexNumberErrorAST(img._start_line,img._start_column,img._end_line,img._end_column,img,token)
    
    return NumberAST(str(_value),np.complex128,img._start_line,img._start_column)

cdef inline AST vector_reductor(ASTListView asts):
    cdef VectorComponentsAST components = asts._get(1) # type:ignore
    return VectorAST(components)

cdef inline AST vector_components_reductor(ASTListView asts):
    cdef VectorComponentsAST components
    cdef AST ast

    if asts._size() == 1:
        ast = asts._get(0)
        components = VectorComponentsAST([ast],ast._start_line,ast._start_column,ast._end_line,ast._end_column)
    else:
        components = asts._get(0) # type:ignore
        ast = asts._get(2)
        components._components.append(ast)
        components._end_line = ast._end_line
        components._end_column = ast._end_column
    return components

cdef inline AST range_reductor(ASTListView asts):
    cdef Token min_,max_,double_dots
    cdef set[SemanticError] errors = set()

    min_ = asts._get(0) # type:ignore
    max_ = asts._get(2) # type:ignore
    double_dots = asts._get(1)

    if int(min_._text).bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',min_._start_line,min_._start_column,min_._end_line,min_._end_column))
    
    if int(max_._text).bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',max_._start_line,max_._start_column,max_._end_line,max_._end_column))

    if int(min_._text) > int(max_._text):
        errors.add(SemanticError('minimum value must be less or equal to maximum value',min_._start_line_line,min_._start_column,max_._end_line,max_._end_column))

    if errors:
        return RangeErrorAST(min_._start_line,min_._start_column,max_._end_line,max_._end_column,errors)
    return RangeAST(int(min_._text),int(max_._text),min_._start_line,min_._start_column,max_._end_line,max_._end_column)

cdef inline AST range_reductor_1(ASTListView asts):
    cdef Token min_,max_,_minus,double_dots
    cdef set[SemanticError] errors = set()

    _minus = asts._get(0) # type:ignore
    min_ = asts._get(1) # type:ignore
    max_ = asts._get(3) # type:ignore
    double_dots = asts._get(2)

    if int(f'{_minus._text}{min_._text}').bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',_minus._start_line,_minus._start_column,min_._end_line,min_._end_column))
    
    if int(max_._text).bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',max_._start_line,max_._start_column,max_._end_line,max_._end_column))

    if int(f'{_minus._text}{min_._text}') > int(max_._text):
        errors.add(SemanticError('minimum value must be less or equal to maximum value',_minus._start_line_line,_minus._start_column,max_._end_line,max_._end_column))

    if errors:
        return RangeErrorAST(_minus._start_line,_minus._start_column,max_._end_line,max_._end_column,errors)
    return RangeAST(int(f'{_minus._text}{min_._text}'),int(max_._text),_minus._start_line,_minus._start_column,max_._end_line,max_._end_column)

cdef inline AST range_reductor_2(ASTListView asts):
    cdef Token min_,max_,_minus,double_dots
    cdef set[SemanticError] errors = set()

    min_ = asts._get(0) # type:ignore
    double_dots = asts._get(1)
    _minus = asts._get(2) # type:ignore
    max_ = asts._get(3) # type:ignore

    if int(min_._text).bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',min_._start_line,min_._start_column,min_._end_line,min_._end_column))
    
    if int(f'{_minus._text}{max_._text}').bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',_minus._start_line,_minus._start_column,max_._end_line,max_._end_column))

    if int(min_._text) > int(f'{_minus._text}{max_._text}'):
        errors.add(SemanticError('minimum value must be less or equal to maximum value',min_._start_line,min_._start_column,max_._end_line,max_._end_column))

    if errors:
        return RangeErrorAST(min_._start_line,min_._start_column,max_._end_line,max_._end_column,errors)
    return RangeAST(int(min_._text),int(f'{_minus._text}{max_._text}'),min_._start_line,min_._start_column,max_._end_line,max_._end_column)

cdef inline AST range_reductor_3(ASTListView asts):
    cdef Token min_,max_,_minus1,_minus2,double_dots
    cdef set[SemanticError] errors = set()

    _minus1 = asts._get(0) # type:ignore
    min_ = asts._get(1) # type:ignore
    double_dots = asts._get(2)
    _minus2 = asts._get(3) # type:ignore
    max_ = asts._get(4) # type:ignore

    if int(f'{_minus1._text}{min_._text}').bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',_minus1._start_line,_minus1._start_column,min_._end_line,min_._end_column))
    
    if int(f'{_minus2._text}{max_._text}').bit_length() >= 32:
        errors.add(SemanticError('Integer too large for 32 bits',_minus2._start_line,_minus2._start_column,max_._end_line,max_._end_column))

    if int(f'{_minus1._text}{min_._text}') > int(f'{_minus2._text}{max_._text}'):
        errors.add(SemanticError('minimum value must be less or equal to maximum value',_minus1._start_line,_minus1._start_column,max_._end_line,max_._end_column))

    if errors:
        return RangeErrorAST(_minus1._start_line,_minus1._start_column,max_._end_line,max_._end_column,errors)

    return RangeAST(int(f'{_minus1._text}{min_._text}'),int(f'{_minus2._text}{max_._text}'),_minus1._start_line,_minus1._start_column,max_._end_line,max_._end_column)


cdef inline AST indexing_reductor(ASTListView asts):
    cdef Token index = asts._get(2) # type:ignore
    cdef AST target = asts._get(0)
    return IndexingAST(target,int(index._text),target._start_line,target._start_column,asts._get(3)._end_line,asts._get(3)._end_column)

cdef inline AST slicing_reductor(ASTListView asts):
    cdef AST target = asts._get(0)
    cdef RangeAST _range = asts._get(2) # type:ignore

    return SlicingAST(target,_range,target._start_line,target._start_column,asts._get(3)._end_line,asts._get(3)._end_column)

cdef inline AST function_call_reductor(ASTListView asts):
    cdef VariableExpressionAST function_name = asts._get(0) # type:ignore
    cdef FunctionArgsAST args = asts._get(2) # type:ignore
    return FunctionCallAST(function_name._name,args,function_name._start_line,function_name._start_column,asts._get(3)._end_line,asts._get(3)._end_column)

cdef inline AST built_in_function_call_reductor(ASTListView asts):
    cdef Token keyword = asts._get(0) # type:ignore
    cdef FunctionArgsAST args = asts._get(2) # type:ignore
    return FunctionCallAST(keyword._text,args,keyword._start_line,keyword._start_column,asts._get(3)._end_line,asts._get(3)._end_column)

cdef inline AST function_args_reductor(ASTListView asts):
    cdef FunctionArgsAST args
    cdef AST arg

    if asts._size() == 1:
        arg = asts._get(0)
        args = FunctionArgsAST([arg],arg._start_line,arg._start_column,arg._end_line,arg._end_column)
    else:
        args = asts._get(0) # type:ignore
        arg = asts._get(2)
        args._args.append(arg)
        args._end_line = arg._end_line
        args._end_column = arg._end_column
    
    return args

cdef inline AST function_declare_reductor(ASTListView asts):
    cdef VariableExpressionAST var = asts._get(0) # type:ignore
    cdef FunctionDeclArgsAST args = asts._get(2) # type:ignore
    cdef AST body = asts._get(5)

    return FunctionDeclAST(var._name,args,body,var._start_line,var._start_column)

cdef inline AST function_declare_args_reductor(ASTListView asts):
    cdef FunctionDeclArgsAST args
    cdef VariableExpressionAST var
    cdef TypeAST type_
    
    if asts._size() == 3:
        var = asts._get(0) # type:ignore
        type_ = asts._get(2) # type:ignore
        args = FunctionDeclArgsAST({var:type_._type},var._start_line,var._start_column,type_._end_line,type_._end_column)
    else:
        args = asts._get(0) # type:ignore
        var = asts._get(2) # type:ignore
        type_ = asts._get(4) # type:ignore
        args._args[var] = type_._type
        args._childs.append(var)
        args._end_line = type_._end_line
        args._end_column = type_._end_column
    
    return args

cdef inline AST type_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    return TypeAST(token._text,token._start_line,token._start_column)