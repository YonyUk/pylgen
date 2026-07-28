# Step 2: Building the Parser and AST

VecLang's grammar is richer than the arithmetic language we saw earlier: it includes vectors, ranges, slicing, indexing, function definitions, and complex numbers. Our parser must handle all these features efficiently, which is why we'll use **Cython** to compile the parser and its reductors into fast, native code.

## Grammar Symbols: Terminals and Non-terminals

Before writing grammar rules, we must declare the symbols they will use. Recall the distinction:

 - **Terminals**: correspond to actual tokens from the lexer (e.g., `+`, `number`, `variable`). They are the leaves of our grammar.
 - **Non‑terminals**: abstract categories that represent groups of symbols (e.g., `ArithmeticExpressionLevel1`, `Vector`). They will be expanded into more specific symbols.

In the Cython‑based implementation, all symbols are defined as `cdef Symbol` variables, both in the declaration file (`asts.pxd`) and the implementation file (`asts.pyx`). This ensures they are available at compile time and reduces overhead.

These are the symbols that map directly to token types. They were already defined in the lexer, but we need to declare them as `cdef` so the parser can recognise them.

!!! important
    The symbols returned by the mapping function must perfectly match those used in the grammar, and follow the same token-symbol correspondence.

File: `asts.pxd`
```cython
from pylgen.common.types cimport Symbol

# NON-TERMINALS
cdef Symbol VecLangProgram
cdef Symbol VecLangInstruction
cdef Symbol VecLangInstructionsSequence
cdef Symbol ArithmeticExpressionLevel1
cdef Symbol ArithmeticExpressionLevel2
cdef Symbol ArithmeticExpressionLevel3
cdef Symbol ArithmeticExpressionLevel4
cdef Symbol Number
cdef Symbol ComplexNumber
cdef Symbol NumberExpression
cdef Symbol VariableExpression
cdef Symbol VoidInstruction
cdef Symbol Components
cdef Symbol Vector
cdef Symbol Range
cdef Symbol Indexing
cdef Symbol Slicing
cdef Symbol FunctionCall
cdef Symbol FunctionArgs
cdef Symbol FunctionDecl
cdef Symbol FunctionDeclArgs
cdef Symbol Type

# TERMINALS
cdef Symbol new_line
cdef Symbol int_number
cdef Symbol float_number
cdef Symbol variable
cdef Symbol plus
cdef Symbol minus
cdef Symbol mod
cdef Symbol div
cdef Symbol mul
cdef Symbol exp
cdef Symbol eq
cdef Symbol lp
cdef Symbol rp
cdef Symbol lc
cdef Symbol rc
cdef Symbol com
cdef Symbol double_dot
cdef Symbol sum_keyword
cdef Symbol mean_keyword
cdef Symbol dot_keyword
cdef Symbol print_keyword
cdef Symbol type_int
cdef Symbol type_float
cdef Symbol type_complex
cdef Symbol type_vector
```

## Designing the Abstract Syntax Tree (AST)

The parser's goal is not just to validate the input but to produce a structured representation of the program, the AST. Each node in the AST corresponds to a language construct, carrying enough information for later evaluation.

In VecLang, we have many node types. To keep the code maintainable, we use a class hierarchy:

 - A base `AST` class (provided by PyLGEN) provides common attributes like line/column and a `children()` method.

 - `BinaryAST` is an abstract base for all binary operations (addition, subtraction, multiplication, division, modulo, exponentiation, and assignment). It stores `left` and `right` children.

 - Specific binary operation classes (`PlusAST`, `MinusAST`, etc.) inherit from `BinaryAST` and simply forward the operator symbol.

 - Other nodes are domain‑specific: `NumberAST` (for integers, floats, and complex numbers), `VariableExpressionAST`, `VectorAST`, `RangeAST`, `IndexingAST`, `SlicingAST`, `FunctionCallAST`, `FunctionDeclAST`, `FunctionDeclArgsAST`, `TypeAST`, and several for sequences and instructions.

All AST classes are defined as `cdef class` in `asts.pxd` to allow fast attribute access in Cython, and implemented in `asts.pyx`.

### Specialised Nodes

