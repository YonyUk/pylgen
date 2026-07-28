# Step 3: Semantic Analysis and Evaluation

VecLang is far richer than a simple arithmetic language: it supports vectors, slicing, indexing, compex numbers, user-defined functions, and built-ins. This complexity demands a robust semantic framework. We'll build on the same **Visitor** and **Strategy** patterns we used before, but this time we'll leverage Cython to achieve near-native performance.

## Custom Runtime Errors (`errors.pxd`,`errors.pyx`)

VecLang defines a hierarchy of runtime errors, all inheriting from PyLGEN's `RuntimeError`. Each error carries a stack trace, line, column, and a descriptive message.

File: `errors.pxd`(declarations)
```cython
from pylgen.analysis.error cimport RuntimeError

cdef class DivisionByZeroError(RuntimeError):
    pass

cdef class ModuleByZeroError(RuntimeError):
    pass

cdef class UnSupportedOperationError(RuntimeError):
    pass

cdef class UnSupportedOperationForTypeError(UnSupportedOperationError):
    pass

cdef class UnSupportedOperationForTypesError(UnSupportedOperationError):
    pass

cdef class InvalidOperationError(RuntimeError):
    pass

cdef class BadRangeError(InvalidOperationError):
    pass

cdef class IndexOutOfRangeError(RuntimeError):
    pass
```

File: `errors.pyx`(implementations)
```cython
from pylgen.analysis.error cimport RuntimeError

cdef class DivisionByZeroError(RuntimeError):

    def __init__(self, list[str] stack_trace, int line, int column) -> None:
        super().__init__(stack_trace, line, column, 'Division by zero not allowed')

cdef class ModuleByZeroError(RuntimeError):
    def __init__(self, list[str] stack_trace, int line, int column) -> None:
        super().__init__(stack_trace, line, column, 'Module by zero not allowed')

cdef class UnSupportedOperationError(RuntimeError):

    def __init__(self, list[str] stack_trace, int line, int column, str msg) -> None:
        super().__init__(stack_trace, line, column, msg)

cdef class UnSupportedOperationForTypeError(UnSupportedOperationError):

    def __init__(self, list[str] stack_trace, int line, int column,str operation ,type _type) -> None:
        super().__init__(stack_trace, line, column, f'operation "{operation}" not supported for type {_type}')

cdef class UnSupportedOperationForTypesError(UnSupportedOperationError):
    
    def __init__(self, list[str] stack_trace, int line, int column,str operation ,type _type1,type _type2) -> None:
        super().__init__(stack_trace, line, column, f'operation ({_type1} "{operation}" {_type2}) not supported')

cdef class InvalidOperationError(RuntimeError):

    def __init__(self, list[str] stack_trace, int line, int column, str msg) -> None:
        super().__init__(stack_trace, line, column, msg)

cdef class BadRangeError(InvalidOperationError):

    def __init__(self, list[str] stack_trace, int line, int column) -> None:
        super().__init__(stack_trace, line, column, f'The args[1] < args[0] is not allowed')

cdef class IndexOutOfRangeError(RuntimeError):
    
    def __init__(self, list[str] stack_trace, int line, int column,int index, int size) -> None:
        super().__init__(stack_trace, line, column, f'Index {index} out of range (0-{size - 1})')
```

By keeping them as `cdef` classes, we avoid Python attribute lookups and make error creation cheap, important when processing millions of lines.

## The VecLangContext (Managing State)

The `VecLangContext` class (defined in `visitors.pyx`) is the central repository for all runtime state. It extends PyLGEN's `Context` and adds:

 - **Variables**: stored in parallel lists (`_var_values`,`_var_types`,`_var_flags`) and indexed by a dictionary `_vars_index` that maps variable names to integer indices. This is much faster than using a dictionary for values because we can access lists by index.
 - **Scopes**: a stack of scopes (`_scopes`). Each scope is a tuple of (`values`,`types`,`flags`,`index_map`,`eval_stack`). When we enter a function, we push a new scope; when we exit, we pop it.
 - **Functions**: a dictionary `_functions` mapping function names to a tuple of (`body_ast`,`list[(parameter_name,type_str)]`).
 - **Evaluation stack**: `_eval_stack` holds intermediate values during post-order traversal.
 - **Runtime errors**: a dictionary `_runtime_errors` mapping AST nodes to the error that occurred at that node (to avoid duplicate reports).
 - **Built-in functions**: a set `_built_in_functions` for `sum`,`mean`,`dot`, and `print`.

All attributes are declared as `cdef` to enable C-level access.

```cython
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
    cdef void assign_var(self,str var_name,object value)

    cpdef void reset(self)

    cpdef void hard_reset(self)
```

The context provides methods to look up variables (`look_for_var`), assign variables (`assign_var`), push/pop scopes, and manage errors. All methods are `cdef` for speed. This design is a direct performance upgrade over the pure-Python version, which did not support scopes.

## The Visitor Pattern in Cython

We use PyLGEN's visitor framework, but with a Cython twist: all visitors classes are `cdef` and their `visit` methods are `cpdef`. This allows them to be called from Cython code without Python function call overhead.

## Function Collector

Before the **semantic error collector** pass, we need to collect all functions defined by the user. This task is done by the `FunctionDeclASTCollectorVisitor` visitor. It scans the AST for function definitions and stores them in the context. This must happen before any function call checks. This visitor is registered in the `functions_collector` walker.

```cython
functions_collector.add_visitor_without_signature_checking(FunctionDeclAST,FunctionDeclASTCollectorVisitor())
```

## Semantic Error Collectors

After user-defined functions collection and before evaluation, we run a **semantic error collection** pass. These visitors detect issues that can be caught statically:

 - `FunctionCall ASTErrorCollectorVisitor`: verifies that called functions exist, that the argument count matches the signature, that arguments are declared variables (if they are variable references), and detects infinite recursion (calls that loop back to the same function).
 - `VectorComponentASTErrorCollector`: ensures that any variable used inside a vector literal has been declared.
 - `RangeASTErrorCollectorVisitor`: checks that the range's `min` <= `max`.
 - `SlicingASTErrorCollectorVisitor`: validates that slicing indices are within bounds of the target (if the target is a literal vector or range).
 - `IndexingASTErrorCollectorVisitor`: similar for indexing.
 - `BinaryASTErrorCollectorVisitor`: checks that variables used in binary operations are declared.
 - `DivASTErrorCollectorVisitor` and `ModASTErrorCollectorVisitor`: specialise for division and modulo, if the right operand is a literal zero, they raise a semantic error (division by zero).
 - `VariableIndexerVisitor`: when an assignment is encountered, it assigns an index to the variable in the context, preparing for fast lookup during evaluation.

All these visitors are registered in the `error_collector_walker`.

## Evaluator Visitors

