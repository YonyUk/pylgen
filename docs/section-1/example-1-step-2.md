# Step 2: Build the parser (Syntactic Analysis – Defining the Grammar)

With our lexer up and running, we now have a clean stream of tokens. But having the pieces is only half the battle, we also need to know how they fit together. For instance, `x = 10` makes perfect sense, while `= x 10` clearly doesn't. To define these structural rules, we move on to syntactic analysis.

In this step, we'll establish the grammar of our language: a set of rules that determines which sequences of tokens are valid. We'll begin by naming the basic building blocks (like numbers and variables) and then write the rules that specify how to combine them into assignments, expressions, and built-in commands.

As the parser processes the token stream and checks it against these rules, it doesn't just validate the input, it also builds a structured representation of your code called an **Abstract Syntax Tree (AST)**. Think of the AST as a simplified, hierarchical map of your program: it strips away superficial details like parentheses or whitespace and captures only the meaningful structure. For example, the parser will transform `x = 10` into a distinct node representing an assignment, with `x` on one side and `10` on the other. We'll define these node structures upfront, so the parser knows exactly what shape to produce.

The files we'll be working on are:

 - `grammar_symbols.py`: where we define the fundamental symbols.
 - `grammar.py`: where we write the combination rules, set up the parser, and tell it which AST nodes to build.
 - `asts.py`: where we define the node structure for our AST.
 - `reductors.py`: where we define how to build each AST node.

Let's start by declaring our basic building blocks.

## Grammar symbols

With the overall structure in mind, let's start by declaring the actual symbols of our grammar. These symbols,both terminals (like `+` or `number`) and non-terminals (like `E` for expression), will serve as the alphabet for our syntactic rules.

File `grammar_symbols.py`
```python
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

## Defining the AST nodes

Parallel to defining the grammar, we need to decide how the parser will represent valid programs. Instead of simply reporting "valid", we want it to produce a structured, easy‑to‑traverse tree. This is where our **Abstract Syntax Tree (AST)** nodes come into play.

We'll start by defining a base BinaryAST class that captures any binary operation. All specific binary nodes (like addition, multiplication, or assignment) will inherit from it, which saves us from repeating common logic.

File `asts.py`
```python
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
```

Now we can create a dedicated node for each binary operation, simply forwarding the operands and the corresponding symbol:

```python
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
```

For assignments, we follow the same binary structure. However, note that we override the children method to return only the right‑hand side, this is a design choice to simplify later tree traversals by treating the variable name as metadata rather than a child node.

```python
class AssignmentAST(BinaryAST):

    def __init__(self, left: AST, right: AST, line: int, column: int):
        super().__init__(left, right, eq, line, column)

    def children(self) -> List[AST]:
        return [self._right]
```

Finally, we define leaf‑like nodes for variable references and our built‑in commands:

```python 
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

Putting it all together, here is the complete asts.py module:

File `asts.py`
```python
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

With our symbols and AST nodes ready, we're all set to write the actual grammar rules and connect the parser in the next section.

## Designing our language

With our symbols and AST nodes ready, it's time to define the actual grammar rules. This is where we specify how the tokens can be combined to form valid expressions, assignments, and commands, and, crucially, which AST nodes should be built for each valid combination.

We'll use PyLGEN's `AttributedGrammar` class, which allows us to attach a **reductor** (a function) to each production. This reductor will be called during parsing whenever that production is recognized; its job is to take the children (the ASTs of the symbols on the right‑hand side) and produce a new AST node for the left‑hand side.

Let's start by importing everything we need and creating the grammar object.

```python
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
# Reductors – we will define them in the next step; for now we just import them
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
```

Now we add the production rules. Each rule has the form:
```python
G[NonTerminal] += (symbol1, symbol2, ...), reductor_function
```

> ### ArithmeticExpression -  the top-level rule

We define three possible forms for a complete input:

`1` - A simple expression (like 3 + 5).

`2` - A variable assignment (like x = 10).

`3` - A built-in command ( `exit()` or `clear()`).

```python
# ...

G[ArithmeticExpression] += (E,), single_reductor
G[ArithmeticExpression] += (VAR, eq, E), binary_reductor
G[ArithmeticExpression] += (exit, lp, rp), exit_reductor
G[ArithmeticExpression] += (clear, lp, rp), clear_reductor
```

> ### Expression rules (**E**,**T**,**F**,**P**)

We follow the classic precedence hierarchy:

 - `E`: handles addition and substraction (lowest precedence).
 - `T`: handles multiplication, division and modulo.
 - `F`: handles exponentiation.
 - `P`: handles parentheses and atomic values (numbers and variables)

```python
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
```

> ### Variable production

Finally, we define how a **VAR** non‑terminal is derived from the terminal variable. This rule will be used inside assignments and simple variable references.

```python
G[VAR] += (variable,), variable_reductor
```

> ### Building the parser

Once all rules are in place, we instruct PyLGEN to construct an LALR(1) parser from our attributed grammar. The resulting parser will be able to parse any valid input and produce an AST.

```python
parser: BottomUpParser = ParserBuilder.build_parser_from_attributed(G, ParserType.LALR1)
```

!!! note
    In this file, we are importing `binary_reductor`, `single_reductor`, and the others from the reductors module. We haven't written them yet, we'll do that in the next step. For now, it's enough to know that each reductor receives a view over a list of child AST nodes (and their associated symbols) and returns a new AST node for the left‑hand side. For example, `binary_reductor` will combine two operands with an operator to produce a `PlusAST`, `MinusAST`, or similar, depending on the specific production.

With the grammar defined and the parser built, we're almost ready to start evaluating code. The next logical step is implementing the reductors themselves, which will bridge the gap between the syntactic structure and the actual AST nodes we designed earlier.

> ### Recap

File: `grammar.py`
```python
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

