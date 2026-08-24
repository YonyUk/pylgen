# `pylgen.visual` Module (Visualizing Grammars, Automata, and ASTs)

The `visual` submodule provides a set of functions to generate interactive HTML visualizations of the core PyLGEN components. Using `networkx` and `pyvis`, you can explore **automata**, **lexers**, **abstract syntax trees**, **parse trees**, and even inspect **LALR parser tables** and **propagation edges** directly in your browser. This module is invaluable for debugging grammars, understanding parser behavior, and teaching language concepts.

All visualizations produce self‑contained HTML files that can be opened in any modern browser. They support optional caching of external resources (like CSS/JS from CDN) to enable offline viewing and faster loading.

## Drawing Automata and Lexers

> ### `draw_automaton(automaton: Automaton, **kwargs) -> None`

Generates an interactive HTML visualization of a finite automaton (`DFA` or `NFA`). The graph displays states (with accept states in green, start state in white with a green border if it is also an accept state, and other states in blue) and transitions labeled with symbols. Epsilon transitions are shown as dashed edges.

 - **Parameters**:

    - **`automaton`**: An instance of `pylgen.automaton.Automaton`.

    - **`**kwargs`**: Common parameters (see above). The default filename is `automaton-{automaton.id}`.

 - **Returns**: `None`, writes an HTML file to disk.

```python
from pylgen.visual import draw_automaton
from my_grammar import my_automaton

draw_automaton(my_automaton, show=True, physics=True)
```

> ### `draw_lexer(lexer: BaseLexer, **kwargs) -> None`

Convenience function that extracts the underlying `DFA` from a lexer and calls `draw_automaton` on it. All parameters are the same.

```python
from pylgen.visual import draw_lexer
from my_lexer import my_lexer

draw_lexer(my_lexer, filename='lexer_dfa', show=True)
```

## Drawing Abstract Syntax Trees

> ### `draw_ast(ast: AST, **kwargs) -> None`

Visualizes an AST. The graph is laid out as a hierarchical tree (top‑down). Each node displays its symbol as the label, and a tooltip shows additional non‑private attributes (e.g., line, column, text for tokens). The AST is recursively traversed via the `children()` method.

 - **Parameters**:

    - **`ast`**: The root AST node (an instance of a subclass of `pylgen.common.types.AST`).

    - **`**kwargs`**: Common parameters. Default filename is `ast`.

 - **Returns**: `None`.

```python
from pylgen.visual import draw_ast

# Assume `root` is the AST returned by the parser
draw_ast(root, show=True, physics=False)
```

## Drawing Parse Trees

> ### `draw_parse_tree_from_parser(parser: Parser, **kwargs) -> None`

Visualizes the **parse tree** (also known as the **concrete syntax tree**) that the parser built during parsing. This tree contains all grammar symbols (terminals and non‑terminals) and is useful for debugging grammar rules.

 - **Parameters**:

    - **`parser`**: A `pylgen.parser.parser.Parser` instance that has already parsed some input (i.e., its `parse_tree` attribute is set).

    - **`**kwargs`**: Common parameters. Default filename is `parse tree`.

 - **Returns**: None.

```python
from pylgen.visual import draw_parse_tree_from_parser

parser.set_draw_parse_tree_flag(True) # this instruct the parser to keep information for the parse tree

parser.parse(lexer.tokens)

draw_parse_tree_from_parser(parser, show=True)
```

!!! warning
    The `parser.set_draw_parse_tree_flag(True)` must be called before the parsing action, otherwise the parse tree is not produced

## Inspecting LR Grammars

> ### `show_propagation_edges_table(g: Grammar, **kwargs) -> None`

Generates an HTML table that shows all **propagation edges** used in LALR lookahead computation. This is a low‑level debugging tool for understanding how lookaheads propagate between LR(0) items. The table lists for each source state and item, the symbol that triggers the edge, the destination state and item, and the associated lookaheads.

 - **Parameters**:

    - **`g`**: A `pylgen.grammar.grammar.Grammar` instance.

    - **`**kwargs`**: Supports `filename`, `show`, and `cache` (no physics or other graph controls).

 - **Returns**: `None`.