The evaluator visitors perform the actual computation. They assume that all semantic checks have passed and that the context is properly initialised.

 - `NumberASTEvaluatorVisitor`: converts a `NumberAST` to a **NumPy** scalar (`np.int64`,`np.float64`, or `np.complex128`) and pushes it onto the evaluation stack.
 - `BinaryASTEvaluatorVisitor` (base class): fetches left and right values from the stack (or from variables), checks for errors, and stores them int `_left_value`, `_right_value`. Specific subclasses (`PlusASTEvaluatorVisitor`, `MinusASTEvaluatorVisitor`, `MulASTEvaluatorVisitor`,  `DivASTEvaluatorVisitor`, `ModASTEvaluatorVisitor`, `ExpASTEvaluatorVisitor`) perform the operation and push the result.
 - `AssignmentASTEvaluatorVisitor`: evaluates the right-hand side, then assigns the value to the variable using `context.assign_var`.
 - `VectorComponentsASTEvaluatorVisitor`: evaluates each component of a vector, collects them into a NumPy array, and pushes the array.
 - `RangeASTEvaluatorVisitor`: creates a NumPy array using `np.arange` and pushes it.
 - `SlicingASTEvaluatorVisitor`: applies a slice to a vector/range and pushes the result.
 - `IndexingASTEvaluatorVisitor`: extracts a single element from a vector/range.
 - `FunctionCallASTEvaluatorVisitor`: handles both built-in functions (`print`,`sum`,`dot`,`mean`) and user-defined functions. For built-ins, it directly computes the result. For user-defined functions, it pushes a new scope, evaluates the function body, and pops the scope, leaving the return value on the stack.

All these evaluator visitors are registered in the `evaluator_walker`.

!!! note
    All these AST node visitors are `cdef` and use typed local variables to avoid Python overhead. They also leverage NumPy's vectorised operations for speed.


## Traversal Strategies

We use two custom traversal strategies, both implementing post-order (children before parent) to ensure that values are available when a node is evaluated.

 - `PostOrderTraversalStrategy`: a standard post-order walk used for function collection and error collection. It uses a stack of `(node,processed)` flags.
 - `PostOrderTraversalEvaluatorStrategy`: similar, but it stops the traversal as soon as any runtime error is added to the context. This prevents cascading errors and saves time.

Both strategies are implemented in Cython with `cdef` methods and use efficent list operations. This strategy works with a **selector** to decide which children to visit. We use `DefaultChildrenSelector` for most nodes, but for `FunctionDeclAST` we use a custom selector that returns no children during function collection (so that function bodies are not checked until the semantic error collection).

## Building the Walkers

The `build_walkers()` function (in `visitors.pyx`) orchestrates everything. It creates a single `VecLangContext` and three `ASTWalker` instances:

 - `functions_collector`: uses `PostOrderTraversalStrategy` and the `FunctionDeclASTCollectorVisitor` to register all function definitions.
 - `error_collector_walker`: uses the same strategy but with all error-collector visitors. This pass performs static checks.
 - `evaluator_walker`: uses `PostOrderTraversalEvaluatorStrategy` and all evaluator visitors. This pass computes results.

All walkers share the same context, so variables and functions persist across passes.

```cython
cpdef tuple[VecLangContext,ASTWalker,ASTWalker,ASTWalker] build_walkers():
    cdef VecLangContext context = VecLangContext()
    cdef TraversalStrategy strategy = PostOrderTraversalStrategy()
    cdef TraversalStrategy eval_strategy = PostOrderTraversalEvaluatorStrategy()
    cdef ASTWalker error_collector_walker = ASTWalker(context,strategy) # type:ignore
    cdef ASTWalker functions_collector = ASTWalker(context,strategy) # type:ignore
    cdef ASTWalker evaluator_walker = ASTWalker(context,eval_strategy) # type:ignore
    # ...

    return context,error_collector_walker,functions_collector,evaluator_walker
```

## Getting the Final Value

After evaluation, we need to extract the result. The helper `get_ast_value(ast,context)`:

 - If the AST is a `VecLangInstructionSequenceAST`, it returns the value of the last instruction.
 - If it's a `VariableExpressionAST`, it looks up the variable in the context.
 - Otherwise, it returns `None` (or you could extend it).

This function is used byt the REPL to display the result.

> ### Recap

File: `visitors.pxd`
```cython
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
    cdef void assign_var(self,str var_name,object value)

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

cdef class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):
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

cpdef tuple[VecLangContext,ASTWalker,ASTWalker,ASTWalker] build_walkers()

cpdef object get_ast_value(AST ast,VecLangContext context)
```

