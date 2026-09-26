# Building a Lexer from Scratch

A lexer is, at its core, a finite automaton that recognizes tokens. But before we reach for the `BaseLexer` class, let us build the scanning algorithm ourselves. This will show us exactly what [**maximal munch**](https://en.wikipedia.org/wiki/Maximal_munch) means, and how a DFA is used to recognize tokens.

## The Idea Behind Maximal Munch

The maximal munch algorithm is the standard strategy for tokenization. It says: at each position in the input, find the longest prefix that matches any token pattern. If two patterns match the same length, the one with the higher priority wins.

To implement this, we need a DFA for each token pattern. Then, at each position, we ask each DFA: *"What is the longest prefix of the remaining input that you accept?"* The DFA that gives the longest answer wins.

## Step 1: Build a DFA for Each Token Pattern

We use the `regex` engine to turn each pattern into a minimized DFA. This is the same `RegexEngine.Parse` method we saw in the module documentation.

```python
from pylgen.regex import RegexEngine

# Build a DFA for each token pattern, in priority order.
# The order matters: if two patterns match the same length, the first one wins.
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
```

Notice that we do not use `TokenType` here. We are keeping things simple: each pattern is just a string label and a DFA. This is the raw API, without the convenience of the `TokenType` enumeration.

## Step 2: Find the Longest Match

Now we need a function that, given a DFA and a position in the input, returns the length of the longest prefix accepted by the DFA. The `DFA.accept` method from the [`automaton`](../automaton/intro.md) module does exactly what we need: it takes a list of symbols and returns `True` if the DFA accepts it.

```python
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
```

Let us trace through this. For `text = "1 + 2 * (3 - 4/2)"`, `pos = 0`, and the `NUMBER` DFA:

 - `end = 1`: `accept(['1'])` -> `True`. `best = 1`. `stop = False`..

 - `end = 4`: `accept(['1', ' '])` -> `False`. `best` stays `1`.

So `longest_match` returns `1`, which is the length of `"1"`.

Now consider a case where the first character does not match at all. For `text = "+ 4"`, `pos = 0`, and the `NUMBER` DFA:

 - `end = 1`: `accept(['+'])` -> `False`. `stop` is still `True`, so we break immediately.

 - Return `0`.

The `stop` flag lets us exit early: if we have not accepted anything yet and the current prefix fails, no longer prefix will succeed either. Once we have accepted something, we keep going to find the longest match.

## Step 3: The Tokenization Loop

Now we put it all together. At each position, we ask each DFA for its longest match. The DFA with the longest match wins. If two DFAs tie, the one that appears first in the `patterns` list wins.

```python
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
```

Let us trace through `text = "1 + 2 * (3 - 4/2)"`:

 - `pos = 0`:

    - `NUMBER` matches `"1"` (length 1).

    - `PLUS` matches nothing (length 0).

    - `SPACE` matches nothing (length 0).

    - Best: `NUMBER`, length 1. Emit `('NUMBER', '1')`. `pos = 1`.

 - `pos = 1`:

    - `NUMBER` matches nothing.

    - `PLUS` matches nothing.

    - `SPACE` matches `" "` (length 1).

    - Best: `SPACE`, length 1. Emit `('SPACE', ' ')`. `pos = 2`.

 - `pos = 2`:

    - `NUMBER` matches nothing.

    - `PLUS` matches `"+"` (length 1).

    - Best: `PLUS`, length 1. Emit `('PLUS', '+')`. `pos = 3`.

 - ... and so on.

## Step 4: Run the Tokenizer

Now we can tokenize a full expression. We filter out the `SPACE` tokens for display, since they are not interesting.

```python
text = "1 + 2 * (3 - 4/2)"
for token_type, token_text in tokenize(text, patterns):
    if token_type != 'SPACE':
        print(token_type, repr(token_text))
```

Output:
```text
NUMBER '1'
PLUS '+'
NUMBER '2'
STAR '*'
LPAREN '('
NUMBER '3'
MINUS '-'
NUMBER '4'
SLASH '/'
NUMBER '2'
RPAREN ')'
```

## The Complete Lexer

Here is the full script, ready to run.

```python
from pylgen.regex import RegexEngine

# Build a DFA for each token pattern, in priority order.
# The order matters: if two patterns match the same length, the first one wins.
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

text = "1 + 2 * (3 - 4/2)"
for token_type, token_text in tokenize(text, patterns):
    if token_type != 'SPACE':
        print(token_type, repr(token_text))
```

This is a pure implementation of maximal munch, using only the [`regex`](../regex/regex.md) and [`automaton`](../automaton/intro.md) modules. No `TokenType`, no `BaseLexer`, no `Symbol`. Just the raw API and the scanning algorithm.

## A Note on Complexity: Why This Is Slow

Before we move on, let us pause and think about the cost of this algorithm. It is a good exercise in algorithmic analysis, and it will motivate the more efficient approach that `BaseLexer` actually uses.

Let $n$ be the length of the input text, and $k$ the number of token patterns. What is the time complexity of `tokenize`?

 - The outer while loop runs at most $n$ times, because each iteration consumes at least one character.

 - Inside the loop, for each of the $k$ patterns, we call `longest_match`.

 - `longest_match` iterates over `end` from `pos + 1` to `len(text)`, which is at most $n$ iterations.

 - Each iteration calls `dfa.accept(list(text[pos:end]))`. The slice `text[pos:end]` has length `end- pos`, and `dfa.accept` processes it in $O \lparen$ `end` - `pos` $\rparen$ time. So each call to `accept` costs $O \lparen n \rparen$ in the worst case.

Putting it all together, the worst-case complexity is:

$$
O \lparen n \rparen \times O \lparen k \rparen \times O \lparen n \rparen \times O \lparen n \rparen = O \lparen k \cdot n^3 \rparen
$$

That is cubic in the length of the input. For a small calculator language, this is fine. But for a real programming language with thousands of tokens and megabytes of source code, this would be unusably slow.

!!! note "The `stop` flag helps, but not enough"
    The `stop` flag lets us exit `longest_match` early when the first character fails to match. This helps in practice, but it does not change the worst-case complexity. When patterns match long prefixes (like `\d+` on a long number), `longest_match` still explores every possible prefix length.

## The Path to $O \lparen n \rparen$: A Single Combined DFA

The inefficiency comes from two sources:

 - `1`: We try each pattern separately, which multiplies the cost by $k$.

 - `2`: For each pattern, we re-scan the input from the current position, which is redundant.

Both problems can be solved by combining all token DFAs into a **single DFA** that recognizes the union of all token languages, and then running that DFA over the input **once**, character by character.

The [`automaton`](../automaton/automaton.md#static-methods-of-automaton-language-operations) module provides exactly the operations we need:

 - `Automaton.Union(automatons)` builds an NFA that recognizes the union of all input automata. This NFA has a new start state with ε-transitions to the start state of each original DFA.

 - `NFA.to_deterministic()` converts the NFA into an equivalent DFA using the subset (powerset) construction.

 - `DFA.make_complete()` adds a fault state (often denoted `q⊥`) and fills in all missing transitions by pointing them to this fault state. The fault state loops to itself on all symbols and is not accepting.

 - `DFA.minimize()` reduces the DFA to its smallest equivalent form, while preserving the ability to distinguish token types (by using an appropriate initial partition).

Once we have this combined DFA, the scanning algorithm becomes:

 - `1`: Start at the initial state of the combined DFA.

 - `2`: Read the input character by character.

 - `3`: At each step, follow the transition for the current character.

 - `4`: Keep track of the last accepting state encountered, and the position at which it was encountered.

 - `5`: When the DFA enters the fault state, we have gone past the longest match. Backtrack to the last accepting state, emit the corresponding token, and resume scanning from there.

 - `6`: If we never reached an accepting state before hitting the fault state, report a lexical error.

This algorithm runs in $O \lparen n \rparen$ time: each character of the input is read exactly once, and the DFA transitions are $O \lparen 1 \rparen$ dictionary lookups. The fault state tells us exactly when to stop, and the last accepting state tells us exactly where to cut the token. No backtracking over the input is needed, only over the DFA's state history, which is bounded by the length of the current token.

!!! tip "This is exactly what `BaseLexer` does"
    The [`BaseLexer`](../lexer/lexer.md#baselexer-the-scanning-engine) class in the `lexer` module implements precisely this algorithm. It combines all token automata into a single NFA using `Union`, determinizes it, completes it with a fault state, and minimizes it with an initial partition that preserves token discrimination. Then it runs the combined DFA over the input, keeping track of the last accepting state. This is the **maximal munch algorithm**, but with a single DFA instead of many, and in linear time instead of cubic. The `lexer` module documentation describes this process in detail.

!!! note "Why we did not implement this here"
    Our goal in this section is pedagogical clarity, not performance. The naive implementation above shows exactly what maximal munch means, without the machinery of automata union, determinization, completion, and minimization. Once you understand the naive version, the optimized version is a natural next step. And if you want to see the optimized version in action, you can always reach for `BaseLexer`, or, better yet, read its source code and see how it uses the same building blocks we have been exploring.