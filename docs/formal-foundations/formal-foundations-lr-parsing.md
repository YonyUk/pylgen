# LR Parsing

LR parsing is a **bottom-up, shift-reduce** parsing technique that reads input from left to right (L) and produces a rightmost derivation in reverse (R). It is one of the most powerful and general parsing methods, capable of handling virtually all context-free grammars that are not ambiguous.

## The LR Parser

An LR parser consists of:

 - **`1` A parsing table** with two parts:
    - **`ACTION`**: Given the current parser state and the current lookahead token, tells the parser whether to *shift* (consume the token and push a new state), reduce (apply a production), or accept.
    - **`GOTO`**: Given a state and a non‑terminal, tells the parser which state to transition to after a reduction.
 - **`2` A stack** that holds states, grammar symbols, and AST nodes (or parse tree nodes).
 - **`3` A driver loop** that repeatedly consults the **`ACTION`** table, performs the indicated operation, and updates the stack.

The LR parsing algorithm is elegant and efficient: it runs in linear time, requires no backtracking, and can detect syntax errors as soon as they occur.

## LR Items and States

The construction of an LR parser begins with **LR(0) items**, which represent a production with a dot somewhere in its right‑hand side. For example, the production $E \rightarrow E + T$ gives rise to the items:

 - $E \rightarrow \cdot E + T$ (dot at the begining).
 - $E \rightarrow E \cdot + T$ (dot before the `+`).
 - $E \rightarrow E + \cdot T$ (dot before `T`).
 - $E \rightarrow E + T \cdot$ (dot at the end, indicating a completed production).

An **LR(0) state** is a set of LR(0) items that are reachable from the start state via a sequence of symbols. The collection of all such states forms the **canonical LR(0) automaton**. This automaton is the foundation for constructing the parsing tables.

## The Three Levels of LR Parsing

For more powerful parsers, additional lookahead information is added to the items.

> ### SLR (Simple LR)

**SLR (Simple LR)** parsers use the `FOLLOW` sets of the grammar to decide when to reduce. During table construction, each LR(0) state with a completed item (dot at the end) generates reduce actions for all terminals in the `FOLLOW` set of the production's head. This is a simple and efficient approach, but it is not powerful enough for many practical grammars.

> ### LR(1)

**LR(1)** items extend LR(0) items with a **single lookahead terminal**. An LR(1) item is written as [$A \rightarrow \alpha \cdot \beta,a$] where $a$ is a terminal that must follow the production. The closure and goto operations are augmented to propagate these lookaheads precisely. LR(1) parsers are the most powerful (they can handle any deterministic context‑free language), but they can generate a very large number of states (often hundreds or thousands).

> ### LALR(1) (Look-Ahead LR)

**LALR(1)** items also carry lookahead information, but they use **set of lookaheads** (instead of a single one) and merge LR(0) states that have identical kernels (the items without lookaheads). This reduces the number of states to that of LR(0), while still retaining much of the power of LR(1). The lookaheads are computed using a propagation algorithm that starts with the lookahead `$` (end‑of‑file) for the initial item and propagates lookaheads through transitions in the LR(0) automaton.

> ### Comparison

| **Parser** | **Lookahead** | **States** | **Power** | **Typical Use** |
| :---: | :---: | :---: | :---: | :---: |
| **SLR** | **`FOLLOW` sets** | **LR(0)** | Weakest	| Simple grammars |
| **LR(1)** | One terminal per item | **Many** | Strongest | Complex grammars where state count is acceptable |
| **LALR(1)** | Set of terminals per item | **LR(0)** | Intermediate | Recommended default |

## Closure and Goto

The two fundamental operations for building the LR automaton are **closure** and **goto**.

 - **Closure**: Given a set of items, if an item has the dot before a non-terminal $A$, add all productions of $A$ with the dot at the beginning. Repeat until no new items are added

 - **Goto**: Given a set of items and a symbol $X$, move the dot over $X$ for all items that have $X$ right after the dot, then take the **closure** of the result.

The canonical collection of LR states is built by starting with the closure of the initial item $S^{'} \rightarrow \cdot S$, then repeatedly applying goto on each symbol after a dot, adding new states as they are discovered. The process terminates because the set of possible items is finite.

## Conflicts

LR parsers can encounter two kinds of conflicts:

 - **Shift-reduce conflict**: the parser cannot decide whether to shift the next token or reduce by a completed production.

 - **Reduce-reduce conflict**: the parser cannot decide which of two completed productions to reduce by.

Conflicts are a property of the grammar, not of the parser. They can often be resolved by:

 - Rewriting the grammar to remove ambiguity.

 - Adding precedence and associativity declarations.

 - Switching to a more powerful parser type (SLR → LALR(1) → LR(1)).

PyLGEN detects conflicts during table construction and raises specific exceptions that include the state, symbol, and conflicting actions, so you can diagnose and fix the grammar.