File: `visitors.pyx`
```cython
from pylgen.analysis.visitor cimport ASTChildrenSelector,ASTVisitor,ASTWalker,TraversalStrategy
from pylgen.analysis.error cimport RuntimeError,SemanticError
from pylgen.analysis.context cimport Context
from pylgen.common.types cimport AST

import numpy as np # type:ignore

from .asts cimport (
    FunctionCallAST,
    SlicingAST,
    RangeAST,
    VectorAST,
    VectorComponentsAST,
    IndexingAST,
    BinaryAST,
    VariableExpressionAST,
    AssignmentAST,
    PlusAST,
    MinusAST,
    MulAST,
    DivAST,
    ModAST,
    ExpAST,
    NumberAST,
    VecLangInstructionsSequenceAST,
    FunctionArgsAST,
    FunctionDeclAST,
    FunctionDeclArgsAST,
    TypeAST,
    VariableExpression,
    FunctionDecl,
    FunctionCall,
    Vector,
    Range,
    Slicing,
    Number,
    NumberExpression,
    eq
)

from .errors cimport(
    DivisionByZeroError,
    UnSupportedOperationForTypesError,
    ModuleByZeroError,
    BadRangeError,
    InvalidOperationError,
    IndexOutOfRangeError
)

cdef class VecLangContext(Context):

    def __init__(self) -> None:
        super().__init__()
        self._built_in_functions = { 
            'sum',
            'dot',
            'mean',
            'print',
        }
        self._functions = {}
        self._var_flags = []
        self._var_values = []
        self._scopes = []
        self._eval_stack = []
        self._runtime_errors = {}
        self._vars_index = {}
        self._var_types = []
    
    cpdef void reset(self):
        super(VecLangContext,self).reset()
        self._var_flags.clear()
        self._var_values.clear()
        self._scopes.clear()
        self._eval_stack.clear()
        self._vars_index.clear()
        self._var_types.clear()
    
    cpdef void hard_reset(self):
        self.reset()
        self._functions.clear()

    cdef tuple[bint,object] look_for_var(self,str var_name):
        cdef int idx
        cdef int length = len(self._scopes)
        cdef tuple[list[object],list[type],list[bint],dict[str,int],list[object]] scope
        cdef list[object] values
        cdef dict[str,int] idxs

        if var_name in self._vars_index:
            return True, self._var_values[self._vars_index[var_name]]

        for idx in range(length - 1, -1, -1):
            scope = self._scopes[idx]
            values,_,_,idxs,_ = scope
            if var_name in idxs:
                return True, values[idxs[var_name]]
        
        return False,None
    
    cdef void assign_var(self,str var_name,object value):
        cdef int idx,tidx
        cdef int length = len(self._scopes)
        cdef tuple[list[object],list[type],list[bint],dict[str,int],list[object]] scope
        cdef list[object] values
        cdef list[type] types
        cdef list[bint] flags
        cdef dict[str,int] idxs
        cdef list[object] stack

        if var_name in self._vars_index:
            idx = self._vars_index[var_name]
            self._var_flags[idx] = True # type:ignore
            self._var_types[idx] = type(value)
            self._var_values[idx] = value
        else:
            for idx in range(length - 1, -1, -1):
                scope = self._scopes[idx]
                values,types,flags,idxs,stack = scope
                if var_name in idxs:
                    tidx = idxs[var_name]
                    values[tidx] = value
                    flags[tidx] = True # type:ignore
                    types[tidx] = type(value)
                    scope = (values,types,flags,idxs,stack)
                    self._scopes[idx] = scope
                    break

    cpdef list[RuntimeError] get_runtime_errors(self):
        return list(self._runtime_errors.values()) # type:ignore
    
    cpdef void clear_runtime_errors(self):
        self._runtime_errors.clear()

    cpdef void push_new_scope(self):
        cdef tuple[list[object],list[type],list[bint],dict[str,int],list[object]] new_scope
        new_scope = (self._var_values,self._var_types,self._var_flags,self._vars_index,self._eval_stack)
        self._scopes.append(new_scope)
        self._var_values = []
        self._var_types = []
        self._var_flags = []
        self._vars_index = {}
    
    cpdef void pop_scope(self):
        cdef tuple[dict[str,AST],list[object],list[type],list[bint],dict[str,int],list[object]] new_scope
        new_scope = self._scopes.pop()
        self._var_values,self._var_types,self._var_flags,self._vars_index,self._eval_stack = new_scope
        
    cpdef void add_runtime_error(self, AST ast,RuntimeError error):
        if not ast in self._runtime_errors:
            self._runtime_errors[ast] = error # type:ignore

cdef class PostOrderTraversalStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
        self._stack = []
    
    cdef void set_function_scope(self,FunctionDeclAST func_ast, VecLangContext context):
        cdef tuple[AST,list[tuple[str,str]]] func_scope
        cdef str var_name,var_type
        cdef int var_index

        if func_ast._name in context._functions:
            func_scope = context._functions[func_ast._name]
            
            for var_name,var_type in func_scope[1]: # type:ignore
                var_index = len(context._vars_index)
                context._vars_index[var_name] = var_index
                context._var_flags.append(False) # type:ignore
                context._var_values.append(None)
                if var_type == 'int':
                    context._var_types.append(np.int64)
                elif var_type == 'float':
                    context._var_types.append(np.float64)
                elif var_type == 'complex':
                    context._var_types.append(np.complex128)
                else:
                    context._var_types.append(np.ndarray)
    
    cpdef void init(self,AST root):
        super(PostOrderTraversalStrategy,self).init(root)
        self._stack.append((root,False))
    
    cpdef bint has_next(self):
        return len(self._stack) > 0 # type:ignore

    cpdef AST current(self,Context context):

        cdef AST node
        cdef bint processed
        cdef ASTChildrenSelector selector
        cdef list[AST] children
        cdef int idx

        while self._stack:
            node,processed = self._stack.pop()
            if processed:
                if node._symbol == FunctionDecl:
                    context.pop_scope()
                return node

            if node._symbol == FunctionDecl:
                context.push_new_scope()
                self.set_function_scope(node,context) # type:ignore

            self._stack.append((node,True))
            selector = self._get_selector(node) # type:ignore
            children = selector.select_children(node,context)
            for idx in range(len(children) - 1,-1,-1):
                self._stack.append((children[idx],False))
        return None # type:ignore
    
    cpdef void reset(self):
        self._stack.clear()

cdef class PostOrderTraversalEvaluatorStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
        self._stack = []

    cpdef void init(self,AST root):
        super(PostOrderTraversalEvaluatorStrategy,self).init(root)
        self._stack.append((root,False))
    
    cpdef bint has_next(self):
        return len(self._stack) > 0 # type:ignore

    cpdef AST current(self,Context context):

        cdef AST node
        cdef bint processed
        cdef ASTChildrenSelector selector
        cdef list[AST] children
        cdef int idx

        while self._stack:
            if (<VecLangContext>context)._runtime_errors:
                self._stack.clear()
                break
            node,processed = self._stack.pop()
            if processed:
                return node

            self._stack.append((node,True))
            selector = self._get_selector(node) # type:ignore
            children = selector.select_children(node,context)
            for idx in range(len(children) - 1,-1,-1):
                self._stack.append((children[idx],False))
        return None # type:ignore
    
    cpdef void reset(self):
        self._stack.clear()

cdef class DefaultChildrenSelector(ASTChildrenSelector):
    
    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef list[AST] select_children(self,AST ast,Context context):
        self._check_context_type(context)
        return ast.children()

cdef class FunctionDeclASTChildrenSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef list[AST] select_children(self, AST ast, Context context):
        self._check_context_type(context)
        return []

cdef class FunctionDeclASTCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):
        cdef FunctionDeclAST func = ast # type:ignore
        cdef FunctionDeclArgsAST args = func._args
        cdef VariableExpressionAST var
        cdef str var_type
        cdef tuple[AST,list[tuple[str,str]]] function_base_context
        cdef list[tuple[str,str]] arg_vars = []

        for var,var_type in args._args.items():
            arg_vars.append((var._name,var_type))

        self._check_context_type(context)
        function_base_context = (func._body,arg_vars)
        (<VecLangContext>context)._functions[func._name] = (func._body,arg_vars)

cdef class FunctionCallASTErrorCollectorVisitor(ASTVisitor):
    
    def __init__(self) -> None:
        super().__init__(VecLangContext)
        self._checkers = {
            'sum':self._sum_checker,
            'dot':self._dot_checker,
            'mean':self._mean_checker,
            'print':self._print_checker
        }
    
    cdef void _print_checker(self, VecLangContext context, FunctionArgsAST args):
        cdef SemanticError error
        cdef AST arg
        cdef VariableExpressionAST var

        if len(args._args) != 1:
            error = SemanticError(f'Wrong number of args: got {len(args._args)}, expected 1',args._line,args._column) # type:ignore
            context.add_semantic_error(error)
        
        if len(args._args) < 1:
            return # type:ignore

        arg = args._args[0]

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error)

    cdef void _mean_checker(self,VecLangContext context, FunctionArgsAST args):
        cdef SemanticError error
        cdef AST arg
        cdef VariableExpressionAST var

        if len(args._args) != 1:
            error = SemanticError(f'Wrong number of args: got {len(args._args)}, expected 1',args._line,args._column) # type:ignore
            context.add_semantic_error(error)
        
        if len(args._args) < 1:
            return # type:ignore

        arg = args._args[0]

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error)
    
    cdef void _dot_checker(self,VecLangContext context, FunctionArgsAST args):
        cdef SemanticError error
        cdef AST arg
        cdef VariableExpressionAST var

        if len(args._args) != 2:
            error = SemanticError(f'Wrong number of args: got {len(args._args)}, expected 2',args._line,args._column) # type:ignore
            context.add_semantic_error(error)

        if len(args._args) < 1:
            return # type:ignore

        arg = args._args[0]

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error)

        if len(args._args) < 2:
            return # type:ignore

        arg = args._args[1]

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error)

    cdef void _sum_checker(self,VecLangContext context, FunctionArgsAST args):
        cdef SemanticError error
        cdef AST arg
        cdef VariableExpressionAST var

        if len(args._args) != 1:
            error = SemanticError(f'Wrong number of args: got {len(args._args)}, expected 1',args._line,args._column) # type:ignore
            context.add_semantic_error(error)

        arg = args._args[0]

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error)

    cdef void _check_call_loop(self,VecLangContext context, FunctionCallAST call):
        cdef AST func_body
        cdef tuple[AST,list[tuple[str,str]]] func_data
        cdef list[AST] asts,seens
        cdef AST child,current
        cdef SemanticError error
        cdef FunctionCallAST func_call

        func_data = (<VecLangContext>context)._functions[call._function_name]
        func_body,_ = func_data

        asts = [func_body]
        seens = []

        while asts:

            current = asts.pop()
            seens.append(current)

            for child in current.children():
                if child._symbol == FunctionCall:
                    func_call = <FunctionCallAST>child # type:ignore
                    if func_call._function_name == call._function_name:
                        error = SemanticError(f'Infinite loop call detected for function {call._function_name}',child._line,child._column) # type:ignore
                        if not error in context._errors:
                            context.add_semantic_error(error)

                    func_data = (<VecLangContext>context)._functions[func_call._function_name]
                    func_body,_ = func_data
                    
                    if not func_body in seens:
                        asts.append(func_body)

                if not child in seens:
                    asts.append(child)

    cpdef void visit(self, AST ast,Context context):
        cdef SemanticError error
        cdef FunctionCallAST func = ast # type:ignore
        cdef tuple[AST,list[tuple[str,str]]] func_data
        cdef FunctionArgsAST args
        cdef list[tuple[str,str]] func_signature
        cdef AST func_body
        cdef VariableExpressionAST var_arg
        cdef AST arg
        cdef int idx,sig_args_len,args_len

        self._check_context_type(context)
        if not (func._function_name in (<VecLangContext>context)._functions or func._function_name in (<VecLangContext>context)._built_in_functions):
            error = SemanticError(f'function {func._function_name} doesn\'t exists',func._line,func._column) # type:ignore
            context.add_semantic_error(error)
        
        if func._function_name in self._checkers:
            self._checkers[func._function_name](context,func._args) # type:ignore
        elif func._function_name == 'print':
            pass
        else:

            if not func._function_name in (<VecLangContext>context)._functions:
                return # type:ignore
            
            self._check_call_loop(context,func) # type:ignore
            
            func_data = (<VecLangContext>context)._functions[func._function_name]
            func_body,func_signature = func_data
            args = func._args
            sig_args_len = len(func_signature)
            args_len = len(args._args)
            args = func._args
            if args_len != sig_args_len:
                error = SemanticError(f'Wrong number of args: got {args_len}, expected {sig_args_len}',args._line,args._column) # type:ignore
                context.add_semantic_error(error)

            for idx in range(args_len):
                arg = args._args[idx]
                param_type_tuple = func_signature[idx]
                if arg._symbol == VariableExpression:
                    var_arg = arg # type:ignore
                    if not (<VecLangContext>context).look_for_var(var_arg._name)[0]:
                        error = SemanticError(f'Undeclared variable "{var_arg._name}"',var_arg._line,var_arg._column) # type:ignore
                        context.add_semantic_error(error)

cdef class VectorComponentsASTErrorCollector(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):
        cdef VectorComponentsAST components = ast # type:ignore
        cdef VariableExpressionAST var
        cdef AST component
        cdef int idx
        cdef int length = len(components._components)
        cdef SemanticError error

        self._check_context_type(context)

        for idx in range(length):
            component = components._components[idx]
            if component._symbol == VariableExpression:
                var = component # type:ignore
                if not (<VecLangContext>context).look_for_var(var._name)[0]:
                    error = SemanticError(f'Undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                    context.add_semantic_error(error)

cdef class RangeASTErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast,Context context):
        cdef RangeAST _range = ast # type:ignore

        self._check_context_type(context)

        if _range._max < _range._min:
            context.add_runtime_error(ast,BadRangeError(context._stack,_range._line,_range._column)) # type:ignore    

cdef class SlicingASTErrorCollectorVisitor(ASTVisitor):
    
    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast,Context context):
        cdef SemanticError error1,error2
        cdef SlicingAST slice = ast # type:ignore
        cdef AST target = slice._target
        cdef RangeAST _range = slice._range
        cdef VectorComponentsAST components
        cdef RangeAST inner_range
        cdef VariableExpressionAST var

        self._check_context_type(context)
        if _range._min < 0:
            error1 = SemanticError(f'min index can\'t be less than 0',_range._line,_range._column) # type:ignore
            context.add_semantic_error(error1)
        if target._symbol == Vector:
            components = (<VectorAST>target)._components
            if _range._max > len(components._components):
                error2 = SemanticError(f'max index can\'t be greater than vector size',_range._line,_range._column) # type:ignore
                context.add_semantic_error(error2)
        elif target._symbol == Range:
            if _range._max > (<RangeAST>target)._max - (<RangeAST>target)._min:
                error2 = SemanticError(f'max index can\'t be greater than range size',_range._line,_range._column) # type:ignore
                context.add_semantic_error(error2)
        elif target._symbol == Slicing:
            inner_range = (<SlicingAST>target)._range
            if _range._max > inner_range._max - inner_range._min:
                error2 = SemanticError(f'max index can\'t be greater than range size',_range._line,_range._column) # type:ignore
                context.add_semantic_error(error2)
        elif target._symbol == VariableExpression:
            var = target # type:ignore
            if not (<VecLangContext>context).look_for_var(var._name)[0]:
                error2 = SemanticError(f'undeclared variable "{var._name}"',var._line,var._column) # type:ignore
                context.add_semantic_error(error2)

cdef class IndexingASTErrorCollectorVisitor(ASTVisitor):
    
    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):
        cdef SemanticError error
        cdef IndexingAST indexing = ast # type:ignore
        cdef AST target = indexing._target
        cdef VectorComponentsAST components

        self._check_context_type(context)
        if target._symbol == Vector:
            components = (<VectorAST>target)._components
            if indexing._index > len(components._components) - 1 or indexing._index < 0:
                error = SemanticError(f'index out of range',indexing._line,indexing._column) # type:ignore
                context.add_semantic_error(error)
        elif target._symbol == Range:
            if indexing._index < 0 or indexing._index > (<RangeAST>target)._max - (<RangeAST>target)._min - 1:
                error = SemanticError(f'index out of range',indexing._line,indexing._column) # type:ignore
                context.add_semantic_error(error)

cdef class BinaryASTErrorCollectorVisitor(ASTVisitor):
    
    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self, AST ast, Context context):
        cdef SemanticError error1,error2
        cdef BinaryAST op = ast # type:ignore
        cdef VecLangContext _context = context # type:ignore
        cdef VariableExpressionAST var

        self._check_context_type(context)
        if op._left._symbol == VariableExpression:
            var = op._left # type:ignore
            if op._symbol != eq:
                if not _context.look_for_var(var._name)[0]:
                    error1 = SemanticError(f'variable "{var._name}" doesn\'t exists',var._line,var._column) # type:ignore
                    context.add_semantic_error(error1)

        if op._right._symbol == VariableExpression:
            var = op._right # type:ignore
            if not _context.look_for_var(var._name)[0]:
                error2 = SemanticError(f'variable "{var._name}" doesn\'t exists',var._line,var._column) # type:ignore
                context.add_semantic_error(error2)

cdef class DivASTErrorCollectorVisitor(BinaryASTErrorCollectorVisitor):

    cpdef void visit(self,AST ast, Context context):
        cdef SemanticError error
        cdef DivAST div = ast # type:ignore
        cdef NumberAST number
        cdef object value

        super(DivASTErrorCollectorVisitor,self).visit(ast,context)
        if div._right._symbol == Number:
            number = div._right # type:ignore
            if number._type == np.complex128: # type:ignore
                value = np.complex128(number._value)
            elif number._type == np.float64: # type:ignore
                value = np.float64(number._value)
            else:
                value = np.int64(number._value)
            if value == 0: # type:ignore
                error = SemanticError('division by zero not allowed',div._line,div._column) # type:ignore
                context.add_semantic_error(error)

cdef class ModASTErrorCollectorVisitor(BinaryASTErrorCollectorVisitor):

    cpdef void visit(self,AST ast, Context context):
        cdef SemanticError error1,error2
        cdef ModAST mod = ast # type:ignore
        cdef NumberAST left,right
        cdef object value

        super(ModASTErrorCollectorVisitor,self).visit(ast,context)
        if mod._left._symbol == Number:
            left = mod._left # type:ignore
            if left._type == np.complex128: # type:ignore
                error1 = SemanticError('operation not supported for complex numbers',mod._line,mod._column) # type:ignore
                context.add_semantic_error(error1)
        if mod._right._symbol == Number:
            right = mod._right # type:ignore
            if right._type == np.complex128: # type:ignore
                error2 = SemanticError('operation not supported for complex numbers',mod._line,mod._column) # type:ignore
                context.add_semantic_error(error2)
        
            if right._type == np.complex128: # type:ignore
                value = np.complex128(right._value)
            elif right._type == np.float64: # type:ignore
                value = np.float64(right._value)
            else:
                value = np.int64(right._value)
        
            if value == 0: # type:ignore
                error1 = SemanticError('module by zero not allowed',mod._line,mod._column) # type:ignore
                context.add_semantic_error(error1)

cdef class VariableIndexerVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast,Context context):
        cdef AssignmentAST assignment = ast # type:ignore
        cdef VariableExpressionAST var = assignment._left # type:ignore
        cdef int idx

        if not (<VecLangContext>context).look_for_var(var._name)[0]:
            idx = len((<VecLangContext>context)._var_values)
            (<VecLangContext>context)._vars_index[var._name] = idx
            (<VecLangContext>context)._var_flags.append(False) # type:ignore
            (<VecLangContext>context)._var_values.append(None)
            (<VecLangContext>context)._var_types.append(None) # type:ignore
            var._index = idx

cdef class NumberASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext) # type:ignore
    
    cpdef void visit(self,AST ast, Context context):
        cdef NumberAST number = ast # type:ignore
        
        self._check_context_type(context)
        (<VecLangContext>context)._eval_stack.append(number._type(number._value)) # type:ignore

cdef class BinaryASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
        self._runtime_error = False # type:ignore
    
    cpdef void visit(self,AST ast, Context context):
        cdef BinaryAST binary = ast # type:ignore
        cdef VariableExpressionAST var
        cdef NumberAST number
        cdef RuntimeError error

        self._check_context_type(context)
        if binary._right._symbol == VariableExpression:
            var = binary._right # type:ignore
            self._right_value = (<VecLangContext>context).look_for_var(var._name)[1]
        else:
            self._right_value = (<VecLangContext>context)._eval_stack.pop()
        self._right_type = type(self._right_value)
        
        if binary._left._symbol == VariableExpression:
            var = binary._left # type:ignore
            self._left_value = (<VecLangContext>context).look_for_var(var._name)[1]
        else:
            self._left_value = (<VecLangContext>context)._eval_stack.pop()
        self._left_type = type(self._left_value)
        if self._left_type == self._right_type and self._left_type == np.ndarray:
            if self._left_value.shape != self._right_value.shape: # type:ignore
                error = InvalidOperationError(context._stack,ast._line,ast._column,'Vectors operands must have same size') # type:ignore
                context.add_runtime_error(ast,error)
                self._runtime_error = True # type:ignore

cdef class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):
        cdef AssignmentAST assignment = ast # type:ignore
        cdef VariableExpressionAST var = assignment._left # type:ignore

        super(AssignmentASTEvaluatorVisitor,self).visit(ast,context)
        (<VecLangContext>context).assign_var(var._name,self._right_value)

cdef class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):

        super(PlusASTEvaluatorVisitor,self).visit(ast,context)
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            (<VecLangContext>context)._eval_stack.append(self._left_value + self._right_value) # type:ignore

cdef class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):

        super(MinusASTEvaluatorVisitor,self).visit(ast,context)
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            (<VecLangContext>context)._eval_stack.append(self._left_value - self._right_value) # type:ignore

cdef class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):

        super(MulASTEvaluatorVisitor,self).visit(ast,context)
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            (<VecLangContext>context)._eval_stack.append(self._left_value * self._right_value) # type:ignore

cdef class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):
        cdef int line,column
        cdef RuntimeError error
        
        super(DivASTEvaluatorVisitor,self).visit(ast,context)
        
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            if self._right_value == 0:
                line = (<AST>ast)._line
                column = (<AST>ast)._column
                error = DivisionByZeroError(context._stack,line,column) # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            else:
                (<VecLangContext>context)._eval_stack.append(self._left_value / self._right_value) # type:ignore

cdef class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast,Context context):
        cdef int line,column
        cdef RuntimeError error

        super(ModASTEvaluatorVisitor,self).visit(ast,context)
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            if self._left_type == np.complex128 or self._right_type == np.complex128:
                line = (<AST>ast)._line
                column = (<AST>ast)._column
                error = UnSupportedOperationForTypesError(context._stack,line,column,"%",self._left_type,self._right_type) # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            elif self._right_value == 0:
                line = (<AST>ast)._line
                column = (<AST>ast)._column
                error = ModuleByZeroError(context._stack,line,column) # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            else:
                (<VecLangContext>context)._eval_stack.append(self._left_value % self._right_value) # type:ignore

cdef class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    cpdef void visit(self,AST ast, Context context):
        cdef int line,column

        super(ExpASTEvaluatorVisitor,self).visit(ast,context)
        if self._left_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if self._right_value is None:
            (<VecLangContext>context)._eval_stack.append(None)
            self._runtime_error = True # type:ignore
        if not self._runtime_error:
            (<VecLangContext>context)._eval_stack.append(self._left_value ** self._right_value) # type:ignore

cdef class VectorComponentsASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self, AST ast, Context context):
        cdef int line,column
        cdef RuntimeError error
        cdef VectorComponentsAST components = ast # type:ignore
        cdef int length = len(components._components)
        cdef int idx
        cdef AST component
        cdef VariableExpressionAST var
        cdef VecLangContext _context
        cdef object value
        cdef str type_name
        cdef list values = [0] * length

        self._check_context_type(context)
        _context = context # type:ignore

        for idx in range(length - 1 ,-1,-1):
            component = components._components[idx]
            if component._symbol == VariableExpression:
                var = component # type:ignore
                value = _context.look_for_var(var._name)[1]
                if value is None:
                    continue
                else:
                    values[idx] = value # type:ignore
            else:
                value = _context._eval_stack.pop()
                if value is None:
                    continue
                else:
                    values[idx] = value # type:ignore
        
        (<VecLangContext>context)._eval_stack.append(np.array(values))

cdef class VectorASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):

        self._check_context_type(context)

cdef class RangeASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):
        cdef RangeAST _range = ast # type:ignore

        self._check_context_type(context)

        _components = np.arange(_range._min,_range._max,dtype=np.int64)
        (<VecLangContext>context)._eval_stack.append(_components)

cdef class SlicingASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)

    cpdef void visit(self,AST ast, Context context):
        cdef SlicingAST slice = ast # type:ignore
        cdef RangeAST _range = slice._range
        cdef AST target = slice._target
        cdef object value
        cdef VariableExpressionAST var
        cdef type var_type # type:ignore
        cdef RuntimeError error

        self._check_context_type(context)

        (<VecLangContext>context)._eval_stack.pop()
        if target._symbol == Vector or target._symbol == Range or target._symbol == Slicing:
            components = (<VecLangContext>context)._eval_stack.pop()
            (<VecLangContext>context)._eval_stack.append(components[_range._min:_range._max]) # type:ignore
        elif target._symbol == VariableExpression:
            var = target # type:ignore
            value = (<VecLangContext>context).look_for_var(var._name)[1]
            var_type = type(value)
            if var_type != np.ndarray:
                error = InvalidOperationError(context._stack,slice._line,slice._column,f'Slicing operation not supported for type "{var_type}"') # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            elif _range._max >= len(value): # type:ignore
                error = InvalidOperationError(context._stack,slice._line,slice._column,f'max index is greater than vector size {len(value)}') # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            else:
                (<VecLangContext>context)._eval_stack.append(value[_range._min:_range._max]) # type:ignore

cdef class IndexingASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(VecLangContext)
    
    cpdef void visit(self,AST ast, Context context):
        cdef IndexingAST indexing = ast # type:ignore
        cdef AST target = indexing._target
        cdef VariableExpressionAST var
        cdef object value
        cdef type var_type # type:ignore
        cdef RuntimeError error

        self._check_context_type(context)

        if target._symbol == VariableExpression:
            var = target # type:ignore
            value = (<VecLangContext>context).look_for_var(var._name)[1]
            var_type = type(value)
            if var_type != np.ndarray:
                error = InvalidOperationError(context._stack,indexing._line,indexing._column,f'Indexing operation not supported for type "{var_type}"') # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            elif indexing._index >= len(value): # type:ignore
                error = IndexOutOfRangeError(context._stack,indexing._line,indexing._column,indexing._index,len(value)) # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            else:
                (<VecLangContext>context)._eval_stack.append(value[indexing._index]) # type:ignore
        elif target._symbol == Vector or target._symbol == Range or target._symbol == Slicing:
            components = (<VecLangContext>context)._eval_stack.pop()
            if indexing._index >= len(components): # type:ignore
                error = IndexOutOfRangeError(context._stack,indexing._line,indexing._column,indexing._index,len(components)) # type:ignore
                (<VecLangContext>context).add_runtime_error(ast,error)
                (<VecLangContext>context)._eval_stack.append(None)
            else:
                (<VecLangContext>context)._eval_stack.append(components[indexing._index]) # type:ignore

cdef class FunctionCallASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        cdef TraversalStrategy eval_strategy = PostOrderTraversalEvaluatorStrategy()
        
        super().__init__(VecLangContext)
        self._evaluators = {
            'print':self._print,
            'sum':self._sum,
            'dot':self._dot,
            'mean':self._mean
        }
    
        eval_strategy.set_default_selector_without_signature_checking(DefaultChildrenSelector()) # type:ignore
        eval_strategy.add_selector_without_signature_checking(FunctionDeclAST,FunctionDeclASTChildrenSelector()) # type:ignore
        
        self._evaluator = ASTWalker(VecLangContext(),eval_strategy) # type:ignore

        self._evaluator.add_visitor_without_signature_checking(NumberAST,NumberASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(AssignmentAST,AssignmentASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(PlusAST,PlusASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(MinusAST,MinusASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(MulAST,MulASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(DivAST,DivASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(ModAST,ModASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(ExpAST,ExpASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(VectorComponentsAST,VectorComponentsASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(VectorAST,VectorASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(RangeAST,RangeASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(SlicingAST,SlicingASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(IndexingAST,IndexingASTEvaluatorVisitor())
        self._evaluator.add_visitor_without_signature_checking(FunctionCallAST,self)

    cdef void _mean(self,VecLangContext context, FunctionArgsAST args):
        cdef AST arg
        cdef RuntimeError error
        cdef VariableExpressionAST var
        cdef type var_type # type:ignore
        cdef object val,var_val

        arg = args._args[0]
        
        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            var_val = context.look_for_var(var._name)[1]
            var_type = type(var_val)
            if var_type != np.ndarray and not var_val is None:
                error = InvalidOperationError(context._stack,arg._line,arg._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg,error)
                val = None
            else:
                val = var_val
        else:
            val = context._eval_stack.pop()
            var_type = type(val)
            if var_type != np.ndarray and not val is None:
                error = InvalidOperationError(context._stack,arg._line,arg._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg,error)
        
        if val is None:
            context._eval_stack.append(None)
        else:
            context._eval_stack.append(float(np.mean(val)))

    cdef void _dot(self,VecLangContext context, FunctionArgsAST args):
        cdef AST arg1,arg2
        cdef RuntimeError error
        cdef VariableExpressionAST var
        cdef type var_type # type:ignore
        cdef object val1,val2,var_val

        arg1 = args._args[0]
        arg2 = args._args[1]

        if arg2._symbol == VariableExpression:
            var = arg2 # type:ignore
            var_val = context.look_for_var(var._name)[1]
            var_type = type(var_val)
            if var_type != np.ndarray and not var_val is None:
                error = InvalidOperationError(context._stack,arg2._line,arg2._column,f'arg2 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg2,error)
                val2 = None
            else:
                val2 = context.look_for_var(var._name)[1]
        else:
            val2 = context._eval_stack.pop()
            var_type = type(val2)
            if var_type != np.ndarray and not val2 is None:
                error = InvalidOperationError(context._stack,arg2._line,arg2._column,f'arg2 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg1,error)
        
        if arg1._symbol == VariableExpression:
            var = arg1 # type:ignore
            var_val = context.look_for_var(var._name)[1]
            var_type = type(var_val)
            if var_type != np.ndarray and not var_val is None:
                error = InvalidOperationError(context._stack,arg1._line,arg1._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg1,error)
                val1 = None
            else:
                val1 = context.look_for_var(var._name)[1]
        else:
            val1 = context._eval_stack.pop()
            var_type = type(val1)
            if var_type != np.ndarray and not val1 is None:
                error = InvalidOperationError(context._stack,arg1._line,arg1._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg1,error)
        
        if val1 is None:
            context._eval_stack.append(None)
        elif val2 is None:
            context._eval_stack.append(None)
        else:
            if val1.shape != val2.shape: # type:ignore
                error = InvalidOperationError(context._stack,arg2._line,arg2._column,f'dot product invalid; vectors must have the same size') # type:ignore
                context.add_runtime_error(args,error)
                context._eval_stack.append(None)
            else:
                context._eval_stack.append(np.dot(val1,val2))

    cdef void _sum(self,VecLangContext context,FunctionArgsAST args):
        cdef AST arg
        cdef RuntimeError error
        cdef VariableExpressionAST var
        cdef type var_type # type:ignore
        cdef object val,var_val

        arg = args._args[0]
        
        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            var_val = context.look_for_var(var._name)[1]
            var_type = type(var_val)
            if var_type != np.ndarray and not var_val is None:
                error = InvalidOperationError(context._stack,arg._line,arg._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg,error)
                val = None
            else:
                val = var_val
        else:
            val = context._eval_stack.pop()
            var_type = type(val)
            if var_type != np.ndarray and not val is None:
                error = InvalidOperationError(context._stack,arg._line,arg._column,f'arg1 must be of type "Vector"; got {var_type}') # type:ignore
                context.add_runtime_error(arg,error)
        
        if val is None:
            context._eval_stack.append(None)
        else:
            context._eval_stack.append(np.sum(val))

    cdef void _print(self,VecLangContext context,FunctionArgsAST args):
        cdef AST arg = args._args[0]
        cdef VariableExpressionAST var
        cdef object val

        if context._runtime_errors:
            return # type:ignore

        if arg._symbol == VariableExpression:
            var = arg # type:ignore
            print(context.look_for_var(var._name)[1])
        else:
            val = context._eval_stack[-1]
            if not val is None:
                print(val)

    cpdef void visit(self,AST ast, Context context):
        cdef FunctionCallAST call = ast # type:ignore
        cdef FunctionArgsAST args = call._args
        cdef RuntimeError error
        cdef AST func_body
        cdef list[tuple[str,str]] func_signature
        cdef int idx,call_var_arg_index
        cdef tuple[str,str] param_type_tuple
        cdef bint runtime_error = False # type:ignore
        cdef object  arg_value
        cdef type arg_type
        cdef AST arg
        cdef VariableExpressionAST var
        cdef list[object] arguments = [None] * len(args._args)

        self._check_context_type(context)


        for idx in range(len(args._args)):
            arg = args._args[idx]
            if arg._symbol == VariableExpression:
                var = arg # type:ignore
                arguments[idx] = (<VecLangContext>context).look_for_var(var._name)[1]
            else:
                arguments[idx] = (<VecLangContext>context)._eval_stack.pop()
        
        (<VecLangContext>context).push_new_scope()
        (<VecLangContext>context).push_trace(call._function_name)
        (<VecLangContext>context)._eval_stack.extend(arguments)

        if call._function_name in (<VecLangContext>context)._built_in_functions:
            self._evaluators[call._function_name](context,call._args) # type:ignore
        else:

            func_body,func_signature = (<VecLangContext>context)._functions[call._function_name]
            
            for idx in range(len(args._args) - 1, -1, -1):
                param_type_tuple = func_signature[idx]
                arg_value = (<VecLangContext>context)._eval_stack.pop()
                arg_type = type(arg_value)

                if arg_value is None:
                    continue
                
                if param_type_tuple[1] == 'vector' and arg_type != np.ndarray:
                    error = RuntimeError(context._stack,ast._line,ast._column,f' expected type for param{idx} is {param_type_tuple[1]}; got {arg_type}') # type:ignore
                    context.add_runtime_error(ast,error)
                    runtime_error = True # type:ignore
                elif param_type_tuple[1] == 'complex' and arg_type == np.ndarray:
                    error = RuntimeError(context._stack,ast._line,ast._column,f' expected type for param{idx} is {param_type_tuple[1]}; got {arg_type}') # type:ignore
                    context.add_runtime_error(ast,error)
                    runtime_error = True # type:ignore
                elif param_type_tuple[1] == 'float' and (arg_type == np.array or arg_type == np.complex128):
                    error = RuntimeError(context._stack,ast._line,ast._column,f' expected type for param{idx} is {param_type_tuple[1]}; got {arg_type}') # type:ignore
                    context.add_runtime_error(ast,error)
                    runtime_error = True # type:ignore
                elif param_type_tuple[1] == 'int' and arg_type != np.int64:
                    error = RuntimeError(context._stack,ast._line,ast._column,f' expected type for param{idx} is {param_type_tuple[1]}; got {arg_type}') # type:ignore
                    runtime_error = True # type:ignore
                    context.add_runtime_error(ast,error)
                
                if param_type_tuple[0] in (<VecLangContext>context)._vars_index:
                    call_var_arg_index = (<VecLangContext>context)._vars_index[param_type_tuple[0]]
                    (<VecLangContext>context)._var_values[call_var_arg_index] = arg_value
                    (<VecLangContext>context)._var_types[call_var_arg_index] = type(arg_value)
                else:
                    call_var_arg_index = len((<VecLangContext>context)._vars_index)
                    (<VecLangContext>context)._vars_index[param_type_tuple[0]] = call_var_arg_index
                    (<VecLangContext>context)._var_values.append(arg_value)
                    (<VecLangContext>context)._var_types.append(type(arg_value))

            if not runtime_error:
                self._evaluator._context = context
                self._evaluator.walk(func_body)
                arg_value = (<VecLangContext>context)._eval_stack.pop()
            
            (<VecLangContext>context).pop_scope()
            (<VecLangContext>context).pop_trace()

            if not runtime_error:
                (<VecLangContext>context)._eval_stack.append(arg_value)
            else:
                (<VecLangContext>context)._eval_stack.append(None)

cpdef tuple[VecLangContext,ASTWalker,ASTWalker,ASTWalker] build_walkers():
    cdef VecLangContext context = VecLangContext()
    cdef TraversalStrategy strategy = PostOrderTraversalStrategy()
    cdef TraversalStrategy eval_strategy = PostOrderTraversalEvaluatorStrategy()
    cdef ASTWalker error_collector_walker = ASTWalker(context,strategy) # type:ignore
    cdef ASTWalker functions_collector = ASTWalker(context,strategy) # type:ignore
    cdef ASTWalker evaluator_walker = ASTWalker(context,eval_strategy) # type:ignore

    strategy.set_default_selector_without_signature_checking(DefaultChildrenSelector()) # type:ignore
    
    eval_strategy.set_default_selector_without_signature_checking(DefaultChildrenSelector()) # type:ignore
    eval_strategy.add_selector_without_signature_checking(FunctionDeclAST,FunctionDeclASTChildrenSelector()) # type:ignore

    functions_collector.add_visitor_without_signature_checking(FunctionDeclAST,FunctionDeclASTCollectorVisitor())

    error_collector_walker.add_visitor_without_signature_checking(FunctionCallAST,FunctionCallASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(SlicingAST,SlicingASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(IndexingAST,IndexingASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(PlusAST,BinaryASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(MinusAST,BinaryASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(MulAST,BinaryASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(ExpAST,BinaryASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(DivAST,DivASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(ModAST,ModASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(AssignmentAST,BinaryASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(AssignmentAST,VariableIndexerVisitor())
    error_collector_walker.add_visitor_without_signature_checking(RangeAST,RangeASTErrorCollectorVisitor())
    error_collector_walker.add_visitor_without_signature_checking(VectorComponentsAST,VectorComponentsASTErrorCollector())

    evaluator_walker.add_visitor_without_signature_checking(NumberAST,NumberASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(AssignmentAST,AssignmentASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(PlusAST,PlusASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(MinusAST,MinusASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(MulAST,MulASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(DivAST,DivASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(ModAST,ModASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(ExpAST,ExpASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(VectorComponentsAST,VectorComponentsASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(VectorAST,VectorASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(RangeAST,RangeASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(SlicingAST,SlicingASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(IndexingAST,IndexingASTEvaluatorVisitor())
    evaluator_walker.add_visitor_without_signature_checking(FunctionCallAST,FunctionCallASTEvaluatorVisitor())

    return context,error_collector_walker,functions_collector,evaluator_walker

cpdef object get_ast_value(AST ast,VecLangContext context):
    cdef AST ast_result = ast
    cdef VariableExpressionAST var

    if isinstance(ast,VecLangInstructionsSequenceAST):
        ast_result = (<VecLangInstructionsSequenceAST>ast)._instructions[-1]

    if isinstance(ast_result,VariableExpressionAST):
        var = ast_result
        return context.look_for_var(var._name)[1]
    return None
```

