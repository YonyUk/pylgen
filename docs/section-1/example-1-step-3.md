# Step 3: Bringing Meaning to the Tree (Semantic Analysis)

With our AST ready and our parser validated, we've reached the stage where we move beyond structure and into **meaning**. Lexical and syntactic analysis tell us ***how*** the code is written; semantic analysis tells us ***what*** it means and ***whether*** it makes sense.

In a typical compiler pipeline, semantic analysis handles tasks like:

 - **Type checking**: ensuring operations are performed on compatible types.
 - **Scope resolution**: verifying that variables are declared before use.
 - **Error detection**: cacthing nonsensical operations like division by zero at compile time (when possible).

For our REPL, we'll also combine **semantic analysis** with **evaluation**, after all, we're building an **interpreter**. But before we compute values, we must ensure that the computation is valid.

> ### The Context (Managing State)

Every interpreter needs a way to store and retrieve information during execution. Our `ArithmeticExpressionContext` class, defined in `context.py` serves as the central repository for all runtime state:

 - **Variables storage**: a dictionary (`_variables`) that maps variable names to their current values.
 - **AST value caching**: a dictionary (`_values`) that associates each AST node with its evaluated result or, if an error ocurred, the error itself.
 - **Error management**: methods to add, retrieve, and clear errors.

File: `contex.py`
```python
from pylgen.common.types import AST
from pylgen.analysis.context import Context
from pylgen.analysis.error import RuntimeError

from .asts import VarAST

class ArithmeticExpressionContext(Context):

    def __init__(self) -> None:
        super().__init__()
        self._variables:Dict[str,Any] = {}
        self._values:Dict[AST,Any] = {}

    def reset(self) -> None:
        super().reset()
        self._variables.clear()
        self._values.clear()
    
    def clear_garbage(self) -> None:
        super().clear_errors()
        self._values.clear()

    def define_variable(self,var_name:str):
        self._variables[var_name] = None
    
    def check_variable_in_context(self,var_name:str) -> bool:
        return var_name in self._variables

    def add_runtime_error(self, ast: AST, error: RuntimeError) -> None:
        self._values[ast] = error

    # the base method Context.clear_runtime_errors() raises NotImplementedError()
    def clear_runtime_errors(self) -> None:
        pass

    def get_runtime_errors(self) -> List[RuntimeError]:
        return [value for value in self._values.values() if isinstance(value,RuntimeError)]

    def add_variable(self,name:str,value:Any) -> None:
        self._variables[name] = value
    
    def exists_variable(self,name:str) -> bool:
        return name in self._variables
    
    def get_variable_value(self,name:str) -> Any:
        return self._variables[name]
    
    def add_ast_value(self,ast:AST,value:Any) -> None:
        self._values[ast] = value
    
    def get_ast_value(self,ast:AST) -> Any:
        if isinstance(ast,VarAST):
            return self._variables[ast.name]
        return self._values.get(ast,None)
```

This context will be passed to every visitor, providing a shared environment for both semantic error collection and evaluation.

> ### Custom Runtime Errors

Our language supports a handful of arithmetic operations, and each comes with its own set of pitfalls. We define dedicated error classes in `errors.py` to provide precise, informative feedback:

 - `DivisionByZeroError`: raised when attempting to divide by zero.
 - `ModuleByZeroError`: raised when the right operand of `%` is zero.
 - `ModuleByNotIntegerError`: raised when the right operand of `%` is not an integer.
 - `ModuleWithComplexNumberError`: raised when either operand of `%` is a complex number.

Each error carries a stack trace, line number, column number, and a descriptive message, making debugging straightforward.

File: `errors.py`
```python
from typing import List
from pylgen.analysis.error import RuntimeError

class DivisionByZeroError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'division by zero not allowed')

class ModuleByZeroError(RuntimeError):
    
    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'module by zero not allowed')

class ModuleByNotIntegerError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'module by a not-integer not allowed')

class ModuleWithComplexNumberError(RuntimeError):

    def __init__(self, stack_trace: List[str], line: int, column: int) -> None:
        super().__init__(stack_trace, line, column, 'module operation not supported for complex numbers')
```

## The **Visitor Pattern** (Separating Concerns)

Rather than cluttering our AST nodes with evaluation logic, we adopt the **Visitor Pattern**. Each node type has one or more dedicated visitor classes that know how to process it. This keeps our AST definitions clean and makes it easy to add new operations (e.g., pretty-printing, type checking, optimization) without modifying existing nodes.