For brevity, we'll highlight a few others:

 - `VectorAST`: holds a `VectorComponentsAST` that contains a list of component ASTs.

 - `RangeAST`: stores `min` and `max` integers (used in vector literals like `[4:10]` and in slicing).

 - `SlicingAST`: combines a target (a variable or vector) with a `RangeAST`.

 - `FunctionCallAST`: stores the function name and a `FunctionArgsAST` (a list of argument ASTs).

 - `FunctionDeclAST`: stores the function name, its arguments (with types), and the body AST.

 - `TypeAST`: holds a type name (int, float, complex, vector).

All AST nodes implement `children()` to return their sub‑ASTs, which is useful for tree traversal during semantic analysis and evaluation.

### Reductors

Reducer functions are also defined and implemented here, so they can be used from other files. We'll explain them later; for now, let's just leave them there.

### Recap

Finally, this is how the files look:

File `asts.pxd`
```cython
from pylgen.common.types cimport AST,Symbol,ASTListView,Token

# NON-TERMINALS
cdef Symbol VecLangProgram
cdef Symbol VecLangInstruction
cdef Symbol VecLangInstructionsSequence
cdef Symbol ArithmeticExpressionLevel1
cdef Symbol ArithmeticExpressionLevel2
cdef Symbol ArithmeticExpressionLevel3
cdef Symbol ArithmeticExpressionLevel4
cdef Symbol Number
cdef Symbol ComplexNumber
cdef Symbol NumberExpression
cdef Symbol VariableExpression
cdef Symbol VoidInstruction
cdef Symbol Components
cdef Symbol Vector
cdef Symbol Range
cdef Symbol Indexing
cdef Symbol Slicing
cdef Symbol FunctionCall
cdef Symbol FunctionArgs
cdef Symbol FunctionDecl
cdef Symbol FunctionDeclArgs
cdef Symbol Type

# TERMINALS
cdef Symbol new_line
cdef Symbol int_number
cdef Symbol float_number
cdef Symbol variable
cdef Symbol plus
cdef Symbol minus
cdef Symbol mod
cdef Symbol div
cdef Symbol mul
cdef Symbol exp
cdef Symbol eq
cdef Symbol lp
cdef Symbol rp
cdef Symbol lc
cdef Symbol rc
cdef Symbol com
cdef Symbol double_dot
cdef Symbol sum_keyword
cdef Symbol mean_keyword
cdef Symbol dot_keyword
cdef Symbol print_keyword
cdef Symbol type_int
cdef Symbol type_float
cdef Symbol type_complex
cdef Symbol type_vector

cdef class TypeAST(AST):
    cdef str _type
    cdef list[AST] _childs

cdef class FunctionDeclArgsAST(AST):
    cdef dict[VariableExpressionAST,str] _args
    cdef list[AST] _childs

cdef class FunctionDeclAST(AST):
    cdef AST _body
    cdef FunctionDeclArgsAST _args
    cdef str _name
    cdef list[AST] _childs

cdef class FunctionArgsAST(AST):
    cdef list[AST] _args

cdef class FunctionCallAST(AST):
    cdef FunctionArgsAST _args
    cdef str _function_name
    cdef list[AST] _childs

cdef class SlicingAST(AST):
    cdef AST _target
    cdef RangeAST _range
    cdef list[AST] _childs

cdef class IndexingAST(AST):
    cdef AST _target
    cdef int _index
    cdef list[AST] _childs

cdef class RangeAST(AST):
    cdef int _min
    cdef int _max
    cdef list[AST] _childs

cdef class VectorAST(AST):
    cdef VectorComponentsAST _components
    cdef list[AST] _childs

cdef class VectorComponentsAST(AST):
    cdef list[AST] _components

cdef class VoidInstructionAST(AST):
    cdef list[AST] _childs

cdef class VariableExpressionAST(AST):
    cdef str _name
    cdef int _index
    cdef list[AST] _childs

cdef class VecLangInstructionsSequenceAST(AST):
    cdef list[AST] _instructions

cdef class NumberAST(AST):
    cdef type _type # type:ignore
    cdef str _value
    cdef list[AST] _childs

cdef class BinaryAST(AST):
    cdef AST _left
    cdef AST _right
    cdef list[AST] _childs

cdef class PlusAST(BinaryAST):
    pass

cdef class MinusAST(BinaryAST):
    pass

cdef class MulAST(BinaryAST):
    pass

cdef class DivAST(BinaryAST):
    pass

cdef class ModAST(BinaryAST):
    pass

cdef class ExpAST(BinaryAST):
    pass

cdef class AssignmentAST(BinaryAST):
    pass

cdef AST single_reductor(ASTListView asts)

cdef AST plus_reductor(ASTListView asts)

cdef AST minus_reductor(ASTListView asts)

cdef AST mul_reductor(ASTListView asts)

cdef AST div_reductor(ASTListView asts)

cdef AST mod_reductor(ASTListView asts)

cdef AST exp_reductor(ASTListView asts)

cdef AST assignment_reductor(ASTListView asts)

cdef AST extractor_reductor(ASTListView asts)

cdef AST instructions_sequence_reductor(ASTListView asts)

cdef AST number_reductor(ASTListView asts)

cdef AST void_reductor(ASTListView asts)

cdef AST variable_reductor(ASTListView asts)

cdef AST complex_number_reductor(ASTListView asts)

cdef AST vector_reductor(ASTListView asts)

cdef AST vector_components_reductor(ASTListView asts)

cdef AST range_reductor(ASTListView asts)

cdef AST range_reductor_1(ASTListView asts)

cdef AST range_reductor_2(ASTListView asts)

cdef AST range_reductor_3(ASTListView asts)

cdef AST indexing_reductor(ASTListView asts)

cdef AST slicing_reductor(ASTListView asts)

cdef AST function_call_reductor(ASTListView asts)

cdef AST function_args_reductor(ASTListView asts)

cdef AST built_in_function_call_reductor(ASTListView asts)

cdef AST function_declare_reductor(ASTListView asts)

cdef AST function_declare_args_reductor(ASTListView asts)

cdef AST type_reductor(ASTListView asts)
```

