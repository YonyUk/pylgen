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

cdef class AssigmentAST(BinaryAST):
    pass

cdef AST single_reductor(ASTListView asts)

cdef AST plus_reductor(ASTListView asts)

cdef AST minus_reductor(ASTListView asts)

cdef AST mul_reductor(ASTListView asts)

cdef AST div_reductor(ASTListView asts)

cdef AST mod_reductor(ASTListView asts)

cdef AST exp_reductor(ASTListView asts)

cdef AST assigment_reductor(ASTListView asts)

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