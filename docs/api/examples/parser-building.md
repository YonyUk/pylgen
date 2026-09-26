# Building a Parser from Scratch

Now for the parser. We will build an SLR parser without calling `ParserBuilder.build_parser`. Instead, we will use the lower-level static methods of the class to construct the LR(0) automaton, compute the ACTION and GOTO tables, and instantiate a `BottomUpParser`. The overall construction follows the description in the [`parser`](../parser/parser.md#building-a-parser-from-a-grammar) module documentation, with one implementation detail: `GOTO` stores transitions for both terminals and non-terminals, as explained below.

## Step 1: Define the Grammar

Let us use a classic arithmetic grammar with precedence, the same one described in the [`grammar`](../grammar/grammar.md#complete-example-defining-an-arithmetic-expression-grammar) module documentation.

```python
from pylgen.common.types import Symbol
from pylgen.grammar.grammar import Grammar

E = Symbol('E')
T = Symbol('T')
F = Symbol('F')
plus   = Symbol('+', True)
minus   = Symbol('-', True)
star   = Symbol('*', True)
slash   = Symbol('/', True)
lparen = Symbol('(', True)
rparen = Symbol(')', True)
number = Symbol('number', True)

G = Grammar(E, end_symbol='$')

G[E] += E, plus, T
G[E] += E, minus, T
G[E] += T,
G[T] += T, star, F
G[T] += T, slash, F
G[T] += F,
G[F] += lparen, E, rparen
G[F] += number,
```

This grammar correctly handles precedence: multiplication binds tighter than addition, and parentheses override precedence.

## Step 2: Compute `FIRST` and `FOLLOW` (Optional)

The `grammar` module computes `FIRST` and `FOLLOW` sets lazily. We can force computation to inspect them, which is instructive.

```python
print("FIRST(E + T) =", G.first([E, plus, T]))
print("FOLLOW(E) =", G.follow(E))
```

These sets are used internally by the parser builder to construct the parsing tables, so we do not need to pass them explicitly.

## Step 3: Build the Canonical LR(0) States

This is the heart of the parser construction. We will build the canonical collection of LR(0) states using the two fundamental operations:

 - `closure_lr0(items, g)`: given a set of LR(0) items, compute the **closure**. If an item has a dot before a non-terminal, add all productions of that non-terminal with the dot at the beginning, and repeat until no new items are added.

 - `goto_lr0(items, x, g)`: given a set of LR(0) items and a symbol `x`, compute the set of items obtained by moving the dot over `x` (for items that have `x` right after the dot), then take the **closure** of the result.

The algorithm is a classic worklist algorithm:

 - `1`: Start with the initial item `S' -> • S`, compute its closure, and create the first state.

 - `2`: For each state in the worklist, collect all symbols that appear right after a dot.

 - `3`: For each such symbol, compute the goto of the state on that symbol, and take the closure.

 - `4` If the resulting item set has not been seen before, create a new state and add it to the worklist.

 - `5`: Repeat until the worklist is empty.

```python
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.lr0_parser import LR0Item, LR0State

def build_lr0_states(g_aug):
    """
    Build the canonical collection of LR(0) states using closure and goto.
    """
    # Find the start production (S' -> S) of the augmented grammar
    start_production = None
    for prod in g_aug.productions:
        if prod.head == g_aug.start_symbol:
            start_production = prod
            break

    # Initial item: S' -> • S
    initial_item = LR0Item(
        start_production.head,
        [],
        list(start_production.production)
    )
    initial_items = ParserBuilder.closure_lr0({initial_item}, g_aug)

    states = []
    state_map = {}

    def add_state(items):
        key = frozenset(items)
        if key in state_map:
            return state_map[key], False
        state = LR0State(items,len(states))
        states.append(state)
        state_map[key] = state
        return state, True

    initial_state, _ = add_state(initial_items)
    worklist = [initial_state]

    while worklist:
        current = worklist.pop(0)

        # Collect all symbols that appear right after a dot
        symbols_after_dot = set()
        for item in current.items:
            if item.right:
                symbols_after_dot.add(item.right[0])

        # For each such symbol, compute goto and closure
        for sym in symbols_after_dot:
            next_items = ParserBuilder.goto_lr0(current.items, sym, g_aug)
            if not next_items:
                continue
            next_state, is_new = add_state(next_items)
            if is_new:
                worklist.append(next_state)

    return states
```

Let us run this and inspect the result:

```python
G_aug = Grammar.AugmentGrammar(G)
states = build_lr0_states(G_aug)

print(f"Number of LR(0) states: {len(states)}")
for state in sorted(states, key=lambda s: s.index):
    print(f"I{state.index}:")
    for item in state.items:
        print(f"    {item}")
    print()
```

Output:

```text
Number of LR(0) states: 16
I0:
    T ->  ◦ T / F
    E ->  ◦ T
    T ->  ◦ F
    T ->  ◦ T * F
    F ->  ◦ number
    E' ->  ◦ E
    F ->  ◦ ( E )
    E ->  ◦ E - T
    E ->  ◦ E + T

I1:
    F -> number ◦ 

I2:
    E -> T ◦ 
    T -> T ◦ / F
    T -> T ◦ * F

I3:
    T -> F ◦ 

I4:
    T ->  ◦ T / F
    E ->  ◦ T
    T ->  ◦ F
    F -> ( ◦ E )
    T ->  ◦ T * F
    F ->  ◦ number
    F ->  ◦ ( E )
    E ->  ◦ E - T
    E ->  ◦ E + T

I5:
    E -> E ◦ + T
    E' -> E ◦ 
    E -> E ◦ - T

I6:
    T -> T * ◦ F
    F ->  ◦ number
    F ->  ◦ ( E )

I7:
    F ->  ◦ number
    F ->  ◦ ( E )
    T -> T / ◦ F

I8:
    E -> E ◦ + T
    E -> E ◦ - T
    F -> ( E ◦ )

I9:
    T ->  ◦ T * F
    F ->  ◦ number
    T ->  ◦ T / F
    E -> E + ◦ T
    F ->  ◦ ( E )
    T ->  ◦ F

I10:
    T ->  ◦ T * F
    F ->  ◦ number
    T ->  ◦ T / F
    F ->  ◦ ( E )
    E -> E - ◦ T
    T ->  ◦ F

I11:
    T -> T * F ◦ 

I12:
    T -> T / F ◦ 

I13:
    F -> ( E ) ◦ 

I14:
    T -> T ◦ / F
    E -> E + T ◦ 
    T -> T ◦ * F

I15:
    T -> T ◦ / F
    E -> E - T ◦ 
    T -> T ◦ * F
```

You will see 16 states, each containing a set of LR(0) items. This is the canonical LR(0) automaton, built entirely by ourselves using `closure_lr0` and `goto_lr0`.

!!! note "What `closure_lr0` and `goto_lr0` do"
    The `closure_lr0` method implements the closure operation: if the dot is before a non-terminal, it adds all productions of that non-terminal with the dot at the beginning, and recursively takes the closure of those. The `goto_lr0` method implements the goto operation: it moves the dot over a given symbol for all items that have that symbol right after the dot, then takes the closure. Together, these two operations generate the entire LR(0) automaton. The [`parser`](../parser/parser.md#parserbuilder-the-parser-generator) module documentation describes this in more detail.

## Step 4: Build the `ACTION` and `GOTO` Tables

Now that we have the states, we build the SLR tables. We build two tables, each with a distinct role:

 - `GOTO`: maps `(state, symbol)` to a next state, for every symbol (terminal or non-terminal). This is the table the parser runtime uses: on a shift, it looks up the target state directly here, without unpacking the `ACTION` tuple or checking the type of its second element. Storing terminal transitions here as well is a deliberate performance choice, since the shift lookup happens in the hottest loop of the parser.

 - `ACTION`: maps `(state, terminal)` to a decision. It has three forms:

    - `SHIFT`: `('SHIFT', S')`, where `S'` is the target state. The runtime does not need this state (it reads it from `GOTO`), but storing it here makes the table self-contained and readable when inspected or printed.

    - `REDUCE`: `('REDUCE', A -> α)`, where `A -> α` is the production to apply.

    - `ACCEPT`: `('ACCEPT', None)`.

The rules for filling these tables are:

 - For each state `S` and symbol `x` (terminal or non-terminal), if `goto(S, x) = S'`, set `GOTO[S, x] = S'`.

 - For each state `S` and terminal `a`, if `goto(S, a) = S'`, set `ACTION[S, a] = ('SHIFT', S')`.

 - For each state `S` with a completed item `A -> α •` (where `A` is not the augmented start symbol), and each `a` in `FOLLOW(A)`, set `ACTION[S, a] = ('REDUCE', A -> α)`.

 - For the completed item `S' -> S •`, set `ACTION[S, $] = ('ACCEPT', None)`.

```python
from pylgen.grammar.grammar import Production

def build_slr_tables(g_aug, states):
    """
    Build the SLR ACTION and GOTO tables from the LR(0) states.
    """
    # Index states by their item set for quick lookup
    state_by_items = {frozenset(s.items): s for s in states}

    goto_table = {}
    action_table = {}

    for state in states:
        # Collect symbols that appear right after a dot
        symbols_after_dot = set()
        for item in state.items:
            if item.right:
                symbols_after_dot.add(item.right[0])

        # SHIFT and GOTO actions
        for sym in symbols_after_dot:
            next_items = ParserBuilder.goto_lr0(state.items, sym, g_aug)
            if not next_items:
                continue
            next_state = state_by_items[frozenset(next_items)]
            goto_table[(state, sym)] = next_state
            action_table[(state, sym)] = ('SHIFT', next_state)

        # REDUCE and ACCEPT actions
        for item in state.items:
            if not item.right:
                # Completed item: A -> α •
                if item.head == g_aug.start_symbol:
                    action_table[(state, g_aug.end_symbol)] = ('ACCEPT', None)
                else:
                    production = Production(item.head, item.left)
                    for a in g_aug.follow(item.head):
                        action_table[(state, a)] = ('REDUCE', production)

    return goto_table, action_table
```

Let us run this and inspect the result:

```python
goto_table,action_table = build_slr_tables(G_aug,states)

print("GOTO entries:")
for (state, sym), target in list(goto_table.items()):
    print(f"  GOTO[I{state.index}, {sym}] = I{target.index}")

print()
print("\nACTION entries:")
for (state, sym), (action, value) in list(action_table.items()):
    if isinstance(value,LR0State):
        print(f"  ACTION[I{state.index}, {sym}] = {action}, I{value.index}")
    else:
        print(f"  ACTION[I{state.index}, {sym}] = {action}, {value}")
```

Output:

```text
GOTO entries:
  GOTO[I0, number] = I1
  GOTO[I0, T] = I2
  GOTO[I0, F] = I3
  GOTO[I0, (] = I4
  GOTO[I0, E] = I5
  GOTO[I2, *] = I6
  GOTO[I2, /] = I7
  GOTO[I4, number] = I1
  GOTO[I4, T] = I2
  GOTO[I4, F] = I3
  GOTO[I4, (] = I4
  GOTO[I4, E] = I8
  GOTO[I5, +] = I9
  GOTO[I5, -] = I10
  GOTO[I6, number] = I1
  GOTO[I6, (] = I4
  GOTO[I6, F] = I11
  GOTO[I7, number] = I1
  GOTO[I7, (] = I4
  GOTO[I7, F] = I12
  GOTO[I8, )] = I13
  GOTO[I8, +] = I9
  GOTO[I8, -] = I10
  GOTO[I9, number] = I1
  GOTO[I9, (] = I4
  GOTO[I9, F] = I3
  GOTO[I9, T] = I14
  GOTO[I10, number] = I1
  GOTO[I10, (] = I4
  GOTO[I10, F] = I3
  GOTO[I10, T] = I15
  GOTO[I14, *] = I6
  GOTO[I14, /] = I7
  GOTO[I15, *] = I6
  GOTO[I15, /] = I7


ACTION entries:
  ACTION[I0, number] = SHIFT, I1
  ACTION[I0, (] = SHIFT, I4
  ACTION[I0, T] = SHIFT, I2
  ACTION[I0, F] = SHIFT, I3
  ACTION[I0, E] = SHIFT, I5
  ACTION[I1, *] = REDUCE, F -> number
  ACTION[I1, +] = REDUCE, F -> number
  ACTION[I1, )] = REDUCE, F -> number
  ACTION[I1, $] = REDUCE, F -> number
  ACTION[I1, /] = REDUCE, F -> number
  ACTION[I1, -] = REDUCE, F -> number
  ACTION[I2, *] = SHIFT, I6
  ACTION[I2, /] = SHIFT, I7
  ACTION[I2, )] = REDUCE, E -> T
  ACTION[I2, $] = REDUCE, E -> T
  ACTION[I2, +] = REDUCE, E -> T
  ACTION[I2, -] = REDUCE, E -> T
  ACTION[I3, *] = REDUCE, T -> F
  ACTION[I3, +] = REDUCE, T -> F
  ACTION[I3, )] = REDUCE, T -> F
  ACTION[I3, $] = REDUCE, T -> F
  ACTION[I3, /] = REDUCE, T -> F
  ACTION[I3, -] = REDUCE, T -> F
  ACTION[I4, number] = SHIFT, I1
  ACTION[I4, (] = SHIFT, I4
  ACTION[I4, T] = SHIFT, I2
  ACTION[I4, F] = SHIFT, I3
  ACTION[I4, E] = SHIFT, I8
  ACTION[I5, +] = SHIFT, I9
  ACTION[I5, -] = SHIFT, I10
  ACTION[I5, $] = ACCEPT, None
  ACTION[I6, number] = SHIFT, I1
  ACTION[I6, (] = SHIFT, I4
  ACTION[I6, F] = SHIFT, I11
  ACTION[I7, number] = SHIFT, I1
  ACTION[I7, (] = SHIFT, I4
  ACTION[I7, F] = SHIFT, I12
  ACTION[I8, )] = SHIFT, I13
  ACTION[I8, +] = SHIFT, I9
  ACTION[I8, -] = SHIFT, I10
  ACTION[I9, number] = SHIFT, I1
  ACTION[I9, (] = SHIFT, I4
  ACTION[I9, T] = SHIFT, I14
  ACTION[I9, F] = SHIFT, I3
  ACTION[I10, number] = SHIFT, I1
  ACTION[I10, (] = SHIFT, I4
  ACTION[I10, T] = SHIFT, I15
  ACTION[I10, F] = SHIFT, I3
  ACTION[I11, *] = REDUCE, T -> T * F
  ACTION[I11, +] = REDUCE, T -> T * F
  ACTION[I11, )] = REDUCE, T -> T * F
  ACTION[I11, $] = REDUCE, T -> T * F
  ACTION[I11, /] = REDUCE, T -> T * F
  ACTION[I11, -] = REDUCE, T -> T * F
  ACTION[I12, *] = REDUCE, T -> T / F
  ACTION[I12, +] = REDUCE, T -> T / F
  ACTION[I12, )] = REDUCE, T -> T / F
  ACTION[I12, $] = REDUCE, T -> T / F
  ACTION[I12, /] = REDUCE, T -> T / F
  ACTION[I12, -] = REDUCE, T -> T / F
  ACTION[I13, *] = REDUCE, F -> ( E )
  ACTION[I13, +] = REDUCE, F -> ( E )
  ACTION[I13, )] = REDUCE, F -> ( E )
  ACTION[I13, $] = REDUCE, F -> ( E )
  ACTION[I13, /] = REDUCE, F -> ( E )
  ACTION[I13, -] = REDUCE, F -> ( E )
  ACTION[I14, *] = SHIFT, I6
  ACTION[I14, /] = SHIFT, I7
  ACTION[I14, )] = REDUCE, E -> E + T
  ACTION[I14, $] = REDUCE, E -> E + T
  ACTION[I14, +] = REDUCE, E -> E + T
  ACTION[I14, -] = REDUCE, E -> E + T
  ACTION[I15, *] = SHIFT, I6
  ACTION[I15, /] = SHIFT, I7
  ACTION[I15, )] = REDUCE, E -> E - T
  ACTION[I15, $] = REDUCE, E -> E - T
  ACTION[I15, +] = REDUCE, E -> E - T
  ACTION[I15, -] = REDUCE, E -> E - T
```

The `ACTION` table maps `(state,terminal)` to a tuple `(action,value)`, where `action` is `'SHIFT'`, `'REDUCE'` or `'ACCEPT'`. For `'SHIFT'`, `value` is the target state. For `'REDUCE'`, `value` is a `Production` object.

!!! note "Why `GOTO` contains terminal entries, and why `ACTION` repeats the target state"
    Two deliberate choices are visible in the tables above:

     - `GOTO` stores transitions for both terminals and non-terminals. Classical LR theory defines `GOTO` only over non-terminals, but storing terminal transitions here lets the runtime perform a shift with a single lookup, without unpacking the `ACTION` tuple or checking the type of its second element.

    - `ACTION` also stores the target state for `SHIFT`, even though the runtime reads it from `GOTO`. This redundancy is intentional: it makes the `ACTION` table self-contained, so it can be printed, inspected, or rendered in a report without cross-referencing `GOTO`.

    Neither choice changes the LR algorithm or the language recognized by the parser. They are implementation details that trade a small amount of memory for speed and clarity.

## Step 5: Instantiate the `BottomUpParser`

The `BottomUpParser` constructor takes the start state `ID`, the `GOTO` table, and the `ACTION` table. The tables must be keyed by state `ID`s (strings), not state objects. We need to convert.

```python
from pylgen.parser import BottomUpParser

start_state_id = 'I0'

goto_dict = {}
for (state,sym),target in goto_table.items():
    goto_dict[(f'I{state.index}',sym)] = f'I{target.index}'

action_dict = {}
for (state,sym),(action,value) in action_table.items():
    if action == 'SHIFT':
        action_dict[(f'I{state.index}',sym)] = (action,f'I{value.index}')
    elif action == 'REDUCE':
        action_dict[(f'I{state.index}',sym)] = (action,value)
    else:
        action_dict[(f'I{state.index}',sym)] = (action,None)

parser = BottomUpParser(start_state_id,goto_dict,action_dict)
```

This separation between the state construction (which works with `LR0State` objects) and the parser runtime (which works with state `ID`s) keeps the runtime lightweight and fast.

## Step 6: Attach Reductors

The parser does **not** build anything by itself. Every reduction requires a reductor, and every production in the grammar must have one assigned before parsing can proceed. If a reduction is triggered for a production without a reductor, the parser will fail. This is a deliberate design choice: PyLGEN wants every semantic action to be under explicit user control, so nothing happens behind your back.

A reductor is a function that takes the ASTs of the right-hand side symbols (wrapped in `ASTListView`) and returns a new AST for the left-hand side non-terminal. This is the cornerstone of attributed grammars, as described in the [`grammar`](../grammar/grammar.md#attributedgrammar-grammar-with-reductors) module documentation.

```python
from pylgen.common.types import AST,Token,ASTListView

class NumberAST(AST):

    def __init__(self,token:Token):
        line,column = token.start_position
        super().__init__(token.symbol,line,column,line,column + len(token.text))
        self._value = token.text

    def children(self):
        return []

class BinaryOpAST(AST):

    def __init__(self,left:AST,right:AST,op:Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        super().__init__(op,sl,sc,el,ec)
        self._left = left
        self._right = right
        self._op = op
    
    def children(self):
        return [self._left,self._right]

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

for prod in G_aug.productions:
    if prod.head == F and prod.production == [number]:
        parser[prod] = number_reductor
    elif prod.head in (E,T) and len(prod.production) == 3:
        parser[prod] = binary_reductor
    elif prod.head == F and len(prod.production) == 3:
        parser[prod] = paren_reductor
    else:
        parser[prod] = single_reductor
```

!!! warning "No default reductor"
    There is no built-in default reductor. If you want a generic fallback (for example, an AST node that simply wraps the children without any semantic interpretation), you can assign one explicitly to every production you have not covered. But that is a choice you make, not something the parser does for you. The parser has no opinion about what your AST should look like; it only knows how to reduce productions, and it will ask you for the reductor every time.

!!! note "The parse tree is a separate feature"
    If you want the parser to also build a parse tree (the concrete syntax tree, including all grammar symbols), you can enable it with `parser.set_draw_parse_tree_flag(True)` before parsing. This is orthogonal to reductors: you can have reductors without a parse tree, a parse tree without reductors, or both. The parse tree is useful for visualization and debugging, and the [`visual`](../visual/visual.md#drawing-parse-trees) module can draw it. But it is not built by default, and it does not replace the need for reductors.

## Step 7: Parse

Now we can tokenize and parse. Remember that our simple tokenizer does not emit tokens nor an EOF token, so we need to do that manually.

!!! note
    We must added the enum `MyTokenTypeEnum` due to `Token` constructor requires a member of a subclass of `TokenType` for the `type_` parameter.

```python
from pylgen.common.enums import TokenType

class MyTokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    SPACE = 'SPACE'
    EOF = 'EOF'


SYMBOL_MAP = {
    'NUMBER': number,
    'PLUS':   plus,
    'MINUS':  minus,
    'STAR':   star,
    'SLASH':  slash,
    'LPAREN': lparen,
    'RPAREN': rparen,
}

text = "1 + 2 * (3 - 4 / 2)"
raw_tokens = tokenize(text, patterns)

tokens = []
column = 0
for token_type, token_text in raw_tokens:
    if token_type == 'SPACE':
        column += len(token_text)
        continue
    tokens.append(Token(token_text, MyTokenTypeEnum[token_type], SYMBOL_MAP[token_type], 1, text.index(token_text,column) + 1))
    column += len(token_text)

eof_token = Token('$', MyTokenTypeEnum['EOF'], Symbol('$', True), 1, len(text) + 1)
tokens.append(eof_token)

ast = parser.parse(tokens)

if parser.errors:
    for error in parser.errors:
        print(error)
else:
    print("Parsing successful!")
    print(ast)
```

!!! note
    This example reuses the `tokenize` function and the `patterns` list from the lexer section.

## The Complete Pipeline

Here is the full script, combining the simple lexer with the self-constructed parser.

```python
from pylgen.regex import RegexEngine
from pylgen.common.types import Symbol, Token, AST, ASTListView
from pylgen.grammar.grammar import Grammar, Production
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.lr0_parser import LR0Item, LR0State
from pylgen.parser.parser import BottomUpParser
from pylgen.common.enums import TokenType

# ============================================================
# PART 0: Tokens enumeration
# ============================================================

class MyTokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    SPACE = 'SPACE'
    EOF = 'EOF'

# ============================================================
# PART 1: SIMPLE LEXER
# ============================================================

patterns = [
    ('NUMBER', RegexEngine.Parse(r'\d+')),
    ('PLUS',   RegexEngine.Parse(r'\+')),
    ('MINUS',  RegexEngine.Parse(r'\-')),
    ('STAR',   RegexEngine.Parse(r'\*')),
    ('SLASH',  RegexEngine.Parse(r'/')),
    ('LPAREN', RegexEngine.Parse(r'\(')),
    ('RPAREN', RegexEngine.Parse(r'\)')),
    ('SPACE',  RegexEngine.Parse(' |\t|\n')),
]

def longest_match(dfa, text, pos):
    """
    Return the length of the longest prefix of text[pos:]
    that is accepted by the given DFA.
    """
    best = 0
    stop = True
    for end in range(pos + 1, len(text) + 1):
        if dfa.accept(list(text[pos:end])):
            best = end - pos
            stop = False
        if stop:
            break
    return best

def tokenize(text, patterns):
    """
    Maximal munch tokenizer.
    Returns a list of (type, text) pairs.
    """
    pos = 0
    tokens = []
    while pos < len(text):
        best_type = None
        best_len = 0
        for token_type, dfa in patterns:
            length = longest_match(dfa, text, pos)
            if length > best_len:
                best_len = length
                best_type = token_type
        if best_len == 0:
            raise ValueError(
                f"Unexpected character at position {pos}: {text[pos]!r}"
            )
        tokens.append((best_type, text[pos:pos + best_len]))
        pos += best_len
    return tokens

# ============================================================
# PART 2: GRAMMAR
# ============================================================

E = Symbol('E')
T = Symbol('T')
F = Symbol('F')
plus   = Symbol('+', True)
minus   = Symbol('-', True)
star   = Symbol('*', True)
slash   = Symbol('/', True)
lparen = Symbol('(', True)
rparen = Symbol(')', True)
number = Symbol('number', True)

G = Grammar(E, end_symbol='$')

G[E] += E, plus, T
G[E] += E, minus, T
G[E] += T,
G[T] += T, star, F
G[T] += T, slash, F
G[T] += F,
G[F] += lparen, E, rparen
G[F] += number,

# ============================================================
# PART 3: PARSER CONSTRUCTION
# ============================================================

G_aug = Grammar.AugmentGrammar(G)

# --- Step 3a: Build LR(0) states using closure and goto ---

def build_lr0_states(g_aug):
    """
    Build the canonical collection of LR(0) states using closure and goto.
    """
    # Find the start production (S' -> S) of the augmented grammar
    start_production = None
    for prod in g_aug.productions:
        if prod.head == g_aug.start_symbol:
            start_production = prod
            break

    # Initial item: S' -> • S
    initial_item = LR0Item(
        start_production.head,
        [],
        list(start_production.production)
    )
    initial_items = ParserBuilder.closure_lr0({initial_item}, g_aug)

    states = []
    state_map = {}

    def add_state(items):
        key = frozenset(items)
        if key in state_map:
            return state_map[key], False
        state = LR0State(items,len(states))
        states.append(state)
        state_map[key] = state
        return state, True

    initial_state, _ = add_state(initial_items)
    worklist = [initial_state]

    while worklist:
        current = worklist.pop(0)

        # Collect all symbols that appear right after a dot
        symbols_after_dot = set()
        for item in current.items:
            if item.right:
                symbols_after_dot.add(item.right[0])

        # For each such symbol, compute goto and closure
        for sym in symbols_after_dot:
            next_items = ParserBuilder.goto_lr0(current.items, sym, g_aug)
            if not next_items:
                continue
            next_state, is_new = add_state(next_items)
            if is_new:
                worklist.append(next_state)

    return states

states = build_lr0_states(G_aug)

# --- Step 3b: Build the ACTION and GOTO tables ---

def build_slr_tables(g_aug, states):
    """
    Build the SLR ACTION and GOTO tables from the LR(0) states.
    """
    # Index states by their item set for quick lookup
    state_by_items = {frozenset(s.items): s for s in states}

    goto_table = {}
    action_table = {}

    for state in states:
        # Collect symbols that appear right after a dot
        symbols_after_dot = set()
        for item in state.items:
            if item.right:
                symbols_after_dot.add(item.right[0])

        # SHIFT and GOTO actions
        for sym in symbols_after_dot:
            next_items = ParserBuilder.goto_lr0(state.items, sym, g_aug)
            if not next_items:
                continue
            next_state = state_by_items[frozenset(next_items)]
            goto_table[(state, sym)] = next_state
            action_table[(state, sym)] = ('SHIFT', next_state)

        # REDUCE and ACCEPT actions
        for item in state.items:
            if not item.right:
                # Completed item: A -> α •
                if item.head == g_aug.start_symbol:
                    action_table[(state, g_aug.end_symbol)] = ('ACCEPT', None)
                else:
                    production = Production(item.head, item.left)
                    for a in g_aug.follow(item.head):
                        action_table[(state, a)] = ('REDUCE', production)

    return goto_table, action_table

goto_table, action_table = build_slr_tables(G_aug, states)

# --- Step 3c: Instantiate the parser ---

start_state_id = f'I{next(s for s in states if s.index == 0).index}'

goto_dict = {}
for (state,sym),target in goto_table.items():
    goto_dict[(f'I{state.index}',sym)] = f'I{target.index}'

action_dict = {}
for (state,sym),(action,value) in action_table.items():
    if action == 'SHIFT':
        action_dict[(f'I{state.index}',sym)] = (action,f'I{value.index}')
    elif action == 'REDUCE':
        action_dict[(f'I{state.index}',sym)] = (action,value)
    else:
        action_dict[(f'I{state.index}',sym)] = (action,None)

parser = BottomUpParser(start_state_id,goto_dict,action_dict)

# ============================================================
# PART 4: REDUCTORS (MANDATORY FOR EVERY PRODUCTION)
# ============================================================

class NumberAST(AST):

    def __init__(self,token:Token):
        line,column = token.start_position
        super().__init__(token.symbol,line,column,line,column + len(token.text))
        self._value = token.text

    def children(self):
        return []

class BinaryOpAST(AST):

    def __init__(self,left:AST,right:AST,op:Symbol):
        (sl,sc),(el,ec) = left.start_position,right.end_position
        super().__init__(op,sl,sc,el,ec)
        self._left = left
        self._right = right
        self._op = op

    def children(self):
        return [self._left,self._right]

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

for prod in G_aug.productions:
    if prod.head == F and prod.production == [number]:
        parser[prod] = number_reductor
    elif prod.head in [E,T] and len(prod.production) == 3:
        parser[prod] = binary_reductor
    elif prod.head == F and len(prod.production) == 3:
        parser[prod] = paren_reductor
    else:
        parser[prod] = single_reductor

# ============================================================
# PART 5: RUN
# ============================================================

SYMBOL_MAP = {
    'NUMBER': number,
    'PLUS':   plus,
    'MINUS':  minus,
    'STAR':   star,
    'SLASH':  slash,
    'LPAREN': lparen,
    'RPAREN': rparen,
}

text = "1 + 2 * (3 - 4 / 2)"
raw_tokens = tokenize(text, patterns)

tokens = []
column = 0
for token_type, token_text in raw_tokens:
    if token_type == 'SPACE':
        continue
    tokens.append(Token(token_text, MyTokenTypeEnum[token_type], SYMBOL_MAP[token_type], 1, text.index(token_text,column) + 1))
    column += len(token_text)

eof_token = Token('$', MyTokenTypeEnum['EOF'], Symbol('$', True), 1, len(text) + 1)
tokens.append(eof_token)

ast = parser.parse(tokens)

if parser.errors:
    for error in parser.errors:
        print(error)
else:
    print("Parsing successful!")
    print("AST root:",ast)
```

Output:

```text
Parsing successful!
AST root: +
```

We have now built a complete lexer and parser from the ground up, using only the raw API components. The lexer uses a pure maximal munch implementation, and the parser constructs the LR(0) automaton itself using `closure_lr0` and `goto_lr0`, builds the SLR tables from those states, instantiates a `BottomUpParser`, and assigns a reductor to every production. This is the same pipeline that the `Lexer` and `ParserBuilder.build_parser` classes use internally, but exposed for inspection and customization.

!!! tip "What we gained by building the states ourselves"
    By using `closure_lr0` and `goto_lr0` directly, we saw exactly how the LR(0) automaton is constructed: start with the initial item, take the closure, then repeatedly compute the goto on each symbol after a dot, take the closure, and add the result as a new state if it has not been seen before. This is the fundamental algorithm behind all LR parsers, and building it by hand makes the theory concrete. The same pattern applies to LR(1) and LALR(1), with the additional complexity of lookahead propagation.

## A Note on LALR(1) vs SLR

In the parser example above, we built an SLR parser. SLR is simple and works for many grammars, but it is not as powerful as LALR(1). For more complex grammars, you may need LALR(1).

The process for LALR(1) is analogous, but you would use:

 - `ParserBuilder.closure_lalr(items, g_aug)` instead of `closure_lr0`.

 - `ParserBuilder.goto_lalr(items, sym, g_aug)` instead of `goto_lr0`.

 - `ParserBuilder.build_lookaheads_propagation_edges(g_aug)` to compute the lookahead propagation edges.

The `ParserBuilder` also provides `get_canonical_lalr_states` and `get_goto_action_tables_lalr`, which do all of this for you. But now you know what is happening under the hood.

!!! tip "Pedagogical recommendation"
    Start with SLR. It is easier to understand, and it works for most simple languages. When you encounter a grammar that SLR cannot handle, switch to LALR(1). The [`parser`](../parser/parser.md#building-a-parser-from-a-grammar) module documentation provides a detailed comparison of the two approaches.

## Common Pitfalls and Debugging Tips

> ### Pitfall 1: Forgetting to Augment the Grammar

If you forget to call `Grammar.AugmentGrammar(G)`, the parser will not know when to accept. The augmented grammar adds a new start symbol `S'` and a production `S' -> S`. This is essential for the LR parsing algorithm.

> ### Pitfall 2: Mismatched State IDs

When converting the `GOTO` and `ACTION` tables, make sure you use the same state `ID` format (e.g., `f"I{state.index}"`) consistently. If you mix formats, the parser will not find the entries.

> ### Pitfall 3: Missing EOF Token

The `BottomUpParser` expects the token stream to end with an EOF token. If you forget to append it, the parser will not be able to complete the parsing.

> ### Pitfall 4: Missing Reductor for a Production

Since the parser does not build anything by itself, every production must have a reductor assigned. If a reduction is triggered for a production without one, the parser will fail. If you want a generic fallback, assign a default reductor explicitly to every remaining production, but remember that this is your choice, not a default behavior. Keeping reductors explicit ensures that every semantic action is under your control.

> ### Pitfall 5: Reductor Signature Mismatch

Reductors must have the signature `(ASTListView) -> AST`. PyLGEN validates the signature at addition time, so you will get an error early if the signature is incorrect.

> ### Debugging Tip: Visualize the Automaton

The [`visual`](../visual/visual.md#drawing-automata-and-lexers) module can draw your DFA and LR(0) automaton. This is invaluable for understanding what is happening.

```python
from pylgen.visual import draw_lexer, lr_inspect_grammar

draw_lexer(lexer, show=True) # lexer must be an instance of BaseLexer
lr_inspect_grammar(G, 'SLR', show=True)
```

The `lr_inspect_grammar` function generates an HTML report with the `ACTION` and `GOTO` tables, highlighting conflicts in red. This is essential for diagnosing ambiguities.

## Summary

In this section, we built a lexer and a parser from scratch, using only the raw API components of PyLGEN. The lexer uses a pure maximal munch algorithm, asking each token DFA for its longest match at each position. We saw that this naive approach has a worst-case complexity of $O \lparen k \cdot n^3 \rparen$, and we discussed how combining all token DFAs into a single automaton (using `Union`, determinization, completion with a fault state, and minimization), reduces this to $O \lparen n \rparen$. That optimized approach is exactly what `BaseLexer` implements.

The parser constructs the LR(0) automaton itself using `closure_lr0` and `goto_lr0`, builds the SLR tables from those states, and instantiates a `BottomUpParser`. We assigned a reductor to every production, because the parser does not build anything by itself: every semantic action must be explicitly defined. If we want a parse tree in addition to the AST, we can enable it with `set_draw_parse_tree_flag(True)`, but that is a separate feature and does not replace the reductors.

This exercise demonstrates the pedagogical philosophy of PyLGEN: every stage of the compilation pipeline is exposed, documented, and accessible. There are no black boxes. By building from scratch, we gain a deep understanding of the algorithms and data structures that power the framework, and we acquire the knowledge to customize and extend it for our own needs.

The high-level API is there to save time, but the low-level API is there to give control. Use them wisely, and happy language building!