File: `asts.pyx`
```cython
from pylgen.common.types cimport AST,Symbol,Token,ASTListView
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

cdef class AssignmentAST(BinaryAST):

    def __init__(self, AST left, AST right, int line, int column):
        super().__init__(eq, left, right, line, column)

asts_by_symbol = {
    plus:PlusAST,
    minus:MinusAST,
    mod:ModAST,
    mul:MulAST,
    div:DivAST,
    exp:ExpAST,
    eq:AssignmentAST
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

cdef AST assignment_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return AssignmentAST(asts._get(0),asts._get(2),ast._line,ast._column)

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
```

!!! note
    The linter may complain about type compatibility; this is completely normal and does not affect its correctness. Simply adding a few `# type: ignore` commands will stop the complaining.

## Writing the Grammar

The grammar is built in `parser.pyx`. Here's how we set it up:
```cython
cpdef BottomUpParser build_parser():
    cdef AttributedGrammar VecLangGrammar = AttributedGrammar(VecLangProgram) # default end marker is '\x00' character

    # Add all productions
    # ...

    return _build_lalr_parser_from_attributed(VecLangGrammar)
```

We'll add productions grouped by language feature.

> ### 1. Program and Instructions Sequence

A VecLang program is a sequence of instructions separated by newlines.

```cython
VecLangGrammar._add_attributed_production(VecLangProgram,[VecLangInstructionsSequence],single_reductor)

VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line,VecLangInstruction],instructions_sequence_reductor)
VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line],instructions_sequence_reductor)
VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstruction],instructions_sequence_reductor)
```

 - `single_reductor` simply returns the only child.

 - `instructions_sequence_reductor` builds a VecLangInstructionsSequenceAST that accumulates instructions.

> ### 2. Arithmetic Expressions

Arithmetic is organised into four precedence levels, from lowest to highest:

 - **Level 1**: addition and subtraction (`+`, `-`).

 - **Level 2**: multiplication, division, modulo (`*`, `/`, `%`).

 - **Level 3**: exponentiation (`**`).

 - **Level 4**: atoms (numbers, variables, vectors, indexing, function calls, parentheses).