PyLGEN provides the `ASTVisitor` base class, and we extend it for our specific needs.

> ### Semantic Error Collectors

Before evaluating anything, we run a **semantic error collection** pass. These visitors traverse the AST and llok for issues that can be detected statically, without executing the code:

 - `DivASTSemanticErrorCollectorVisitor`: checks if the right operand of a division is a literal zero and raises a semantic error if so.
 - `ModASTSemanticErrorCollectorVisitor`: similarly, checks for zero or non-integer operands in modulo operations.
 - `VariableASTSemanticErrorCollectorVisitor`: checks that the right-hand side of an assignment doesn't reference an undeclared variable.
 - `AssignmentASTSemanticErrorCollector`:  checks that the right-hand side of an assignment doesn't reference an undeclared variable.

These collectors add `SemanticError` objects to the context, which we can report to the user before any evaluation takes place. This early detection prevents runtime surprises.

File: `visitors.py`
```python
from pylgen.common.types import AST,Token
from pylgen.analysis.visitor import ASTVisitor
from pylgen.analysis.error import SemanticError
from .context import ArithmeticExpressionContext

class DivASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,Token) and float(ast.right.text) == 0:
            error = SemanticError('division by zero not allowed',ast.line,ast.column)
            context.add_semantic_error(error)

class ModASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,Token):
            if float(ast.right.text) == 0:
                error = SemanticError('module by zero not allowed',ast.line,ast.column)
                context.add_semantic_error(error)
            if int(float(ast.right.text)) != float(ast.right.text):
                error = SemanticError('module by not-integer not allowed',ast.line,ast.column)
                context.add_semantic_error(error)

class VariableASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if not context.check_variable_in_context(ast.name):
            error = SemanticError(f'undeclared variable "{ast.name}"',ast.line,ast.column)
            context.add_semantic_error(error)

class AssignmentASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,VarAST):
            if not context.check_variable_in_context(ast.right.name):
                error = SemanticError(f'undeclared variable "{ast.right.name}"',ast.right.line,ast.right.column)
                context.add_semantic_error(error)
```

> ### Evaluator Visitors

Once semantic errors have been cleared, we perform the actual **evaluation** using a second set of visitors. Each visitor computes the the value of its associated AST node and stores the result back in the context:

 - `PlusASTEvaluatorVisitor`, `MinusASTEvaluatorVisitor`, etc.: retrieve the values of left and right children, perform the arithmetic, and store the result.
 - `DivASTEvaluatorVisitor` and `ModASTEvaluatorVisitor`: include an extra runtime checks for division by zero, modulo by zero, and type mismatches, raising `RuntimeError` objects when necessary.
 - `AssignmentASTEvaluatorVisitor`: evaluates the right-hand side and stores the result in the variable table.
 - `AtomicASTEvaluatorVisitor`: handles literal numbers, converting them to `int` or `float` as appropiate.
 - `ExitASTEvaluatorVisitor` and `ClearASTEvaluatorVisitor`: implement the built-in `exit()` and `clear()` commands.

Notice how the evaluator visitors inherit from `BinaryASTEvaluatorVisitor`, which centralizes the common logic of fetching and type-checking the operands.

> adds the necessary imports

File: `visitors.py`
```diff
+ from typing import Any
+ import sys
+ import os
- from pylgen.analysis.error import SemanticError
+ from pylgen.analysis.error import RuntimeError,SemanticError
+ from .errors import (
+    DivisionByZeroError,
+    ModuleByZeroError,
+    ModuleByNotIntegereError,
+    ModuleWithComplexNumberError
+ )
```

