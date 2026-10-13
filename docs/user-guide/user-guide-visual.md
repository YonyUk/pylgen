# The `visual` Module

The `visual` module generates interactive HTML visualizations using `networkx` and `pyvis`. It supports **automata**, **lexers**, **ASTs**, **parse trees**, **parsing tables**, and **propagation edges**. Outputs are **self‑contained HTML files** with **optional caching for offline use**.

## Public Functions

| **Function** | **Purpose** |
| :---: | :---: |
| **`draw_automaton`** | Visualize a `DFA` or `NFA` |
| **`draw_lexer`** | Visualize the `DFA` underlying a lexer |
| **`draw_ast`** | Visualize an AST |
| **`draw_parse_tree`** | Visualize a parse tree |
| **`show_propagation_edges_table`** | Show LALR propagation edges |
| **`lr_inspect_grammar`** | Inspect `ACTION`/`GOTO` tables and conflicts |
| **`set_cache_file`** | Set the cache file for external resources |

## Drawing Automata and Lexers

> ### `draw_automaton(automaton, **kwargs)`

Generates an interactive HTML visualization of a finite automaton. Accept states are green, the start state is white with a green border if it is also accepting, and other states are blue. Epsilon transitions appear as dashed edges.

| **Parameter** | **Description** |
| :---: | :---: |
| **`automaton`** | An instance of `pylgen.automaton.Automaton` |
| **`**kwargs`** | Common parameters. Default filename: `automaton-{automaton.id}` |

#### Example

```python
from pylgen.visual import draw_automaton

draw_automaton(my_automaton, show=True, physics=True)
```

> ### draw_lexer(lexer, **kwargs)

Convenience function that extracts the `DFA` from a lexer and calls `draw_automaton` on it.

#### Example

```python
from pylgen.visual import draw_lexer

draw_lexer(my_lexer, filename='lexer_dfa', show=True)
```

## Drawing Abstract Syntax Trees and Parse Trees

> ### `draw_ast(ast, **kwargs)`

Visualizes an `AST` as a hierarchical tree. Each node displays its symbol; a tooltip shows non‑private attributes. The tree is traversed recursively via `children()`.

| **Parameter** | **Description** |
| :---: | :---: |
| **`ast`** | Root AST node, an instance of `pylgen.common.types.AST` |
| **`**kwargs`** | Common parameters. Default filename: `ast` |

#### Example

```python
from pylgen.visual import draw_ast

draw_ast(root, show=True)
```

> ### `draw_parse_tree(tree, **kwargs)`

Visualizes the parse tree (concrete syntax tree) built by the parser. It contains all grammar symbols and is useful for debugging grammar rules.

| **Parameter** | **Description** |
| :---: | :---: |
| **`tree`** | An instance of `pylgen.parser.parser.ParseTreeNode`, normally taken from a parser that already has parsed something correctly with its `_draw_parse_tree` flag setted to `True`, via `parser.parse_tree` attribute | 
| **`**kwargs`** | Common parameters. Default filename: `parse tree` |

#### Example

```python
from pylgen.visual import draw_parse_tree

parser.set_draw_parse_tree_flag(True)
parser.parse(lexer.tokens)
draw_parse_tree(parser.parse_tree, show=True)
```

!!! warning
    `parser.set_draw_parse_tree_flag(True)` must be called before parsing; otherwise no parse tree is produced.

## Inspecting LR Grammars

> ### `show_propagation_edges_table(g, **kwargs)`

Generates an HTML table of all propagation edges used in LALR lookahead computation. Lists source state/item, trigger symbol, destination state/item, and lookaheads.

| **Parameter** | **Description** |
| :---: | :---: |
| **`g`** | A instance of `pylgen.grammar.grammar.Grammar` |
| **`**kwargs`** | `filename`, `show`, `cache` |

#### Example

```python
from pylgen.visual import show_propagation_edges_table

show_propagation_edges_table(grammar, show=True)
```

