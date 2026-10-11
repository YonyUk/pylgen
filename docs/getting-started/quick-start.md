# Quick Start

On this page, you will build a minimal interpreter capable of evaluating arithmetic expressions like `2 * (4 / 2 - 3) + 1`. At the end, you will see the result on the screen and, optionally, be able to visualize the AST.

The complete pipeline consists of four stages:

```text
text → Lexer → tokens → Parser → AST → Evaluation → result
```

Each stage has its own module, but for this example, you only need the high-level API.

## Step 1: Token types

A **token** is a classified piece of text. You define token types using a subclass of `TokenType`:

```python
from pylgen.common.enums import TokenType

class ArithToken(TokenType):
    NUMBER = "NUMBER"
    PLUS   = "PLUS"
    MINUS  = "MINUS"
    STAR   = "STAR"
    SLASH  = "SLASH"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF    = "EOF"
```

!!! important "The automatic member `INVALID_TOKEN`"
    The base class `TokenType`, through its custom metaclass `TokenTypeMeta`, automatically injects an `INVALID_TOKEN` member into each subclass. The lexer uses it internally to mark text that does not match any pattern.

## Step 2: Grammar symbols

A **symbol** represents an element of the grammar. There are two types:

- **Terminals**: come from the lexer (`NUMBER`, `PLUS`, ...).
- **Non-terminals**: abstract categories that expand (`E`, `T`, `F`).

```python
from pylgen.common.types import Symbol

E = Symbol("E")
T = Symbol("T")
F = Symbol("F")

number = Symbol("number", True)
plus   = Symbol("+", True)
minus  = Symbol("-", True)
star   = Symbol("*", True)
slash  = Symbol("/", True)
lparen = Symbol("(", True)
rparen = Symbol(")", True)
```

The second `True` argument marks the symbol as a terminal.

## Step 3: Build the lexer

The lexer needs a function that translates each token into its corresponding symbol:

```python
from pylgen.common.types import Symbol
from pylgen.lexer import Lexer

def to_symbol(token_type: ArithToken, text: str) -> Symbol:
    if token_type == ArithToken.NUMBER: return number
    if token_type == ArithToken.PLUS:   return plus
    if token_type == ArithToken.MINUS:  return minus
    if token_type == ArithToken.STAR:   return star
    if token_type == ArithToken.SLASH:  return slash
    if token_type == ArithToken.LPAREN: return lparen
    if token_type == ArithToken.RPAREN: return rparen
    return Symbol(text, True)
```

With this, you can now instantiate the lexer and add the patterns. The numbers in brackets represent the **priority**: the lower the number, the sooner the pattern is attempted.

```python
lexer = Lexer(to_symbol, ignore_pattern=r"\s+")
lexer.set_eof_token("$", ArithToken.EOF)

lexer[0, ArithToken.NUMBER] = r"\d+(\.\d+)?"
lexer[1, ArithToken.LPAREN] = r"\("
lexer[2, ArithToken.RPAREN] = r"\)"
lexer[3, ArithToken.STAR]   = r"\*"
lexer[4, ArithToken.SLASH]  = r"/"
lexer[5, ArithToken.PLUS]   = r"\+"
lexer[6, ArithToken.MINUS]  = r"\-"
```

## Step 4: AST nodes

Each grammar rule will construct an AST node. For this example, two nodes suffice: number and binary operation.

```python
from pylgen.common.types import AST,Token

class NumberAST(AST):

    def __init__(self,token:Token):
        line,column = token.start_position
        super().__init__(token.symbol,line,column,line,column + len(token.text))
        self._value = token.text

    @property
    def value(self) -> str:
        return self._value

    def children(self):
        return []

class BinaryOpAST(AST):

    def __init__(self,left:AST,right:AST,op:Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        super().__init__(op,sl,sc,el,ec)
        self._left = left
        self._right = right
        self._op = op

    @property
    def left(self) -> AST:
        return self._left
    
    @property
    def right(self) -> AST:
        return self._right

    def children(self):
        return [self._left,self._right]
```

## Step 5: Reducers

A **reducer** is a function that receives the child ASTs (in an `ASTListView`) and returns the parent AST. This is where the parser builds the tree.

```python
from pylgen.common.types import ASTListView

def number_reductor(asts:ASTListView) -> AST:
    return NumberAST(asts[0]) # type: ignore

def binary_reductor(asts:ASTListView) -> AST:
    left = asts[0]
    right = asts[2]
    op = asts[1].symbol
    return BinaryOpAST(left,right,op)

def single_reductor(asts:ASTListView) -> AST:
    return asts[0]

def paren_reductor(asts:ASTListView) -> AST:
    return asts[1]
```

## Step 6: Attributed grammar

An attributed grammar is a grammar in which a reducer is associated with each production. The `AttributedGrammar` class allows you to write it using `+=`:

```python
from pylgen.grammar import AttributedGrammar

G = AttributedGrammar(E,end_symbol='$')

G[E] += (E,plus,T),binary_reductor
G[E] += (E,minus,T),binary_reductor
G[E] += (T,),single_reductor

G[T] += (T,star,F),binary_reductor
G[T] += (T,slash,F),binary_reductor
G[T] += (F,),single_reductor

G[F] += (lparen,E,rparen),paren_reductor
G[F] += (number,),number_reductor
```

Each line reads: *"the non-terminal on the left can produce this sequence, and when it does, it calls this reducer"*.

## Step 7: Building the parser

The parser is built from the attributed grammar:

```python
from pylgen.parser import ParserBuilder, ParserType

parser = ParserBuilder.build_parser_from_attributed(G, ParserType.LALR1)
```

`LALR1` is the recommended type for most languages: it is powerful and generates compact tables.

## Step 8: Parsing

Now, feed the lexer and parse:

```python
source = "2 * (4 / 2 - 3) + 1"
lexer.load_text(source)
ast = parser.parse(lexer.tokens)

if lexer.errors:
  for error in lexer.errors:
    print(error)
elif parser.errors:
  for error in parser.errors:
    print(error)
else:
    print("Parsing successful!")
    print("AST root:",ast)
```

If everything goes well, `ast` is the root of the tree.

## Step 9: Evaluating the AST

The AST is evaluated by traversing it in **post-order**: first the children, then the parent. Since each node knows its children, a recursive function suffices. No visitor or shared context is needed for an example of this size.

```python
def evaluate(node):
    if isinstance(node, NumberAST):
        return float(node.value)

    if isinstance(node, BinaryOpAST):
        left  = evaluate(node.left)
        right = evaluate(node.right)
        op = node.symbol
        if op == plus:   return left + right
        if op == minus:  return left - right
        if op == star:   return left * right
        if op == slash:  return left / right

    raise TypeError(f"Node not supported: {type(node).__name__}")
```
!!! warning
    `isinstance` works here because `NumberAST` and `BinaryAST` are the only two forms the tree can take in this language. If you add a new node tomorrow, you add a branch to the `if` statement.

!!! note "What about visitors?" 
    PyLGEN includes a visitor framework (`ASTVisitor` + `ASTWalker` + `TraversalStrategy` + `ASTChildrenSelector` + `Context` + `Error`) for cases where you need to apply multiple operations to the same AST, use custom selectors, or employ non-standard traversal strategies. It offers no benefit for evaluating a simple expression. You can find details in the "User Guide" section.

## Step 10: Obtain the result

```python
result = evaluate(ast)
print(result)
```

With `source = "2 * (4 / 2 - 3) + 1"`, you will see:

```text
Parsing successful!
AST root: +
-1.0
```

You have built a complete interpreter: lexer, grammar, parser, AST, and evaluation.

## Optional Step 11: Visualize the AST

If you installed the `[visual]` extra, you can view the tree in your browser:

```python
from pylgen.visual import draw_ast
draw_ast(ast, show=True,filename='ast')
```

A file is generated and opened in the browser. It is a very convenient way to debug grammars and reducers.

!!! warning "HTML is not self-contained by default"
    By default, the generated HTML references `vis.js` and its styles from external CDNs using `<script>` and `<link>` tags. This means that, to view it correctly, you need an internet connection the first time (or the resources must be in your browser cache). If you open the file while offline, the graph will not render.

> ### How to generate self-contained HTML

PyLGEN can embed external resources (JavaScript and CSS) directly into the HTML, making the file completely standalone and capable of working offline. This is done in two steps:

 - `1`: Call `set_cache_file` once to specify where to save the downloaded resource cache.
 - `2`: Pass `cache=True` to the drawing function.

```python
from pylgen.visual import draw_ast, set_cache_file

set_cache_file("cache.pkl")   # created if it doesn't exist
draw_ast(ast, show=True, cache=True,filename='ast')
```

The first time, PyLGEN downloads the resources from CDNs, saves them to the cache file, and embeds them inline within the HTML. On subsequent runs, it reuses the local cache: there are no network requests, and the resulting HTML is self-contained. You can copy, share, or open it offline without issues.

!!! warning
    If you pass `cache=True` without first calling `set_cache_file`, PyLGEN raises a `ValueError`. The cache is global: once configured, all subsequent calls with `cache=True` will reuse it.

> ### AST View Result

<iframe src="../../assets/html/quick-start/ast.html" width="100%" height="400" style="border:none;"></iframe>

!!! tip "Visual Debugging"
    When hovering over any node in the AST visualization, a tooltip appears displaying the **node’s public**, **JSON‑serializable** properties such as its symbol, `start_position`/`end_position`, and any additional data like the variable name or operator. This allows you to inspect the node’s internal state instantly without referring back to the source code or reading the AST class definitions.

## What you have learned

- How to define token types, symbols, and lexical rules.
- How to describe an attributed grammar using `+=`.
- How to build and execute an LALR(1) parser.
- How to evaluate an AST using a post-order recursive function.