```python
# ...

class BinaryASTEvaluatorVisitor(ASTVisitor):
    _left_type:type
    _right_type:type
    _left_value:Any
    _right_value:Any
    _runtime_error = False

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._runtime_error = False
        self._left_type = type(context.get_ast_value(ast.left))
        self._left_value = context.get_ast_value(ast.left)
        self._right_type = type(context.get_ast_value(ast.right))
        self._right_value = context.get_ast_value(ast.right)
        
        if isinstance(self._left_value,RuntimeError):
            context.add_runtime_error(ast,self._left_value)
            self._runtime_error = True
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            self._runtime_error = True

class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value + self._right_value)

class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value - self._right_value)

class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value * self._right_value)

class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,DivisionByZeroError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value / self._right_value)

class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value ** self._right_value)

class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,ModuleByZeroError(context.stack_trace,ast.line,ast.column))
        elif self._right_type == complex or self._left_type == complex:
            context.add_runtime_error(ast,ModuleWithComplexNumberError(context.stack_trace,ast.line,ast.column))
        elif self._right_type != int:
            context.add_runtime_error(ast,ModuleByNotIntegereError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value % self._right_value)

class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._right_value = context.get_ast_value(ast.right)
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            return
        context.add_variable(ast.left.name,self._right_value)

class AtomicASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if '.' in ast.text:
            context.add_ast_value(ast,float(ast.text))
        else:
            context.add_ast_value(ast,int(ast.text))

class ExitASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        sys.exit(0)

class ClearASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if os.sep == '\\':
            os.system('cls')
        else:
            os.system('clear')
```

> ### The Traversal Strategy (Controlling the Walk)

How do these visitors walk the tree? We use a `PostOrderStrategy` defined in `visitors.py`. As the name suggests, it processes the tree bottom-up: children are visited before their parent. This is essential for evaluators, because a parent operation (like addition) needs the values of its children already computed.

The strategy works with a **selector** (`ArithmeticExpressionASTChildrenSelector`) that determines, for each AST node, which chldren to visit. By default, it simply returns `ast.children()`, but you can override this for fine-grained control, for instance, to skip certain branch during error collection.

File: `visitors.py`
```diff
- from typing import Any
+ from typing import Any,List
- from pylgen.analysis.visitor import ASTVisitor
+ from pylgen.analysis.visitor import ASTChildrenSelector,ASTVisitor,TraversalStrategy

# ...
+ class ArithmeticExpressionASTChildrenSelector(ASTChildrenSelector):
+ 
+     def __init__(self) -> None:
+         super().__init__(ArithmeticExpressionContext)
+     
+     def select_children(self, ast: AST, context: ArithmeticExpressionContext) -> List[AST]: # type: ignore
+         self._check_context_type(context)
+         return ast.children()
```

```python
# ...

class ArithmeticExpressionASTChildrenSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def select_children(self, ast: AST, context: ArithmeticExpressionContext) -> List[AST]: # type: ignore
        self._check_context_type(context)
        return ast.children()

# ...

class PostOrderStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
        self._stack = []
        self._seen = []
    
    def init(self, root: AST) -> None:
        super().init(root)
        self._stack.append(root)
    
    def has_next(self) -> bool:
        return len(self._stack) > 0
    
    def current(self,context:ArithmeticExpressionContext) -> AST:
        self._check_context_type(context)
        selector = self._get_selector(self._stack[-1])
        children = selector.select_children(self._stack[-1],context)
        seen = self._stack[-1] in self._seen
        while children and not seen:
            self._seen.append(self._stack[-1])
            for child in children:
                self._stack.append(child)
            selector = self._get_selector(self._stack[-1])
            children = selector.select_children(self._stack[-1],context)
            seen = self._stack[-1] in self._seen
        return self._stack.pop()
    
    def reset(self) -> None:
        self._seen.clear()
        self._stack.clear()
```

This strategy is generic enough to work with both error collectors and evaluators, simply by swapping the visitor set.

> ### Recap

File: `visitors.py`