```cython
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,plus,ArithmeticExpressionLevel2],plus_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,minus,ArithmeticExpressionLevel2],minus_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel2],single_reductor)

VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mul,ArithmeticExpressionLevel3],mul_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,div,ArithmeticExpressionLevel3],div_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mod,ArithmeticExpressionLevel3],mod_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel3],single_reductor)

VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel3,exp,ArithmeticExpressionLevel4],exp_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel4],single_reductor)

VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[NumberExpression],single_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[VariableExpression],single_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Vector],single_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Indexing],single_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[FunctionCall],single_reductor)
VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[lp,ArithmeticExpressionLevel1,rp],extractor_reductor)

```

 - Each binary operator has its own reductor (`plus_reductor`, `minus_reductor`, etc.) for maximum performance.

 - `extractor_reductor` extracts the inner expression from parentheses, discarding the parentheses symbols.

> ### 3. Numbers and ComplexNumbers

Numbers can be integers, floats, or complex numbers (like `complex(2, 3)`). They may also have an explicit sign.

```cython
VecLangGrammar._add_attributed_production(NumberExpression,[Number],single_reductor)
VecLangGrammar._add_attributed_production(NumberExpression,[ComplexNumber],single_reductor)

VecLangGrammar._add_attributed_production(Number,[int_number],number_reductor)
VecLangGrammar._add_attributed_production(Number,[float_number],number_reductor)
VecLangGrammar._add_attributed_production(Number,[plus,int_number],number_reductor)
VecLangGrammar._add_attributed_production(Number,[minus,int_number],number_reductor)
VecLangGrammar._add_attributed_production(Number,[plus,float_number],number_reductor)
VecLangGrammar._add_attributed_production(Number,[minus,float_number],number_reductor)

VecLangGrammar._add_attributed_production(ComplexNumber,[type_complex,lp,Number,com,Number,rp],complex_number_reductor)
```

 - `number_reductor` creates a `NumberAST` and determines the type based on the token type.

 - `complex_number_reductor` builds a complex number from two `NumberAST`s.

> ### 4. Vectors and Ranges

VecLang supports vector literals like `[1,2,3,4]` and range-based vectors like `[4:10]`.

```cython
VecLangGrammar._add_attributed_production(Vector,[lc,Components,rc],vector_reductor)
VecLangGrammar._add_attributed_production(Vector,[lc,Range,rc],extractor_reductor)
VecLangGrammar._add_attributed_production(Vector,[Slicing],single_reductor)
```

!!! note "Slices are vectors too"

Components are sequences of arithmetic expressions separated by commas:

```cython
VecLangGrammar._add_attributed_production(Components,[ArithmeticExpressionLevel1],vector_components_reductor)
VecLangGrammar._add_attributed_production(Components,[Components,com,ArithmeticExpressionLevel1],vector_components_reductor)
```

And ranges can have negative bounds:

```cython
VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,int_number],range_reductor)
VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,int_number],range_reductor_1)
VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,minus,int_number],range_reductor_2)
VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,minus,int_number],range_reductor_3)
```

The different reductors handle the presence of minus signs for negative bounds.

> ### 5. Indexing and Slicing

Indexing: `vec[2]` or `var[5]`. Slicing: `var[0:5]` or `vec[3:7]`.

```cython
VecLangGrammar._add_attributed_production(Indexing,[VariableExpression,lc,int_number,rc],indexing_reductor)
VecLangGrammar._add_attributed_production(Indexing,[Vector,lc,int_number,rc],indexing_reductor)

VecLangGrammar._add_attributed_production(Slicing,[VariableExpression,lc,Range,rc],slicing_reductor)
VecLangGrammar._add_attributed_production(Slicing,[Vector,lc,Range,rc],slicing_reductor)
```

 - `indexing_reductor` builds an `IndexingAST` with the target and the integer index.

 - `slicing_reductor` builds a `SlicingAST` with the target and a `RangeAST`.

> ### 6. Function Calls and Built-in Functions

User‑defined functions and built‑ins (`sum`, `mean`, `dot`, `print`) share the same call syntax.