File `visitors.pyi`
```python
from typing import Any, Tuple,List

from pylgen.analysis.visitor import ASTWalker
from pylgen.analysis.error import RuntimeError
from pylgen.analysis.context import Context
from pylgen.common.types import AST

class VecLangContext(Context):

    def __init__(self) -> None: ...

    def get_runtime_errors(self) -> List[RuntimeError]: ...
    
    def clear_runtime_errors(self) -> None: ...

def build_walkers() -> Tuple[VecLangContext,ASTWalker,ASTWalker,ASTWalker]: ...

def get_ast_value(ast:AST, context:VecLangContext) -> Any: ...
```

## From Python to Cython: Performance-Driven Changes

Compared to the pure-Python implementation in the earlier tutorial, the VecLang semantic layer has undergone significant changes to squeeze out every ounce of performance. Let's examine the key transformations and why they matter.

> ### 1. Typed Attributes in Visitors

All visitor classes declare their attributes as `cdef` with excplicit types. This eliminates Python attribute lookups and allows Cython to generate efficent C code.

> ### 2. Separate Visitor per Operation

Each binary operation has its own visitor class. This avoids a single large `visit` method with many `if/elif` branches, which would be slow.

> ### Early Stopping in Evaluation Strategy

The `PostOrderTraversalEvaluatorStrategy` stops the traversal as soon as a runtime error is added to the context. This avoids wasting time evaluating further nodes when the result is already invalid.

> ### 3. Use of NumPy for Vector Operations

VecLang use NumPy arrays to represent vectors. Operations like addition, multiplication, and dot product are performed using NumPy's vectorised C-level functions, which are orders of magnitude faster than Python loops.

> ### 4. Cython-Level Functions and Method Calls

All visitors and strategies are `cdef` classes with `cdef` or `cpdef` methods. This means calls between them are resolved at compile time and are not subject to Python's dynamic dispatch. The overhead is minimal.

## Trade-offs and Limitations.

 - **Readability**: The Cython code is more verbose and requires type declarations. However, it's still reasonably clear, and the performance gains justify it.
 - **Flexibility**: The context is less dynamic, we cannot add new variable types at runtime without recompiling. For a fixed language like VecLang, this is acceptable.
 - **Compilation overhead**: You need Cython and a C compiler. But for production, this is a one-time cost.