```python
from typing import Any,List
import sys
import os

from pylgen.common.types import AST,Token
from pylgen.analysis.visitor import ASTChildrenSelector,ASTVisitor,TraversalStrategy
from pylgen.analysis.error import RuntimeError,SemanticError
from .context import ArithmeticExpressionContext
from .asts import BinaryAST,VarAST
from .errors import (
    DivisionByZeroError,
    ModuleByZeroError,
    ModuleByNotIntegereError,
    ModuleWithComplexNumberError
)

class ArithmeticExpressionASTChildrenSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def select_children(self, ast: AST, context: ArithmeticExpressionContext) -> List[AST]:
        self._check_context_type(context)
        return ast.children()

class BinaryASTEvaluatorVisitor(ASTVisitor):
    _left_type:type
    _right_type:type
    _left_value:Any
    _right_value:Any
    _runtime_error = False

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._runtime_error = False
        self._left_type = type(context.get_ast_value(ast.left))
        self._left_value = context.get_ast_value(ast.left)
        self._right_type = type(context.get_ast_value(ast.right))
        self._right_value = context.get_ast_value(ast.right)
        
        if isinstance(self._left_value,RuntimeError):
            context.add_runtime_error(ast,self._left_value)
            self._runtime_error = True
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            self._runtime_error = True

class PlusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value + self._right_value)

class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value - self._right_value)

class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value * self._right_value)

class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,DivisionByZeroError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value / self._right_value)

class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value ** self._right_value)

class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,ModuleByZeroError(context.stack_trace,ast.line,ast.column))
        elif self._right_type == complex or self._left_type == complex:
            context.add_runtime_error(ast,ModuleWithComplexNumberError(context.stack_trace,ast.line,ast.column))
        elif self._right_type != int:
            context.add_runtime_error(ast,ModuleByNotIntegereError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value % self._right_value)

class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: BinaryAST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        self._right_value = context.get_ast_value(ast.right)
        if isinstance(self._right_value,RuntimeError):
            context.add_runtime_error(ast,self._right_value)
            return
        context.add_variable(ast.left.name,self._right_value)

class AtomicASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if '.' in ast.text:
            context.add_ast_value(ast,float(ast.text))
        else:
            context.add_ast_value(ast,int(ast.text))

class ExitASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        sys.exit(0)

class ClearASTEvaluatorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if os.sep == '\\':
            os.system('cls')
        else:
            os.system('clear')

class DivASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,Token) and float(ast.right.text) == 0:
            error = SemanticError('division by zero not allowed',ast.line,ast.column)
            context.add_semantic_error(error)

class ModASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,Token):
            if float(ast.right.text) == 0:
                error = SemanticError('module by zero not allowed',ast.line,ast.column)
                context.add_semantic_error(error)
            if int(float(ast.right.text)) != float(ast.right.text):
                error = SemanticError('module by not-integer not allowed',ast.line,ast.column)
                context.add_semantic_error(error)

class VariableASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if not context.check_variable_in_context(ast.name):
            error = SemanticError(f'undeclared variable "{ast.name}"',ast.line,ast.column)
            context.add_semantic_error(error)

class AssignmentASTSemanticErrorCollectorVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
    
    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        self._check_context_type(context)
        if isinstance(ast.right,VarAST):
            if not context.check_variable_in_context(ast.right.name):
                error = SemanticError(f'undeclared variable "{ast.right.name}"',ast.right.line,ast.right.column)
                context.add_semantic_error(error)

class PostOrderStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(ArithmeticExpressionContext)
        self._stack = []
        self._seen = []
    
    def init(self, root: AST) -> None:
        super().init(root)
        self._stack.append(root)
    
    def has_next(self) -> bool:
        return len(self._stack) > 0
    
    def current(self,context:ArithmeticExpressionContext) -> AST:
        self._check_context_type(context)
        selector = self._get_selector(self._stack[-1])
        children = selector.select_children(self._stack[-1],context)
        seen = self._stack[-1] in self._seen
        while children and not seen:
            self._seen.append(self._stack[-1])
            for child in children:
                self._stack.append(child)
            selector = self._get_selector(self._stack[-1])
            children = selector.select_children(self._stack[-1],context)
            seen = self._stack[-1] in self._seen
        return self._stack.pop()
    
    def reset(self) -> None:
        self._seen.clear()
        self._stack.clear()
```

!!! note
    You might have noticed that every visitor begins with a call to `self._check_context_type(context)`. This is a **safety net**, a runtime type guard that ensures the context being passed to the visitor is actually an instance of `ArithmeticExpressionContext`.

    Why is this necessary? PyLGEN's visitor framework is designed to be generic. It doesn't know what specific context class you're using; it simply accepts any object that inherits from the base `Context` class. However, our visitors rely on on methods and attributes that are specific to `ArithmeticExpressionContext`, like `add_variable`,`get_ast_value`, and `check_variable_in_context`. If due to a configuration mistake, a visitor received a different context type, calling those methods would case an attribute error.

    The `_check_context_type` method, which comes from the base `ASTVisitor` class, verifies that the context is of the expected type. If it isn't, it raises a clear error explaining what went wrong, saving you from obscure debugging sessions. It's a small line of defensive code that brings peace of mind, especially as your interpreter grows more complex.

    > **Why this design?** You might wonder why PyLGEN doesn't enforce the context type through the type system instead of relying on runtime checks. This is actually a deliberate  trade-off  to support dynamic visitor registration and multiple context types within the same traversal. We'll explore the full rationale, and how this pattern enables powerfull extension mechanisms, in a later section dedicated to PyLGEN's internal architecture. For now, trust that it's a small price to pay for a flexible and robust framework.

    So, while it might feel repetitive to see it in every visitor, it's a lightweight guarantee that everything is wired up correctly. You'll appreciate it when you start extending your language with new features and need to catch mismatches early.