```cython
VecLangGrammar._add_attributed_production(FunctionCall,[VariableExpression,lp,FunctionArgs,rp],function_call_reductor)
VecLangGrammar._add_attributed_production(FunctionCall,[sum_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
VecLangGrammar._add_attributed_production(FunctionCall,[mean_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
VecLangGrammar._add_attributed_production(FunctionCall,[dot_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
```

!!! note
    `print` function is not an arithmetic expression, so we don't write its production here, but in the top of grammar hierarchy, as a `VecLangInstruction`.

    ```cython
    VecLangGrammar._add_attributed_production(VecLangInstruction,[print_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
    ```

Arguments are lists of expressions:

```cython
VecLangGrammar._add_attributed_production(FunctionArgs,[ArithmeticExpressionLevel1],function_args_reductor)
VecLangGrammar._add_attributed_production(FunctionArgs,[FunctionArgs,com,ArithmeticExpressionLevel1],function_args_reductor)
```

 - `function_call_reductor` uses the name from a `VariableExpressionAST`.

 - `built_in_function_call_reductor` uses the token text (e.g., "sum").


> ### 7. Function Declarations

VecLang allows defining functions with typed arguments:

```txt
f(x: int, y: float) = x + y
```

```cython
VecLangGrammar._add_attributed_production(FunctionDecl,[VariableExpression,lp,FunctionDeclArgs,rp,eq,ArithmeticExpressionLevel1],function_declare_reductor)
```

And the arguments are declared with types:

```cython
VecLangGrammar._add_attributed_production(FunctionDeclArgs,[VariableExpression,double_dot,Type],function_declare_args_reductor)
VecLangGrammar._add_attributed_production(FunctionDeclArgs,[FunctionDeclArgs,com,VariableExpression,double_dot,Type],function_declare_args_reductor)

VecLangGrammar._add_attributed_production(Type,[type_complex],type_reductor)
VecLangGrammar._add_attributed_production(Type,[type_float],type_reductor)
VecLangGrammar._add_attributed_production(Type,[type_int],type_reductor)
VecLangGrammar._add_attributed_production(Type,[type_vector],type_reductor)
```

 - `function_declare_args_reductor` builds a `FunctionDeclArgsAST` that maps variable names to their types.

 - `type_reductor` creates a `TypeAST`.

> ### 8. Instructions

An instruction can be an expression, a function declaration, an assignment, or a `print` statement.

```cython
VecLangGrammar._add_attributed_production(VecLangInstruction,[ArithmeticExpressionLevel1],single_reductor)
VecLangGrammar._add_attributed_production(VecLangInstruction,[FunctionDecl],single_reductor)
VecLangGrammar._add_attributed_production(VecLangInstruction,[VariableExpression,eq,ArithmeticExpressionLevel1],assignment_reductor)
VecLangGrammar._add_attributed_production(VecLangInstruction,[print_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)

# ...

VecLangGrammar._add_attributed_production(VariableExpression,[variable],variable_reductor)
```

 - Assignment uses `assignment_reductor` which creates an `AssignmentAST`.

 - Print is treated as a built‑in function call.

## Connecting the Dots: Reductors

Reductors are the glue between the grammar and the AST. They receive an `ASTListView` (an immutable view of the child ASTs) and produce a new AST for the left‑hand side.

Because performance matters, we define each reductor as a `cdef` function (or `cdef` with a return type) to avoid Python call overhead. They are implemented in `asts.pyx`.

> ### Single and Extractor Reductors

These are trivial:
```cython
cdef AST single_reductor(ASTListView asts):
    return asts._get(0)

cdef AST extractor_reductor(ASTListView asts):
    return asts._get(1)
```

> ### Binary Operation Reductors

We have separate reductors for each operator. For example:

```cython
cdef AST plus_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return PlusAST(asts._get(0),asts._get(2),ast._line,ast._column)
```

Similarly for `minus_reductor`, `mul_reductor`, etc. This avoids a conditional chain and is faster in Cython.

> ### Assignment Reductor

```cython
cdef AST assignment_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return AssignmentAST(asts._get(0),asts._get(2),ast._line,ast._column)
```

> ### Number and Complex Number Reductors

number_reductor creates a `NumberAST` with the appropriate type.

```cython
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
```