G = AttributedGrammar(ArithmeticExpression,END_SYMBOL)

G[ArithmeticExpression] += (E,),single_reductor
G[ArithmeticExpression] += (VAR,eq,E),binary_reductor
G[ArithmeticExpression] += (exit,lp,rp),exit_reductor
G[ArithmeticExpression] += (clear,lp,rp),clear_reductor

G[E] += (E,plus,T),binary_reductor
G[E] += (E,minus,T),binary_reductor
G[E] += (T,),single_reductor


G[T] += (T,mul,F),binary_reductor
G[T] += (T,div,F),binary_reductor
G[T] += (T,mod,F),binary_reductor
G[T] += (F,),single_reductor

G[F] += (F,exp,P),binary_reductor
G[F] += (P,),single_reductor

G[P] += (lp,E,rp),parenthesis_reductor
G[P] += (number,),single_reductor
G[P] += (VAR,),single_reductor

G[VAR] += (variable,),variable_reductor

parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1)
```

## Connecting the Dots (The reductors)

In the previous step, we defined our grammar rules but left the reductors as placeholders. Now it's time to bring them to life.

A **reductor** is a function that receives an inmutable view over a list of AST nodes (or tokens) produced by the right‑hand side of a production and returns a single AST node for the left‑hand side. In essence, it's the builder that assembles our tree structure as the parser reduces the input. Each reductor knows exactly how to combine its children into a meaningful parent node.

Let's implement each one step by step. First, let's make a few imports:

```python
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
    AssigmentAST,
    ExitAST
)
```

> ### The Binary Reductor

The binary_reductor handles all binary operations: addition, subtraction, multiplication, division, exponentiation, modulo, and assignment. It inspects the symbol of the middle child (asts[1]), which is the operator token, to determine which AST class to instantiate. It then constructs the new node using the left child (asts[0]), the right child (asts[2]), and the operator's position information.

```python
# ...
def binary_reductor(asts:ASTListView) -> AST:
    ast_type:type = None  # type: ignore
    if asts[1].symbol == plus:
        ast_type = PlusAST
    if asts[1].symbol == minus:
        ast_type = MinusAST
    if asts[1].symbol == mul:
        ast_type = MulAST
    if asts[1].symbol == div:
        ast_type = DivAST
    if asts[1].symbol == exp:
        ast_type = ExpAST
    if asts[1].symbol == mod:
        ast_type = ModAST
    if asts[1].symbol == eq:
        ast_type = AssigmentAST
    return ast_type(asts[0],asts[2],asts[1].line,asts[1].column)
```

> ### The Single Reductor

This is the simplest reductor: it just forwards the single child it receives. It's used in rules where a non‑terminal directly maps to another non‑terminal (like `E -> T` or `F -> P`).

```python
def single_reductor(asts:ASTListView) -> AST:
    return asts[0]
```

> ### The Parenthesis Reductor

When the parser encounters `( E )`, this reductor extracts the inner expression (`asts[1]`) and discards the parentheses tokens. This effectively removes the parentheses from the AST, keeping only the meaningful content.

```python
def parenthesis_reductor(asts:ASTListView) -> AST:
    return asts[1]
```

> ### The Variable Reductor

This reductor creates a `VarAST` node from the raw token's text and its positional information. The token's text attribute holds the actual variable name (e.g., "x" or "counter").

```python
def variable_reductor(asts:ASTListView) -> AST:
    return VarAST(asts[0].text,asts[0].line,asts[0].column) # type: ignore
```

> ### Command Reductors

Finally, we have two reductors for our built‑in commands: `exit()` and `clear()`. Both simply create the corresponding AST node, using the command token's line and column for error reporting purposes.

```python
def exit_reductor(asts:ASTListView) -> AST:
    return ExitAST(asts[0].line,asts[0].column)

def clear_reductor(asts:ASTListView) -> AST:
    return ClearAST(asts[0].line,asts[0].column)
```

> ### Putting It All Together

File: `reductors.py`
```python
from typing import List

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
    AssigmentAST,
    ExitAST
)

def binary_reductor(asts:ASTListView) -> AST:
    ast_type:type = None  # type: ignore
    if asts[1].symbol == plus:
        ast_type = PlusAST
    if asts[1].symbol == minus:
        ast_type = MinusAST
    if asts[1].symbol == mul:
        ast_type = MulAST
    if asts[1].symbol == div:
        ast_type = DivAST
    if asts[1].symbol == exp:
        ast_type = ExpAST
    if asts[1].symbol == mod:
        ast_type = ModAST
    if asts[1].symbol == eq:
        ast_type = AssigmentAST
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