> ### `lr_inspect_grammar(g, type_=ParserType.LALR1, **kwargs) -> bool`

Performs full LR analysis and generates an HTML report with `ACTION` and `GOTO` tables. Conflicts are highlighted in red. Returns `True` if conflicts exist.

| **Parameter** | **Description** |
| :---: | :---: |
| **`g`** | The instance of `pylgen.grammar.grammar.Grammar` to inspect |
| **`type_`** | `ParserType.SLR`, `ParserType.LR1`, or `ParserType.LALR1`. Others raise `NotImplementedError` |
| **`**kwargs`** | `filename`, `show`, `cache`, `report`. If `report=False`, no file is written but conflict check still runs |

#### Example

```python
from pylgen.visual import lr_inspect_grammar
from pylgen.parser.parser_type import ParserType

has_conflicts = lr_inspect_grammar(
    grammar, ParserType.LALR1,
    filename='my_grammar_report', show=True, report=True
)
if has_conflicts:
    print("Grammar has conflicts. Check the report for details.")
```

> ### Examples

#### 1: Classic LALR1 Grammar Analysis (No Conflicts)

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

##### Propagation Edges

<iframe src="../../assets/html/visual/edges_table.html" width="100%" height="1050px" style="border:none;"></iframe>

##### `ACTION` and `GOTO` Tables

<iframe src="../../assets/html/visual/inspect.html" width="100%" height="1200px" style="border:none;"></iframe>

#### 2: LALR(1) Problematic Grammar Analysis

This example shows a grammar that contains ambiguities, resulting in shift/reduce and reduce/reduce conflicts. The generated tables highlight the conflicting cells in red.

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

##### Propagation Edges

<iframe src="../../assets/html/visual/edges_table_conflict.html" width="100%" height="1430px" style="border:none;"></iframe>

##### `ACTION` and `GOTO` Tables

<iframe src="../../assets/html/visual/inspect_conflict.html" width="100%" height="1400px" style="border:none;"></iframe>

## Cache Management

> ### `set_cache_file(filename: str) -> None`

Sets the global cache file path used when `cache=True` in any drawing function. The cache stores downloaded external resources (CSS and JavaScript from CDNs) so that visualizations can be opened offline without repeated network requests. The cache is a Python pickle file that maps filenames to their content.

| **Parameter** | **Description** |
| :---: | :---: |
| **`filename`** | Path to the cache file |

!!! warning
    Raises `ValueError` if empty or `None`. The cache path applies to future calls. Existing entries are reused; only new resources are downloaded.

#### Example

```python
from pylgen.visual import set_cache_file

set_cache_file('my_cache.pkl')
```

## Common Parameters

> ### Methods x Parameters Table

| **Method** | <span style="white-space: nowrap">**`filename`**</span> | <span style="white-space: nowrap">**`show`**</span> | <span style="white-space: nowrap">**`cache`**</span> | <span style="white-space: nowrap">**`physics`**</span> | <span style="white-space: nowrap">**`select_menu`**</span> | <span style="white-space: nowrap">**`filter_menu`**</span> | <span style="white-space: nowrap">**`nodes`**</span> | <span style="white-space: nowrap">**`edges`**</span> | <span style="white-space: nowrap">**`as_tree`**</span> | <span style="white-space: nowrap">**`report`**</span> |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| <span style="white-space: nowrap">**`draw_automaton`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| <span style="white-space: nowrap">**`draw_lexer`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| <span style="white-space: nowrap">**`draw_ast`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| <span style="white-space: nowrap">**`draw_parse_tree_from_parser`**</span> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| <span style="white-space: nowrap">**`show_propagation_edges_table`**</span> | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| <span style="white-space: nowrap">**`lr_inspect_grammar`**</span> | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

> ### Parameters Details

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

## Best Practices

 - Enable caching for repeated use.

 - Use show=True for quick debugging; otherwise open the HTML files manually.

 - Disable physics for large graphs; enable it interactively if needed.