`complex_number_reductor` extracts the real and imaginary parts from two `NumberAST`s and creates a complex number.

```cython
cdef AST complex_number_reductor(ASTListView asts):
    cdef Token token = asts._get(0) # type:ignore
    cdef NumberAST real,img
    cdef complex _value

    real = asts._get(2) # type:ignore
    img = asts._get(4) # type:ignore

    _value = np.complex128(real._type(real._value),img._type(img._value))

    return NumberAST(str(_value),np.complex128,token._line,token._column)
```

> ### Vector and Components

`vector_reductor` builds a `VectorAST` from a `ComponentsAST`. The components are built by `vector_components_reductor`, which accumulates elements into a list.

> ### Range Reductors

There are four variants to handle signs. Each creates a `RangeAST`.

> ### Indexing and Slicing

`indexing_reductor` extracts the integer index and builds an `IndexingAST`. `slicing_reductor` builds a `SlicingAST` with the target and the `RangeAST`.

> ### Function Call Reductors

`function_call_reductor` gets the function name from a `VariableExpressionAST` and the arguments from a `FunctionArgsAST`.

`built_in_function_call_reductor` uses the token text (e.g., "sum") to name the function.

> ### Function Declaration and Arguments

`function_declare_reductor` creates a `FunctionDeclAST`. `function_declare_args_reductor` builds a dictionary mapping variable names to types.

> ### Type Reductor

`type_reductor` creates a `TypeAST` from the keyword token.

## Putting It All Together: The Parser Builder

Finally, after adding all productions, we build the LALR(1) parser using PyLGEN's `_build_lalr_parser_from_attributed`:

```cython
return _build_lalr_parser_from_attributed(VecLangGrammar)
```

This function compiles the grammar into a table‑driven parser that can be used to parse any VecLang program.

File: `parser.pxd`

```cython
from pylgen.parser.parser cimport BottomUpParser

cpdef BottomUpParser build_parser()
```