## Bringing It All Together (The Semantic Module)

`semantic.py` is the orchestrator. It instantiates a single context and a single traversal strategy, then builds two `ASTWalker` instances:

`1` - `error_collector_ast_walker`: uses the error collector visitors to perform static checks.
`2` - `evaluator_ast_walker`: uses the evaluation visitors to compute results.

File: `semantic.py`

```python
from pylgen.common.types import Token
from pylgen.analysis.visitor import ASTWalker

from .context import ArithmeticExpressionContext
from .visitors import (
    ClearASTEvaluatorVisitor,
    PostOrderStrategy,
    ArithmeticExpressionASTChildrenSelector,
    DivASTSemanticErrorCollectorVisitor,
    ModASTSemanticErrorCollectorVisitor,
    VariableASTSemanticErrorCollectorVisitor,
    AssignmentASTSemanticErrorCollectorVisitor,
    PlusASTEvaluatorVisitor,
    MinusASTEvaluatorVisitor,
    MulASTEvaluatorVisitor,
    DivASTEvaluatorVisitor,
    ExpASTEvaluatorVisitor,
    ModASTEvaluatorVisitor,
    AtomicASTEvaluatorVisitor,
    AssignmentASTEvaluatorVisitor,
    ExitASTEvaluatorVisitor
)
from .asts import (
    AssignmentAST,
    ClearAST,
    PlusAST,
    MinusAST,
    MulAST,
    DivAST,
    ExpAST,
    ModAST,
    VarAST,
    ExitAST
)

context = ArithmeticExpressionContext()
traversal_strategy = PostOrderStrategy()

traversal_strategy.set_default_selector(ArithmeticExpressionASTChildrenSelector())

error_collector_ast_walker = ASTWalker(context,traversal_strategy)

error_collector_ast_walker.add_visitor(DivAST,DivASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(ModAST,ModASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(VarAST,VariableASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(AssignmentAST,AssignmentASTSemanticErrorCollectorVisitor())

evaluator_ast_walker = ASTWalker(context,traversal_strategy)

evaluator_ast_walker.add_visitor(PlusAST,PlusASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(MinusAST,MinusASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(MulAST,MulASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(DivAST,DivASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ExpAST,ExpASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ModAST,ModASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(Token,AtomicASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(AssignmentAST,AssignmentASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ExitAST,ExitASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ClearAST,ClearASTEvaluatorVisitor())
```

## The Workflow

`1` - **Parse** the input to obtain an AST.

`2` - **Run the error collector** on the AST to detect semantic issues(undeclared variables, static division by zero,etc.).

`3` - **If any error are found**, report them and abort evaluation.

`4` - **Otherwise, run the evaluator** on the AST to compute the result.

`5` - **Retrieve the result** from the context and display it.

## Why this design

By combining the **Visitor** and **Strategy** patterns, we achieve:

 - **Separation of concerns**: AST nodes are simple data containers; all logic lives in visitors.
 - **Reusability**: the same traversal strategy works for both semantic checks and evaluation.
 - **Extensibility**: adding a new operation or a new static check simply requires a new visitor class and a single line to register it.
 - **Clear error handling**: semantic errors are collected during the first pass, runtime errors during the second. Both are stored in the context and can be reported uniformly.

## What's next?

With semantic analysis and evaluation in place, we're incredibly close to a complete interpreter. The final step is to wrap everything in a **REPL** loop, handling user input, orchestrating the pipeline, and presenting results. We'll also need to manage the context across multiple input lines, so that variables persist between evaluations.

But before we get there, take a moment to appreciate what we've built: a **lexer**, a **parser**, a **complete AST**, **semantic checks**, and an **evaluator**, **all working together**. The foundation is solid; now we just need to give it a friendly user interface.

Ready? Let's move on to the final step: building the **REPL**.