```python
from pylgen.visual import show_propagation_edges_table
from my_grammar import grammar

show_propagation_edges_table(grammar, show=True)
```

> ### `lr_inspect_grammar(g: Grammar, type_: str | ParserType = ParserType.LALR1, **kwargs) -> bool`

Performs a full LR analysis on the grammar and generates an HTML report containing the **`ACTION`** and **`GOTO`** tables. The report highlights conflicts (`shift/reduce` or `reduce/reduce`) in red. This function is essential for diagnosing ambiguities.

 - **Parameters**:

    - **`g`**: The grammar to inspect.

    - **`type_`**: The parser type (`ParserType.SLR`,`ParserType.LR1`, and `ParserType.LALR1` are supported; others raise `NotImplementedError`).

    - **`**kwargs`**: Supports `filename`, `show`, `cache`, and a special flag `report`; if `True`, the HTML file is generated, if `False`, no file is written (but the conflict check is still performed).

 - **Returns**: `bool`, `True` if the grammar has conflicts, `False` otherwise.

```python
from pylgen.visual import lr_inspect_grammar
from pylgen.parser.parser_type import ParserType

has_conflicts = lr_inspect_grammar(grammar, ParserType.LALR1, filename='my_grammar_report', show=True, report=True)
if has_conflicts:
    print("Grammar has conflicts. Check the report for details.")
```

> ### Example 1: Classic LALR1 Grammar Analysis (No Conflicts)

The following example demonstrates how to visualize the propagation edges and the `ACTION/GOTO` tables for a classic LALR(1) grammar (the well‑known `S -> L = R | R, L -> * R | id, R -> L` grammar). This grammar is LALR(1) and has no conflicts.

```python
from pylgen.common.types import Symbol
from pylgen.grammar import Grammar
from pylgen.visual import show_propagation_edges_table,lr_inspect_grammar,set_cache_file

set_cache_file('cache.pkl')

S = Symbol('S')
L = Symbol('L')
R = Symbol('R')

mul = Symbol('*',True)
id_ = Symbol('id',True)
eq = Symbol('=',True)

G = Grammar(S,'$')

G[S] += L,eq,R
G[S] += R,

G[L] += mul,R
G[L] += id_,

G[R] += L,

show_propagation_edges_table(G,show=True,cache=True,filename='edges_table')
lr_inspect_grammar(G,'LALR1',show=True,report=True,cache=True,filename='inspect')
```

#### Propagation Edges

<iframe src="../../../images/api/visual/edges_table.html" width="100%" height="1050px" style="border:none;"></iframe>

#### `ACTION` and `GOTO` Tables

<iframe src="../../../images/api/visual/inspect.html" width="100%" height="1200px" style="border:none;"></iframe>

> ### Example 2: LALR(1) Problematic Grammar Analysis

This example shows a grammar that contains ambiguities, resulting in shift/reduce and reduce/reduce conflicts. The generated tables highlight the conflicting cells in red, and the propagation edges table also marks conflicting states.

```python
from pylgen.common.types import Symbol
from pylgen.grammar import Grammar
from pylgen.visual import show_propagation_edges_table,lr_inspect_grammar,set_cache_file

set_cache_file('cache.pkl')

S = Symbol('S')

E = Symbol('E')
A = Symbol('A')
B = Symbol('B')
C = Symbol('C')

mul = Symbol('*',True)
id_ = Symbol('id',True)
plus = Symbol('+',True)

G = Grammar(S,'$')

G[S] += E,
G[S] += A,

G[E] += E,plus,E
G[E] += E,mul,E
G[E] += id_,

G[A] += B,
G[A] += C,

G[B] += id_,
G[C] += id_,

show_propagation_edges_table(G,show=True,cache=True,filename='edges_table_conflict')
lr_inspect_grammar(G,'LALR1',show=True,report=True,cache=True,filename='inspect_conflict')
```

#### Propagation Edges

<iframe src="../../../images/api/visual/edges_table_conflict.html" width="100%" height="1430px" style="border:none;"></iframe>

#### `ACTION` and `GOTO` Tables