File: `parser.pyx`
```cython
from pylgen.grammar.grammar cimport AttributedGrammar
from pylgen.parser.parser_builder cimport _build_lalr_parser_from_attributed
from pylgen.parser.parser cimport BottomUpParser
from pylgen.common.types cimport AST,ASTListView



from .asts cimport (
    VecLangProgram,
    VecLangInstruction,
    VecLangInstructionsSequence,
    ArithmeticExpressionLevel1,
    ArithmeticExpressionLevel2,
    ArithmeticExpressionLevel3,
    ArithmeticExpressionLevel4,
    Number,
    ComplexNumber,
    NumberExpression,
    VariableExpression,
    Components,
    Vector,
    Range,
    Indexing,
    Slicing,
    FunctionArgs,
    FunctionCall,
    FunctionDecl,
    FunctionDeclArgs,
    Type,
    int_number,
    float_number,
    variable,
    lp,
    rp,
    new_line,
    plus,
    minus,
    mod,
    mul,
    div,
    exp,
    eq,
    lc,
    rc,
    com,
    double_dot,
    sum_keyword,
    mean_keyword,
    dot_keyword,
    print_keyword,
    type_complex,
    type_float,
    type_int,
    type_vector,
    single_reductor,
    instructions_sequence_reductor,
    plus_reductor,
    minus_reductor,
    mul_reductor,
    div_reductor,
    mod_reductor,
    exp_reductor,
    assignment_reductor,
    extractor_reductor,
    number_reductor,
    variable_reductor,
    complex_number_reductor,
    vector_reductor,
    vector_components_reductor,
    range_reductor,
    range_reductor_1,
    range_reductor_2,
    range_reductor_3,
    indexing_reductor,
    slicing_reductor,
    function_call_reductor,
    function_args_reductor,
    built_in_function_call_reductor,
    function_declare_args_reductor,
    function_declare_reductor,
    type_reductor
)

cpdef BottomUpParser build_parser():
    cdef AttributedGrammar VecLangGrammar = AttributedGrammar(VecLangProgram) # type:ignore

    VecLangGrammar._add_attributed_production(VecLangProgram,[VecLangInstructionsSequence],single_reductor)

    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line,VecLangInstruction],instructions_sequence_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line],instructions_sequence_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstruction],instructions_sequence_reductor)

    VecLangGrammar._add_attributed_production(VecLangInstruction,[ArithmeticExpressionLevel1],single_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[FunctionDecl],single_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[VariableExpression,eq,ArithmeticExpressionLevel1],assignment_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[print_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,plus,ArithmeticExpressionLevel2],plus_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,minus,ArithmeticExpressionLevel2],minus_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel2],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mul,ArithmeticExpressionLevel3],mul_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,div,ArithmeticExpressionLevel3],div_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mod,ArithmeticExpressionLevel3],mod_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel3],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel3,exp,ArithmeticExpressionLevel4],exp_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel4],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[NumberExpression],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[VariableExpression],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Vector],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Indexing],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[FunctionCall],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[lp,ArithmeticExpressionLevel1,rp],extractor_reductor)

    VecLangGrammar._add_attributed_production(NumberExpression,[Number],single_reductor)
    VecLangGrammar._add_attributed_production(NumberExpression,[ComplexNumber],single_reductor)

    VecLangGrammar._add_attributed_production(Number,[int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[float_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[plus,int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[minus,int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[plus,float_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[minus,float_number],number_reductor)

    VecLangGrammar._add_attributed_production(ComplexNumber,[type_complex,lp,Number,com,Number,rp],complex_number_reductor)

    VecLangGrammar._add_attributed_production(VariableExpression,[variable],variable_reductor)

    VecLangGrammar._add_attributed_production(Vector,[lc,Components,rc],vector_reductor)
    VecLangGrammar._add_attributed_production(Vector,[lc,Range,rc],extractor_reductor)
    VecLangGrammar._add_attributed_production(Vector,[Slicing],single_reductor)

    VecLangGrammar._add_attributed_production(Components,[ArithmeticExpressionLevel1],vector_components_reductor)
    VecLangGrammar._add_attributed_production(Components,[Components,com,ArithmeticExpressionLevel1],vector_components_reductor)

    VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,int_number],range_reductor)
    VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,int_number],range_reductor_1)
    VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,minus,int_number],range_reductor_2)
    VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,minus,int_number],range_reductor_3)

    VecLangGrammar._add_attributed_production(Indexing,[VariableExpression,lc,int_number,rc],indexing_reductor)
    VecLangGrammar._add_attributed_production(Indexing,[Vector,lc,int_number,rc],indexing_reductor)

    VecLangGrammar._add_attributed_production(Slicing,[VariableExpression,lc,Range,rc],slicing_reductor)
    VecLangGrammar._add_attributed_production(Slicing,[Vector,lc,Range,rc],slicing_reductor)

    VecLangGrammar._add_attributed_production(FunctionCall,[VariableExpression,lp,FunctionArgs,rp],function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[sum_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[mean_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[dot_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)

    VecLangGrammar._add_attributed_production(FunctionArgs,[ArithmeticExpressionLevel1],function_args_reductor)
    VecLangGrammar._add_attributed_production(FunctionArgs,[FunctionArgs,com,ArithmeticExpressionLevel1],function_args_reductor)

    VecLangGrammar._add_attributed_production(FunctionDecl,[VariableExpression,lp,FunctionDeclArgs,rp,eq,ArithmeticExpressionLevel1],function_declare_reductor)

    VecLangGrammar._add_attributed_production(FunctionDeclArgs,[VariableExpression,double_dot,Type],function_declare_args_reductor)
    VecLangGrammar._add_attributed_production(FunctionDeclArgs,[FunctionDeclArgs,com,VariableExpression,double_dot,Type],function_declare_args_reductor)

    VecLangGrammar._add_attributed_production(Type,[type_complex],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_float],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_int],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_vector],type_reductor)

    return _build_lalr_parser_from_attributed(VecLangGrammar)
```

File: `parser.pyi`
```cython
from pylgen.parser.parser import BottomUpParser

def build_parser() -> BottomUpParser: ...
```

## Performance-Driven Changes

If you compare this VecLang implementation with the pure-Python arithmetic interpreter from earlier tutorial, you'll notice several differences. At first glance, the code looks more verbose and less "Pythonic". But every change has a purpose: **raw speed**. Let's break down the key transformations and why they matter.

