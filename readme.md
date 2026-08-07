# PyLGEN
![PyPI - 0.3.5](https://img.shields.io/pypi/v/pylgen)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/yonyuk/pylgen/ci.yml)
![PyPI - 3.8](https://img.shields.io/pypi/pyversions/pylgen)
![PyPI - LICENSE](https://img.shields.io/pypi/l/pylgen)

![Codecov](https://img.shields.io/codecov/c/github/yonyuk/pylgen)

*From prototype to production: a **Python-native compiler framework** that brings the "**Dragon Book**" to life in Python, with clarity throughout.*

 - Build **interpreters** and **compilers** from scratch, without leaving the **Python's ecosystem**
 - Keep total control of what's going on at every step
 - Build **fast and easy** with python for prototyping and debugging
 - Compile and get more speed with cython

> [!note]
> **Cython compilation** requires a **C** compiler installed on system to compile the code

> ## Summary
 - :rocket: [Fast Installation](#-fast-installation)
 - 📉 [Benchmark](#-benchmark)
 - :book: [Minimal example](#-minimal-example)
 - :gear: [Architecture](#-architecture)

> ## :rocket: Fast Installation

### :package: Fast installation with pip

***PyLGEN*** is a python library, so can be installed via ***pip install*** command

```bash
pip install pylgen
```

### Install from source code

 - Download the source code.
 - Install all build's dependencies.
```bash
pip install -r requirements.txt
```
 - In the root folder, run this command for a local installation
```bash
python setup.py build_ext --inplace
```

> ## 📉 Benchmark

This section evaluates the parsing performance of `pylgen` under a realistic, large-scale workload. This benchmark focuses solely on raw throughput and efficency, comparing `pylgen` againist **Lark** with its Cython acceleration plugin enabled to ensure a fair baseline.

> ### Test Language & Input Data

The benchmark is build around ***VecLang***, a minimal but feature-rich **DSL** designed specifically for this test. (Full details are available in the official documentation, and the reference implementation can be found in the `examples/veclang` folder of this repository.)

To stress-test both parsers, a source file with a total decompressed size of **39,163 KB**. The structure of this files is as follows:

`1` **A core logic block** (see condensed snippet below) that exercises a wide spectrum of ***VecLang*** features:
 - Complex number creation and arithmetic.
 - Function declarations and nested calls.
 - Vector initialization, range generation (`[4:10]`), and elementwise operations.
 - Single and multi-level slicing (`[0:30][5:25][10:15]`).

`2` This core block is **cyclically repeated** across approximately 2 million lines ( exactly 1,999,997 lines) to simulate high-frequency, production-scale parsing scenarios.

`3` The file concludes with a **final block** that invokes built-in functions (`print`,`sum`,`dot` and `mean`) to verify end-to-end correctness after the massive repetition.

> #### Core logic block
```txt
// testing complex numbers creation
complex_number = complex(2,3)

// testing function declarations
f(x:complex,y:float) = x / (y - 5)

// testing functions call
var_a = f(complex_number,10)

// more functions declarations
g(x:int,y:int) = x ** y / 10 - 100

// more functions calls
var_b = g(20,4)

// arithmetic operations
var_c = (var_a + var_b) / (var_a - var_b)

// combining calls and operations
var_d = g(50,4) % 7

// testing vectors
vector_1 = [1,4.5,complex_number,var_b]
vector_2 = vector_1 / 5

// testing range
vector_3 = [4:10]

// testing indexing
var_e = vector_1[1]
var_f = vector_2[2]
var_g = vector_3[3]

var_slice = vector_3[1:3]
var_slice_1 = var_slice[0:1]

// testing multiple slicing
var_slice_2 = [0:30][5:25][10:15]

```
> #### Final block
```txt
// testing built-in functions
print(var_slice_2)
print(vector_1)
print(vector_2)
print(vector_3)

var_sum = sum(vector_1)
var_mean = mean(vector_3)
var_dot = dot(vector_1,vector_2)

print(var_sum)
print(var_mean)
print(var_dot)
```

> [!note]
The source code file can be found in this repository at `examples/veclang/benchmark.zip`.

> [!note]
This benchmark goes beyond measuring mere parsing speed; it evaluates the **entire workflow** that `pylgen` supports in a **real-world execution environment**.

> [!important]
It is crucial to clarify that the scope of the comparision with **Lark**: as a parser generator, Lark participates **exclusively** in the parsing phase.
Consequently, the direct head-to-head comparision between the two tools is strictly limited to syntactic performance.

> ### Technical details
|PC|OS|Processor|RAM|System Type|
|:---:|:---:|:---:|:---:|:---:|
|**HP Pavilion**(portatil)|**Windows 10 Home 22H2**|**Intel(R) Core(TM) i5-10210U CPU @ 1.60 GHz ~ 2.11 GHz**|**8 GB**|64-bit operating system, x64-based processor|

> ### Benchmark time results
| |Syntactic analysis|AST construction|Symbol collection|Semantic validation|Final evaluation|
|:---:|:---:|:---:|:---:|:---:|:---:|
|**`lark` + `lark_cython`**|148.459452 s| --- | --- | --- | --- |
|**`pylgen`**|55.078121 s|Simultaneous with parsing|0.952746 s|1.445209 s|3.502622 s|
|speedup|~2.7x| --- | --- | --- | --- |

> ## :book: Minimal example

This guide walks you through building a complete interpreter for a small arithmetic language with variables, assignments, and REPL commands (exit and clear). The architecture follows a classic three‑stage pipeline:

```mermaid
%%{init:{ 'flowchart': { 'rankSpacing': 800, 'nodeSpacing': 30 } }%%
flowchart TB
    A["tokens definitions and lexer configuration"]
    B["explicit token types"]
    C["mapping function"]
    D["tokens regex"]
    E["lexical rules (optional)"]
    F["define symbols (terminals and non-terminals)"]
    G["define attributed grammar"]
    H["define reducer functions"]
    I["define ASTs"]
    J["builds the parser"]
    K["define children selectors"]
    L["adds selectors a traversal strategies"]
    M["define a context"]
    N["define walkers"]
    O["define visitors"]
    P["adds visitors"]
    RawCode["source code"]
    Lexer["Lexer"]
    Parser["Parser"]
    Context["Context"]
    Walkers["Walkers"]
    AST["AST"]
    AST_Processing["AST Processing"]
    Result["execution result"]

    subgraph Lexical_Analysis_State["Lexical Analysis (tokens definition)"]
        A
        B
        C
        D
        E
    end

    subgraph Syntax_Analysis_State["Syntactic Analysis (symbols, grammar, ASTs)"]
        F
        G
        H
        I
        J
    end

    subgraph Semantic_Analysis_State["Semantic Analysis (visitors, traversal strategies)"]
        K
        L
        M
        N
        O
        P
    end

    subgraph Execution["Execution flow"]
        RawCode
        Lexer
        Parser
        Context
        Walkers
        AST
        AST_Processing
        Result
    end

    B --> A
    C --> A
    D --> A
    E --> A

    F --> G
    H --> G
    I --> H
    G --> J
    F --> I

    K --> L
    M --> N
    M --> K
    L --> N
    M --> O
    N --> P
    O --> P

    A --> Lexer
    J --> Parser
    M --> Context
    P --> Walkers
    RawCode --> Lexer
    Lexer -- "token stream" --> Parser
    Parser --> AST
    Walkers --> AST_Processing
    AST --> AST_Processing
    Context --> AST_Processing
    AST_Processing --> Result

    F --> C
    I --> K
    I --> O

    Syntax_Analysis_State ~~~ Lexical_Analysis_State
    Syntax_Analysis_State ~~~ Semantic_Analysis_State
    Lexical_Analysis_State ~~~ Execution
    Syntax_Analysis_State ~~~ Execution
    Semantic_Analysis_State ~~~ Execution
```

The file structure is organised as follows:

    arithmetic_interpreter
        |--- asts.py
        |--- context.py
        |--- errors.py
        |--- grammar_symbols.py
        |--- grammar.py
        |--- lexer.py
        |--- reductors.py
        |--- semantic.py
        |--- visitors.py
    main.py

> ### **`State 1(Lexical analysis)`**: Build the lexer

The lexer converts raw source code into a stream of tokens. We define token types, regular expressions, and optional validation rules.

```python
# file: lexer.py
from pylgen.common.enums import TokenType
from pylgen.common.types import Symbol
from pylgen.lexer.lexer import Lexer
from pylgen.analysis.lexical import LexicalRule
from .grammar_symbols import (
    END_SYMBOL,
    number,
    variable
)

# Enumeration of token types of our language
class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    VARIABLE = 'VARIABLE'
    KEYWORD = 'KEYWORD'

class NumberLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')

    def _check(self, text: str):
        if '.' in text:
            return str(float(text)) == text
        return str(int(text)) == text

class VariableLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('variables names can\'t star with a number')

    def _check(self, text: str):
        return not text[0].isdigit()

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.KEYWORD:
        return Symbol(tx,True)
    return Symbol(tx,True)

lexer = Lexer(get_symbol_function,'\n|\t| ')
lexer.set_eof_token(END_SYMBOL,TokenTypeEnum.SYMBOL)

lexer[0,TokenTypeEnum.NUMBER] = '\\d+|\\d+\\.\\d+'
lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%|='
lexer[3,TokenTypeEnum.KEYWORD] = 'exit|clear'
lexer[4,TokenTypeEnum.VARIABLE] = '\\w+'

lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicalRule())
lexer.add_rule(TokenTypeEnum.VARIABLE,VariableLexicalRule())
```

> ### **State 2(Syntax analysis)**:

Syntax analysis defines the grammar, builds AST nodes, and attaches reducer functions that produce ASTs from productions.

 - `Define symbols`:
```python
# file: grammar_symbols.py
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
```
 - `Define ASTs`:

AST nodes hold the structure of the parsed input and are later visited for semantic analysis.
```python
# file: asts.py
from typing import List

from pylgen.common.types import AST,Symbol
from .grammar_symbols import (
    clear,
    plus,
    minus,
    mul,
    mod,
    div,
    exp,
    eq,
    variable,
    exit
)

class BinaryAST(AST):

    def __init__(self, left:AST,right:AST,symbol: Symbol, line: int, column: int):
        super().__init__(symbol, line, column)
        self._left:AST = left
        self._right:AST = right

    @property
    def left(self) -> AST:
        return self._left # type:ignore

    @property
    def right(self) -> AST:
        return self._right # type: ignore

    def children(self) -> List[AST]:
        return [self._left,self._right]

class PlusAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,plus, line, column)

class MinusAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,minus, line, column)

class ModAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,mod, line, column)

class MulAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,mul, line, column)

class DivAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,div, line, column)

class ExpAST(BinaryAST):

    def __init__(self, left:AST,right:AST, line: int, column: int):
        super().__init__(left,right,exp, line, column)

class AssignmentAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, eq, line, column)

    def children(self) -> List[AST]:
        return [self._right]

class VarAST(AST):

    def __init__(self,name:str,line:int,column:int):
        super().__init__(variable,line,column)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def children(self) -> List[AST]:
        return []

class ExitAST(AST):

    def __init__(self,line: int, column: int):
        super().__init__(exit, line, column)

    def children(self) -> List[AST]:
        return []

class ClearAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(clear, line, column)

    def children(self) -> List[AST]:
        return []
```

> [!important]
The order in which children are returned by `children()` method is the order in which traversals will get the childs for the current node.

 - `Define reductors`:

Reducers transform a list of ASTs (the right‑hand side of a production) into a single AST.

```python
# file: reductors.py
from pylgen.common.types import AST,ASTListView
from .grammar_symbols import (
    minus,
    plus,
    mul,
    div,
    exp,
    mod,
    eq
)
from .asts import (
    ClearAST,
    PlusAST,
    MinusAST,
    MulAST,
    DivAST,
    ExpAST,
    ModAST,
    VarAST,
    AssignmentAST,
    ExitAST
)

# ...
def binary_reductor(asts:ASTListView) -> AST:
    ast_type:type = None  # type: ignore
    if asts[1].symbol == plus:
        ast_type = PlusAST
    elif asts[1].symbol == minus:
        ast_type = MinusAST
    elif asts[1].symbol == mul:
        ast_type = MulAST
    elif asts[1].symbol == div:
        ast_type = DivAST
    elif asts[1].symbol == exp:
        ast_type = ExpAST
    elif asts[1].symbol == mod:
        ast_type = ModAST
    elif asts[1].symbol == eq:
        ast_type = AssignmentAST
    else:
        raise ValueError()
    return ast_type(asts[0],asts[2],asts[1].line,asts[1].column)

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def parenthesis_reductor(asts:ASTListView) -> AST:
    return asts[1]

def variable_reductor(asts:ASTListView) -> AST:
    return VarAST(asts[0].text,asts[0].line,asts[0].column) # type: ignore

def exit_reductor(asts:ASTListView) -> AST:
    return ExitAST(asts[0].line,asts[0].column)

def clear_reductor(asts:ASTListView) -> AST:
    return ClearAST(asts[0].line,asts[0].column)
```

 - `Define the grammar and build the parser`:

We define an attributed grammar and build an LALR(1) parser.

```python
# file: grammar.py
from pylgen.parser.parser import BottomUpParser
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.grammar.grammar import AttributedGrammar
from .grammar_symbols import (
    END_SYMBOL,
    VAR,
    ArithmeticExpression,
    E,
    T,
    F,
    P,
    plus,
    minus,
    mul,
    div,
    exp,
    mod,
    lp,
    rp,
    number,
    variable,
    eq,
    exit,
    clear
)
from .reductors import (
    binary_reductor,
    single_reductor,
    parenthesis_reductor,
    variable_reductor,
    exit_reductor,
    clear_reductor
)

# Create the attributed grammar with the start symbol and end marker
G = AttributedGrammar(ArithmeticExpression, END_SYMBOL)

G[ArithmeticExpression] += (E,), single_reductor
G[ArithmeticExpression] += (VAR, eq, E), binary_reductor
G[ArithmeticExpression] += (exit, lp, rp), exit_reductor
G[ArithmeticExpression] += (clear, lp, rp), clear_reductor

G[E] += (E, plus, T), binary_reductor
G[E] += (E, minus, T), binary_reductor
G[E] += (T,), single_reductor

G[T] += (T, mul, F), binary_reductor
G[T] += (T, div, F), binary_reductor
G[T] += (T, mod, F), binary_reductor
G[T] += (F,), single_reductor

G[F] += (F, exp, P), binary_reductor
G[F] += (P,), single_reductor

G[P] += (lp, E, rp), parenthesis_reductor
G[P] += (number,), single_reductor
G[P] += (VAR,), single_reductor

G[VAR] += (variable,), variable_reductor

parser = ParserBuilder.build_parser_from_attributed(G, ParserType.LALR1)
```

> ### **State 3(Semantic analysis)**:

Semantic analysis consists of two passes: Semantic error collection(detect undeclared variables and static arithmetic errors); Evaluation (compute the result).

 - `Define errors`
```python
# file: errors.py
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

 - `Define the context`

The context holds variables and stores computed values for each AST node (or errors).

```python
# file: context.py
from typing import List,Any,Dict
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

 - `Define visitors and traversal strategies`:

We define a post‑order traversal strategy (children visited before parent) and multiple visitors for error collection and evaluation.

```python
# file: visitors.py
from typing import Any,List
import sys

from pylgen.common.types import AST,Token
from pylgen.analysis.visitor import ASTChildrenSelector,ASTVisitor,TraversalStrategy
from pylgen.analysis.error import RuntimeError,SemanticError
from .context import ArithmeticExpressionContext
from .asts import BinaryAST,VarAST
from .errors import (
    DivisionByZeroError,
    ModuleByZeroError,
    ModuleByNotIntegerError,
    ModuleWithComplexNumberError
)
from .grammar_symbols import VAR

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

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
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

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value + self._right_value)

class MinusASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value - self._right_value)

class MulASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value * self._right_value)

class DivASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,DivisionByZeroError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value / self._right_value)

class ExpASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if not self._runtime_error:
            context.add_ast_value(ast,self._left_value ** self._right_value)

class ModASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
        super().visit(ast,context)
        if self._runtime_error:
            return
        if self._right_value == 0:
            context.add_runtime_error(ast,ModuleByZeroError(context.stack_trace,ast.line,ast.column))
        elif self._right_type == complex or self._left_type == complex:
            context.add_runtime_error(ast,ModuleWithComplexNumberError(context.stack_trace,ast.line,ast.column))
        elif self._right_type != int:
            context.add_runtime_error(ast,ModuleByNotIntegerError(context.stack_trace,ast.line,ast.column))
        else:
            context.add_ast_value(ast,self._left_value % self._right_value)

class AssignmentASTEvaluatorVisitor(BinaryASTEvaluatorVisitor):

    def visit(self, ast: AST, context: ArithmeticExpressionContext) -> None:
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
        print('\033c',end="")

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
        if ast.right.symbol == VAR:
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

 - `Define the semantic rules`:
```python
# file: semantic.py
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

> ### Define execution loop

The REPL ties everything together.

```python
# file: main.py
from arithmetic_interpreter.grammar import parser
from arithmetic_interpreter.lexer import lexer
from arithmetic_interpreter.semantic import context,evaluator_ast_walker,error_collector_ast_walker

while True:
    context.clear_garbage()
    parser.reset()
    lexer.clear_errors()

    text = input('>>> ')
    if len(text) == 0:
        continue
    lexer.load_text(text)
    ast = parser.parse(lexer.tokens)
    errors = list(lexer.errors) + parser.errors
    if not errors:
        error_collector_ast_walker.walk(ast)
    errors += context.errors
    if not errors:
        evaluator_ast_walker.walk(ast)

    errors += context.errors
    errors = list(set(errors))
    if errors:
        for error in errors:
            print(error)
    else:
        result = context.get_ast_value(ast) # type: ignore
        if result is not None:
            print(result)
```

> ### Run the interpreter
```bash
python ./main.py
```

> ## :gear: Architecture

***PyLGEN*** is a collection of Python modules featuring a high-performance core written in Cython. Together, they offer comprehensive tools for constructing interpreters and compilers from scratch, all while maintaining full compatibility with the broader Python ecosystem

 - [`🔎 pylgen.analysis`](#-analysis)
 - [`🧱 pylgen.common`](#-common)
 - [`🤖 pylgen.automaton`](#-automaton)
 - :books: [`pylgen.grammar`](#-grammar)
 - :books: [`pylgen.lexer`](#-lexer)
 - :books: [`pylgen.parser`](#-parser)
 - :books: [`pylgen.regex`](#-regex)
 - [`📉 pylgen.visual`](#-visual)

### 🔎 analysis

Supplies the essential foundation for **semantic analysis, validation, and execution** of languages built with ***pylgen***. It bridges the gap between raw syntax (the **AST**) and meaningfull program behaviour 

> #### Core Components
 - **`Context(abstract base class)`**: Manages global state during **AST** traversal: 
> [!important]
`push_new_scope,pop_scope,clear_runtime_errors,add_runtime_error` and `get_runtime_errors` must be implemented by users.
 - **`Error and its subclasses (LexicalError,SyntaxError,SemanticError)`**: A hierarchy for errors that occur during lexical, syntactic, and semantic analysis, and runtime errors. All inherit from `Error`, which includes line, column, a descriptive message, and categorisation via the `ErrorType` enum.
 - **`LexicalRule`**: An abstraction to defining validation rules on tokens. Used in `pylgen.lexer` module to check token properties. The `check` method returns a `LexicalError` if the rule is violated, or `None` otherwise.
 - **`ASTVisitor(abstract class)`**: Defines the contract for visitors that operate on `AST` nodes. Each visitor must implement `visit(ast,context)`, where it can inspect or modify the node and the context.
 - **`ASTChildrenSelector(abstract class)`**: Specifies which children (or the node itself) should be considered during traversal, and in what order. It is used by the traversal strategy to determine the next node to visit.
 - **`TraversalStrategy(asbtract class)`**: Defines the interface for traversal strategies (e.g. depth-first, breadth-first, custom-order). Key methods: `init(root),has_next(),current(context)` and `reset()`.
> [!important]
The interface does not explicitly define where the iterator's advance mechanism should be implemented; this responsibility is left to the developer.
 - **`ASTWalker`**: Orchestrates the **AST** traversal by combining a `TraversalStrategy` with a collection of `ASTVisitor` instances associated with specific node types. During `walk(ast)`, it iterates over nodes according to the strategy and applies the corresponding visitor (or a default visitor if it was supplied and none visitor was registered for a node type).

### 🧱 common

Provides the **core data types and utilities** shared across all modules of the framework, forming the common language that ties parsing, analysis, and code generation together.

> #### Core types and utilities
 - **`Symbol`**: Represents grammar symbols (both terminals and non-terminals). It is **immutable** and **hashable**, and distinguishes between terminal, non-terminal, and epsilon symbols. Used throughout grammar definitions, parser tables, and AST nodes.
 - **`AST`**: The abstract base class for all **Abstract Syntax Tree** nodes. Every concrete AST node inherits from it and stores its symbol, source location (line and column), and must implement the `children()` method to provide access to its child nodes.
 - **`Token`**: Encapsulates a lexical token, carrying its type (`TokenType`), text, associated symbol, and precise position information. Used by the lexer and the parser to feed the syntactic analysis.
 - **`ASTListView`**: A lightweight, read-only view over a list of AST nodes. It is passed to reducer functions (semantic actions) during parsing, providing efficient indexed access (`__getitem__`) and length (`__len__`) without copying the underlying list.
 - **`Table`**: A thin wrapper around a dictionary representing transition tables (e.g., for automata or parsing). It enforces string keys and values, and provides convenient properties (`entries`, `values`, `items`) to inspect its contents.
 - **`TokenType`**: A base `StrEnum` that serves as a type-safe enumeration for all lexical token types, ensuring consistency across the lexer and parser.

> #### Examples
```python
from pylgen.common.types import Symbol,AST,Token,Table

# creates a non-terminal symbol
S = Symbol('S')
# creates a terminal symbol
t = Symbol('t',True)
# creates an epsilon symbol
epsilon = Symbol('epsilon',True,True)

# creates an ast
s_ast = AST(S,1,1)

# creates a token
# let's assume a hypothetical enum TokenTypeEnum 
token = Token('texto',TokenTypeEnum.STRING,t,1,1)

# creates a table
table = Table()
# adding values
table['a','b'] = 'c'
```

### :robot: automaton

Provides the **core finite automata infrastructure** for pattern matching, forming the bedrock of the lexer and lexical analysis pipeline. It efficiently bridges regular expressions to executable state machines.

> #### Core capabilities
 - **`Automaton Construction`**: Provides several factory methods to build DFAs and NFAs, supporting standard regular language operations out-of-the-box, including **union** ( `|` ), **concatenation** ( `.` ), **intersection** ( `&` ), and **Kleene star** ( `*` ).
 - **`Determinization and Minimization`**: Transforms NFAs to DFAs via the `to_deterministic()` method and applies **Hopcroft's algorithm** for DFA minimization (`minimize()`). This yields an extremely efficient tokenization engine, drastically reducing state count and lookup overhead.

> #### Usage

 - #### Creating a DFA explicitly

```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

# create the states
q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the transition table
table = Table()
# q0 -- 0 --> q1
table['q0','0'] = 'q1'
# q0 -- 1 --> q0
table['q0','1'] = 'q0'
# q1 -- 0 --> q1
table['q1','0'] = 'q1'
# q1 -- 1 --> q0
table['q1','1'] = 'q0'

# create the dfa

aut = create_dfa({q0,q1},table,'q0',{'0','1'})
```

 - #### Creating a DFA incrementally
```python
from pylgen.automaton import DFA,State

aut = DFA('q0','q0',{'0','1'})

# gets the start state
q0 = aut.start_state
# creates a new state
q1 = State('q1','q1',True)

# adds transitions
aut.add_transition(q0,q1,'0')
aut.add_transition(q0,q0,'1')
aut.add_transition(q1,q1,'0')
aut.add_transition(q1,q0,'1')
```
> [!tip]
 `1` - Alternatively, this can be done this way:
```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the dfa
aut = create_dfa({q0,q1},Table(),'q0',{'0','1'})

# adds transitions
aut.add_transition(q0,q1,'0')
aut.add_transition(q0,q0,'1')
aut.add_transition(q1,q1,'0')
aut.add_transition(q1,q0,'1')
```
> [!tip]
 `2` - More easily
```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the dfa
aut = create_dfa({q0,q1},Table(),'q0',{'0','1'})

# adds transitions
aut += q0,'0',q1
aut += q0,'1',q0
aut += q1,'0',q1
aut += q1,'1',q0
```

### :books: grammar

Provides the **formal language definition framework** that underpins the entire parsing pipeline. It bridges context-free grammar (CFG) specification to executable LR parser tables, with native support for attributed productions that build Abstract Syntax Trees (ASTs) directly during parsing. It also offers basic utilities for grammar analysis and transformation.

> #### Core Components
 - **`Production`**: A rule of the form `head → sequence of symbols`. Immutable and hashable, it uniquely identifies each production.
 - **`ProductionsSet`**: A container that groups all productions sharing the same head. Supports the `+=` operator to add new productions (as tuples of symbols) and preserves insertion order.
 - **`AttributedProductionsSet`**: Extends `ProductionsSet` to associate a **reducer function** (signature `(ASTListView) -> AST`) with each production. Used internally by attributed grammars.
 - **`Grammar`**: The base class that stores the start symbol, end-of-input marker, and all productions. Provides methods for computing **`first`** and **`follow`** sets, and static methods for regularity checks (`IsLeftRegular`, `IsRightRegular`, `IsRegular`), grammar augmentation (`AugmentGrammar`), and reversal (`Reverse`).
 - **`AttributedGrammar`**: Subclass of `Grammar` that pairs each production with a reducer function ( `ASTListView -> AST` ). This is the core mechanism for constructing ASTs during parsing.

> #### Key Features
- **Intuitive API**: Define productions in a Pythonic style using the `+=` operator.

```python
# E, T, plus must be instances of Symbol

# Attributed grammar with reducers
G[E] += (E, plus, T), binary_reducer
G[E] += (T,), single_reducer

# Plain grammar (no reducers)
G[E] += E, plus, T
G[E] += T,
```

### :books: lexer

Provides a **flexible and efficient lexical analysis framework** that transforms raw source code into a stream of tokens, ready for parsing. It combines regex-based pattern matching with automata theory to deliver both correctness and performance.

> #### Core components
 - **`Lexer`**: The main class that manages token definitions, input text, and token streaming. Extends `BaseLexer` with error handling, validation rules, and regex-based token definition.
 - **`BaseLexer`**: The foundational class that handles automaton-driven scanning, with DFA-based token matching and the ability to skip ignored patterns (e.g., whitespace, comments). Typically not used directly.

> #### Key features
 - **`Regex‑Based Pattern Definition`**: Define tokens using standard regex strings, automatically compiled into efficient DFAs:
```python
# TokenTypeEnum must be a subclass of TokenType (from common.enums)
lexer[0, TokenTypeEnum.INTEGER] = r'\d+'
lexer[1, TokenTypeEnum.FLOAT]   = r'\d*\.\d+'
```

 - **`Prioritized Matching`**: Tokens are matched according to an explicit integer priority (lower numbers have higher precedence). This resolves ambiguities when multiple patterns match the same input prefix.

 - **`Validation Rules`**: Attach LexicalRule objects to token types to perform additional checks (e.g., value ranges, format constraints). Violations are collected as LexicalError objects and can be retrieved via the errors property.
```python
class IntegerLexicalRule(LexicalRule):
    # ... code ...

lexer.add_rule(TokenTypeEnum.INTEGER,IntegerLexicalRule())
```

 - **`Custom Symbol Mapping`**: A user‑provided function get_symbol_function(type: TokenType, text: str) -> Symbol maps each token to a grammar symbol, enabling tight integration with the parser.

 - **`Ignore Patterns`**: Supply a DFA for characters to skip (e.g., whitespace, comments) to filter out irrelevant input.

 - **`EOF Handling`**: Explicit end‑of‑file token with configurable type and symbol, ensuring a clean termination of the token stream.

 - **`Lazy Token Stream`**: The tokens property returns a generator that yields tokens on‑the‑fly, minimizing memory usage even for large source files.

### :books: parser

Provides a **production-ready LALR(1) parser framework that transforms** token streams into ***Abstract Syntax Trees (ASTs)*** via attributed grammar reductions. It seamlessly bridges grammar definitions and AST construction offering both performance and flexibility.

> #### Core components
 - **`Parser`**: Abstract base class defining the parsing contract, error handling, and parse tree access.
 - **`BottomUpParser`**: Concrete **BottomUpParser** implementation. Maintains separate stacks for states, symbols, and AST nodes. During each reduction, it invokes a user‑provided reductor associated with the current production, building the AST incrementally.
 - **`ParserBuilder`**: Consumes a plain `Grammar` or an `AttributedGrammar (from pylgen.grammar)` and generates the ACTION and GOTO tables. It detects **shift/reduce** and **reduce/reduce** conflicts.
 - **`ParseTreeNode`**: Optional concrete syntax tree (CST) node, built alongside the AST when debugging or visualisation is enabled. Each node corresponds to a production reduction and stores its children.

> #### Key features
 - **`LALR(1) Parsing`**: Implements the standard algorithm, handling most context‑free grammars. Conflicts are identified at build time and reported as `LALRShiftReduceConflictException` or `LALRReduceReduceConflictException`.
 - **`Error Recovery`**: Employs **panic‑mode** recovery, using synchronisation sets derived from the grammar's **FOLLOW** sets. When a syntax error occurs, the parser discards tokens until a synchronising symbol is found, allowing it to resume parsing and report multiple errors.
 - **`Interactive Support`**: The `reset()` method restores the parser to its initial state, making it suitable for **REPL environments** where multiple independent inputs are processed sequentially.
 - **`Optional Parse Tree`**: By setting the `draw‑parse‑tree flag`, the parser builds a concrete syntax tree alongside the AST, aiding debugging and tooling.
 - **`Custom Reductors`**: Reductors are functions that convert a list of child ASTs (wrapped in an `ASTListView`) into a single AST node. They can be attached to productions either via the attributed grammar or at runtime using the **__setitem__** operator.

### :books: regex

Provides a **complete regular expression engine** that serves as a bridge between textual regex patterns and **automata theory**. It offers a **unified interface for parsing, converting, and generating regular languages**, making it an essential tool for lexer construction, pattern matching, and **language analysis**.

> #### Core components
 - **`RegexEngine`**: Static facade exposing all public operations: `Parse` (string → DFA), `GetAutomaton` (grammar → DFA), `GetGrammar` (automaton → grammar), and `GetRegex` (automaton → regex). It handles the entire pipeline from source text to minimized automaton.

> #### Key features
 - **`Comprehensive Regex Syntax`**: Supports concatenation, alternation (|), repetition (*, +, ?), grouping ((...)), character classes ([...]) with ranges (a-z) and negation ([^...]), predefined constants (\d, \s, \w, .), escape sequences, and bounded quantifiers ({m,n}). The parsing result is an automata.
 - **`Bidirectional Conversion`**: Beyond parsing, the engine can:
    - Convert a regular grammar (left‑linear or right‑linear) into an equivalent DFA, enabling lexer generation from grammatical descriptions.

    - Infer a regular expression from any automaton using state elimination (Brzozowski‑style), producing a readable pattern even for complex automata. This is invaluable for debugging and reverse‑engineering.

### 📉 visual

Provides **interactive graph visualization** tools for **automata, lexers, abstract syntax trees (ASTs), and parse trees**. It leverages **pyvis** and **networkx** to generate **standalone HTML files** with **embedded resources (CSS/JS)** for offline use, making it ideal for debugging, documentation, and presentations.

> #### Key features
 - `Render automata`: Draw an interactive directed graph representing any **DFA/NFA**, with transition labels, accepting states, and ε‑transitions clearly distinguished.
 - **`Visualise Lexer DFAs`**: Convenience wrapper around `draw_automaton` to directly visualise the DFA used by a lexer.
 - `Render AST`: Display **ASTs** as hierarchical trees with node attributes (non‑private, JSON‑serializable) shown as tooltips, helping to inspect the structure and data.
 - **`Render Parse Trees`**: Show the concrete syntax tree produced by a parser, with each node labelled by the grammar symbol.
 - **`Resource Caching`**: Optionally cache external stylesheets and scripts to avoid repeated downloads, generating **self‑contained HTML files** that work offline.
 - **`Export & Share`**: All graphs are saved as single HTML files that can be opened in any modern browser, shared, or embedded.

> #### Usage

#### Setting the cache file

To enable resource caching, specify a cache file path before generating any HTML:

```python
from pylgen.visual import set_cache_file

set_cache_file('vis_cache.pkl')
```

> [!note]
If the cache file path already exists, it will be loaded and updated if necessary, otherwise a new one is created. The cache stores downloaded CSS/JS resources as a pickle dictionary.

#### Drawing an automaton

```python
from pylgen.visual import draw_automaton

# ... code to create the automaton

draw_automaton(automaton, 
               filename="my_automaton",
               show=True,
               cache=True,
               physics=False,
               select_menu=False,
               filter_menu=False,
               nodes=False,
               edges=False,
               as_tree=False)

```

#### Drawing a lexer

```python
from pylgen.visual import draw_lexer

# ... code to build the lexer

draw_lexer(lexer, 
               filename="my_automaton",
               show=True,
               cache=True,
               physics=False,
               select_menu=False,
               filter_menu=False,
               nodes=False,
               edges=False,
               as_tree=False)
```

> [!note]
This is a convenience wrapper that calls `draw_automaton(lexer.dfa,**kwargs)`. All arguments are passed through.

#### Drawing an **AST**

```python
from pylgen.visual import draw_ast

# ... code to build the ast

draw_ast(ast_root, 
         filename="ast",
         show=True,
         cache=True,
         physics=False,
         select_menu=False,
         filter_menu=False,
         nodes=False,
         edges=False)
```

> [!tip]
The resulting graph shows each AST node with its label (the symbol) and, on hover, displays all non‑private, JSON‑serializable attributes for quick inspection.

#### Drawing a **Parse Tree**

```python
from pylgen.visual import draw_parse_tree_from_parser

# ... code to build the parse tree

draw_parse_tree_from_parser(parser, 
                            filename="parse_tree",
                            show=True,
                            cache=True,
                            physics=False,
                            select_menu=False,
                            filter_menu=False,
                            nodes=False,
                            edges=False)
```

Nodes are labelled with the grammar symbol

> [!note]
`draw_parse_tree_from_parser` relies on the parser’s internal parse tree. You must call `parser.set_draw_parse_tree_flag(True)` before parsing; otherwise, the tree will be empty and the visualisation will fail.

#### API Reference

All drawing functions accept the following keword arguments:

| kwarg | type | description | `draw_automaton` | `draw_lexer` | `draw_ast` | `draw_parse_tree_from_parser` |
|:---:| :---: | :--- | :---: | :---: | :---: | :---: |
| filename | `str` | specifies the name of the HTML file generated | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| show | `bool` | specifies if the file will be opened after creating | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| cache | `bool` | specifies if the cache file will be used to generate the file | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| physics | `bool` | enables the physics options in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| select_menu | `bool` | enables selecting menu in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| filter_menu | `bool` | enables filtering menu in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| nodes | `bool` | enables nodes options, see **pyvis**'s official documentation for more information | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| edges | `bool` | enables edges options, see **pyvis**'s official documentation for more information | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| ast_tree | `bool` | displays the graph as a tree | :white_check_mark: | :white_check_mark: | :x:(default) | :x:(default) |

> [!note]
For `AST` and `parse tree` rendering, the layout is fixed to a hierarchical tree structure; the as_tree parameter is ignored. All boolean parameters default to False.