<iframe src="../../../images/api/visual/inspect_conflict.html" width="100%" height="1400px" style="border:none;"></iframe>

## Cache Management

> ### `set_cache_file(filename: str) -> None`

Sets the global cache file path used when `cache=True` in any drawing function. The cache stores downloaded external resources (CSS and JavaScript from CDNs) so that visualizations can be opened offline without repeated network requests. The cache is a Python pickle file that maps filenames to their content.

 - **Parameters**:

    - **`filename`**: Path to the cache file (will be created/overwritten).

 - **Raises**:

    - `ValueError` if filename is empty or `None`.

!!! warning
    If you change the cache file path after some visualizations have been generated, the new path will be used for future calls. The cache is only updated when new resources are downloaded; existing entries are reused.

```python
from pylgen.visual import set_cache_file

set_cache_file('my_cache.pkl')
# Now all subsequent calls with cache=True will use this file.
```

## Common Parameters

| **Method** | <span style="white-space: nowrap">**`filename`**</span> | <span style="white-space: nowrap">**`show`**</span> | <span style="white-space: nowrap">**`cache`**</span> | <span style="white-space: nowrap">**`physics`**</span> | <span style="white-space: nowrap">**`select_menu`**</span> | <span style="white-space: nowrap">**`filter_menu`**</span> | <span style="white-space: nowrap">**`nodes`**</span> | <span style="white-space: nowrap">**`edges`**</span> | <span style="white-space: nowrap">**`as_tree`**</span> | <span style="white-space: nowrap">**`report`**</span> |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| <span style="white-space: nowrap">**`draw_automaton`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| <span style="white-space: nowrap">**`draw_lexer`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| <span style="white-space: nowrap">**`draw_ast`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| <span style="white-space: nowrap">**`draw_parse_tree_from_parser`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| <span style="white-space: nowrap">**`show_propagation_edges_table`**</span> | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| <span style="white-space: nowrap">**`lr_inspect_grammar`**</span> | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

| **Parameter** | **Type** | **Default** | **Description** |
| :---: | :---: | :---: | :---: |
| **`filename`** | `str` | Depends on the function | Name of the output HTML file (without extension). |
| **`show`** | `bool` | `False` | If `True`, opens the generated HTML file in your default browser immediately. |
| **`cache`** | `bool` | `False` | If `True`, uses a global cache file (set via `set_cache_file()`) to store downloaded CSS/JS resources for offline reuse. |
| **`physics`** | `bool` | `False` | If `True`, enables physics controls in the interactive graph. |
| <span style="white-space: nowrap">**`select_menu`**</span> | `bool` | `False` | If `True`, shows a selection menu in the visualization. |
| <span style="white-space: nowrap">**`filter_menu`**</span> | `bool` | `False` | If `True`, shows a filter menu. |
| **`nodes`** | `bool` | `False` | If `True`, displays node controls. |
| **`edges`** | `bool` | `False` | If `True`, displays edge controls. |
| **`as_tree`** | `bool` | `False` | If `True`, lays out the graph as a hierarchical tree. |
| **`report`** | `bool` | `False` | If `True`, the HTML report is generated; if `False`, no file is written (but the conflict check is still performed). |


!!! note
    When `cache=True`, you must have previously called `set_cache_file()` to specify the cache file path. Otherwise, a `ValueError` is raised.

## Resource Embedding


The `ResourceEmbedder` class (subclass of `HTMLParser`) intercepts `<link>` and `<script>` tags that reference external HTTP resources. It downloads the content, caches it, and replaces the external reference with an inline `<style>` or `<script>` block. This makes the final HTML completely self‑contained. The embedding is automatically performed when `cache=True`; you do not need to interact with `ResourceEmbedder` directly.

## Best Practices

 - **Enable caching for repeated use**: If you generate many visualizations, set up a cache file to avoid redundant downloads.

 - **Use `show=True` for quick debugging**; otherwise, open the generated HTML files manually.

 - **Disable physics for large graphs to improve performance**; physics can be enabled interactively via the control buttons if needed.

The visual module is a powerful companion for understanding and debugging the entire pipeline, from lexer construction to parser generation and AST evaluation.