> ### 1. Predefined Symbols Instead of Runtime Creation

Python version
```python
def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    # ...
```

Cython version
```cython
cdef Symbol plus = Symbol('+',True)
cdef Symbol minus = Symbol('-',True)
# ....


cdef Symbol get_symbol_function(object t, str tx):
    # ...
    if t == TokenTypeEnum.OPERATOR:
        return _operators[tx]
    # ...
```

**Why it's faster**: Object allocation is expensive, especially in the hot path of tokenisation. By pre-creating every possible symbol as a `cdef` variable, we eliminate millions of allocations when processing large files.

> ### 2. Separate Reductors per Operator Instead of a Single Conditional

Python version
```python
def binary_reductor(asts:ASTListView) -> AST:
    ast_type = None
    if asts[1].symbol == plus:
        ast_type = PlusAST
    # ...
```

Cython version
```cython
cdef AST plus_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return PlusAST(asts._get(0),asts._get(2),ast._line,ast._column)

cdef AST minus_reductor(ASTListView asts):
    cdef AST ast = asts._get(1)
    return MinusAST(asts._get(0),asts._get(2),ast._line,ast._column)

# ...
```

**Why it's faster**: Function call overhead is reduced, but more importantly, we avoid a runtime conditional chain that must be evaluated for every binary operation. In Cython, `cdef` functions are called with near-C speed, and the parser directly invokes the specific reductor for each production, so no dispatching logic is needed.

> ### 3. C-Level Access to AST Attributes

Python version
```python
class BinaryAST(AST):

    def __init__(self, left:AST,right:AST,symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
        self._left:AST = left
        self._right:AST = right
```

Cython version
```cython
cdef class BinaryAST(AST):
    cdef AST _left
    cdef AST _right
    cdef list[AST] _childs
```

**Why it's faster**: Declaring attributes as `cdef` makes them **direct C struct members**, bypassing Python's attribute dictionary lookup (`__dict__`). Accessing `ast._left` in a reductor becomes a simple memory offset, not a hash table lookup. This is particularly beneficial inside tight loops.

> ### 4. Strong Static Typing for Local Variables

Python version: no type annotations (or optional ones that are ignored at runtime).

Cython version:
```cython
cdef Token operator,number
cdef NumberAST ast
```

**Why it's faster**: Cython can generate C code that uses native C types (or fast Python object pointers) without boxing/unboxing. This reduces the overhead of dynamic type checking and allows optimisations.

> ### 5. Compilation to Native Code

The most obvious difference: all `.pyx` files are compiled to a C extension module. This means:

 - The parser, and reductors run as native machine code.
 - The Python interpreter is bypassed for the hot loops.
 - Memory management  can be more aggressive.

In contrast, the pure-Python version is interpreted line by line by the CPython bytecode evaluator.

> ### Does Every Change Improve Performance? (A Balanced View)

Yes, the overwhelming majority of these changes are **directly motivated by performance**. However, there are a few trade-offs:

 - **Readability**: The code is more verbose and less approachable for beginers. But for a production-grade interpreter that must handle millions of lines, readability takes a back seat to speed.
 - **Flexibility**: In Python, you can easily swap reductors or modify symbol mappings at runtime. In Cython, many of these structures are fixed at compile time, making the interpreter less dynamic. This is acceptable because VecLang's grammar is fixed.
 - **Compilation overhead**: You need a C compiler and Cython installed, and compilation takes extra time. This is a one-time cost for each deployment.

There is one change that is **not** primarily for speed: the use of **NumPy types** (`np.int64`,`np.float64`,`np.complex128`). While **NumPy** itself is highly optimised in C, the main reason we use it is to represent numbers in a way that enables efficent vectorised operations during evaluation (which is a separated stage). This is more about **correctness** and **feature richness** than about parsing performance.

> ### Conclusion

The transition from Python to Cython in VecLang is not cosmetic, it's a series of deliberate, performance-first decisions. We've traded some syntactic sugar for raw speed, and the results will speak for themselves. The approach is not necessary for every project, but when your interpreter must handle production-scale workloads, these are exactly the kinds of optimisations that make the difference between a toy and a tool.