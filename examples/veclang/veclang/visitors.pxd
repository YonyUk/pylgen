from pylgen.analysis.visitor cimport ASTChildrenSelector,ASTVisitor,ASTWalker,TraversalStrategy
from pylgen.analysis.context cimport Context
from pylgen.common.types cimport AST

from .asts cimport (
    FunctionArgsAST,
    FunctionDeclAST,
    FunctionCallAST
)

cdef class VecLangContext(Context):

    cdef set[str] _built_in_functions
    cdef dict[str,tuple[AST,list[tuple[str,str]]]] _functions
    cdef list[object] _var_values
    cdef list[type] _var_types
    cdef list[bint] _var_flags
    cdef dict[AST,RuntimeError] _runtime_errors
    cdef dict[str,int] _vars_index
    cdef list[object] _eval_stack
    cdef list[tuple[list[object],list[type],list[bint],dict[str,int],list[object]]] _scopes

    cdef tuple[bint,object] look_for_var(self,str var_name)

    cpdef void reset(self)

    cpdef void hard_reset(self)

cdef class PostOrderTraversalStrategy(TraversalStrategy):

    cdef list[tuple[AST,bint]] _stack

    cdef void set_function_scope(self,FunctionDeclAST func_ast, VecLangContext context)


cdef class PostOrderTraversalEvaluatorStrategy(TraversalStrategy):

    cdef list[tuple[AST,bint]] _stack

cdef class DefaultChildrenSelector(ASTChildrenSelector):
    pass

##########################################################################
#                        FUNCTION-COLLECTORS
##########################################################################
cdef class FunctionDeclASTCollectorVisitor(ASTVisitor):
    pass

##########################################################################
#                        ERROR-COLLECTORS
##########################################################################
cdef class FunctionCallASTErrorCollectorVisitor(ASTVisitor):
    
    cdef dict[str,object] _checkers

    cdef void _sum_checker(self,VecLangContext context,FunctionArgsAST args)

    cdef void _dot_checker(self,VecLangContext context, FunctionArgsAST args)

    cdef void _mean_checker(self,VecLangContext context,FunctionArgsAST args)

    cdef void _print_checker(self, VecLangContext context, FunctionArgsAST args)

    cdef void _check_call_loop(self,VecLangContext context, FunctionCallAST call)

cdef class VectorComponentsASTErrorCollector(ASTVisitor):
    pass

cdef class RangeASTErrorCollectorVisitor(ASTVisitor):
    pass

cdef class SlicingASTErrorCollectorVisitor(ASTVisitor):
    pass

cdef class IndexingASTErrorCollectorVisitor(ASTVisitor):
    pass

cdef class BinaryASTErrorCollectorVisitor(ASTVisitor):
    pass

cdef class DivASTErrorCollectorVisitor(BinaryASTErrorCollectorVisitor):
    pass

cdef class ModASTErrorCollectorVisitor(BinaryASTErrorCollectorVisitor):
    pass

##########################################################################
#                                 VARIABLE INDEXING VISITOR
##########################################################################

cdef class VariableIndexerVisitor(ASTVisitor):
    pass

##########################################################################
#                            EVALUATORS
##########################################################################

cdef class BinaryASTEvaluatorVisitor(ASTVisitor):
    
    cdef type _left_type # type:ignore
    cdef type _right_type # type:ignore
    cdef object _left_value
    cdef object _right_value
    cdef bint _runtime_error

cdef class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class AssigmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
    pass

cdef class FunctionCallASTEvaluatorVisitor(ASTVisitor):
    
    cdef dict[str,object] _evaluators

    cdef ASTWalker _evaluator

    cdef void _print(self,VecLangContext context,FunctionArgsAST args)

    cdef void _sum(self,VecLangContext context, FunctionArgsAST args)

    cdef void _dot(self,VecLangContext context, FunctionArgsAST args)

    cdef void _mean(self,VecLangContext context, FunctionArgsAST args)

cdef class VectorComponentsASTEvaluatorVisitor(ASTVisitor):
    pass

cdef class VectorASTEvaluatorVisitor(ASTVisitor):
    pass

cdef class RangeASTEvaluatorVisitor(ASTVisitor):
    pass

cdef class SlicingASTEvaluatorVisitor(ASTVisitor):
    pass

cdef class IndexingASTEvaluatorVisitor(ASTVisitor):
    pass

cdef class NumberASTEvaluetorVisitor(ASTVisitor):
    pass

cpdef tuple[VecLangContext,ASTWalker,ASTWalker] build_walkers()

cpdef object get_ast_value(AST ast,VecLangContext context)