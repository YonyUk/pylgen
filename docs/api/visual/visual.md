# `pylgen.visual` Module (Interactive Visualization)

The `visual` module provides a simple yet powerful way to generate interactive, self‑contained HTML visualizations of the core data structures produced by PyLGEN: finite automata, lexers, abstract syntax trees (ASTs), and parse trees. It builds on top of the `pyvis` library (a Python wrapper for the **`vis.js` JavaScript library**) to **create zoomable, navigable graphs** that can be opened in any modern web browser.

This module is designed for debugging, education, and presentation. Being able to see the structure of your automaton, the tree your parser produces, or the shape of your AST is invaluable when diagnosing issues, explaining your language design, or simply appreciating the beauty of your implementation.

## Purpose in the Framework

The `visual` module serves as an **introspection and presentation tool** for PyLGEN. It is entirely optional (you can build and use PyLGEN without ever calling a visualization function) but when you need to visualize, it provides a frictionless experience:

 - **No external dependencies**: The module uses `pyvis` and `networkx` (both installed with PyLGEN) and embeds all required JavaScript and CSS resources directly into the output HTML when caching is enabled.

 - **Standalone output**: The generated HTML files are fully self‑contained (with caching) and can be shared, embedded in documentation, or opened offline.

 - **Consistent API**: All drawing functions accept a common set of keyword arguments (physics controls, filters, show/hide, caching, output filename).

The module extracts structural information from PyLGEN objects (automata, ASTs, parse trees) and converts them into directed graphs that are rendered using vis.js's interactive network visualization.

## Core Functions

> ### `draw_automaton(automaton: Automaton, **kwargs) -> None`

Generates an interactive HTML visualization of a finite automaton.

 - **Args**:

    - `automaton`: An instance of `Automaton` (or any subclass like `DFA` or `NFA`).

    - `**kwargs`: Optional parameters (see below).

#### What is displayed:

 - States are shown as nodes. The initial state are filled in white (has a green border if is accepting); accepting states are filled in green.

 - Transitions are edges labelled with the input symbol. ε‑transitions are drawn as dashed lines.

 - Each node has a tooltip showing its internal ID.

> ### `draw_lexer(lexer: BaseLexer, **kwargs) -> None`

Calls `draw_automaton` on the lexer's internal DFA. This visualises the combined automaton used for tokenization.

 - **Args**: Same as `draw_automaton`, but the `automaton` parameter is replaced by a `BaseLexer` instance.

> ### `draw_ast(ast: AST, **kwargs) -> None`

Generates an interactive HTML visualization of an Abstract Syntax Tree.

 - **Args**:

    - `ast`: The root AST node.

    - `**kwargs`: Optional parameters (see below).

#### What is displayed:

 - Each AST node is shown as a circle labelled with the symbol of that node.

 - Nodes are arranged hierarchically (top‑down) using a directed hierarchical layout.

 - Tooltips display non‑private attributes of the AST node (excluding attributes starting with `_` and the `symbol` attribute) that are JSON‑serializable. This allows you to see e.g., `line`, `column`, or custom data.

> ### `draw_parse_tree_from_parser(parser: Parser, **kwargs) -> None`

Generates an interactive HTML visualization of the full parse tree (concrete syntax tree) recorded by the parser.

 - **Args**:

    - `parser`: A `Parser` instance that has successfully parsed input with `set_draw_parse_tree_flag(True)` called beforehand.

    - `**kwargs`: Optional parameters (see below).

#### What is displayed:

 - The parse tree includes every terminal and non‑terminal symbol from the derivation, showing precisely how the grammar consumed the input.

 - The tree is arranged hierarchically; each node shows the grammar symbol.

> ### `set_cache_file(filename: str) -> None`

Sets the file path to be used as a cache for downloaded JavaScript/CSS resources (vis.js and its dependencies). When caching is enabled (via `cache=True` in any drawing function), the module downloads the external resources once and stores them in this file, avoiding repeated downloads and enabling offline use.

 - **Args**: 
    - `filename`: the path to the cache file (e.g., `'vis_cache.pkl'`).

!!! warning
    If the file already exists, it may be overwritten.

## Common Keyword Arguments

All drawing functions accept the following optional arguments:

| **Parameter** | **Type** | **Default** | **Description** |
| :---: | :---: | :---: | :---: |
| **`filename`** | `str` | Auto‑generated (e.g., 'automaton-id', 'ast', 'parse tree')	| The base name (without extension) for the output HTML file. |
| **`show`** | `bool` | `False` | If `True`, the HTML file is opened in your default web browser after generation. |
| **`cache`** | `bool` | `False` | If `True`, external resources (CSS/JS) are downloaded and embedded into the HTML using a local cache file. This makes the output self‑contained and usable offline. Requires `set_cache_file` to be called first. |
| **`physics`** | `bool` | `False` | If `True`, enables the physics controls in the vis.js network. Disabled by default. |
| **`select_menu`** | `bool` | `False` | If `True`, adds a selection menu in the vis.js interface. |
| **`filter_menu`** | `bool` | `False` | If `True`, adds a filter menu. |
| **`nodes`** | `bool` | `False` | If `True`, shows node controls in the vis.js interface. |
| **`edges`** | `bool` | `False` | If `True`, shows edge controls in the vis.js interface. |
| **`as_tree`** | `bool` | `False` | (Only for `draw_automaton`) | If `True`, the graph is laid out as a tree using vis.js's hierarchical layout. |

## The Resource Embedding Mechanism

To produce self‑contained HTML files, the `visual` module includes a custom `ResourceEmbedder` class (subclass of `HTMLParser`) that:

 - `1`: Parses the HTML generated by `pyvis`.

 - `2`: Detects `<link>` tags referencing external stylesheets and `<script>` tags with `src` pointing to external JavaScript files.

 - `3`: Downloads the content of those resources (using `urllib.request`).

 - `4`: Replaces the external references with inline `<style>` and `<script>` blocks containing the downloaded content.

This process is **cached** when `cache=True`. The cache file is a pickle‑serialized dictionary mapping resource filenames to their content. If the cache file already exists, it is loaded and used; otherwise, it is created after downloading.

!!! important
    To use the cache feature, you must call `set_cache_file()` with a valid file path before calling any drawing function with `cache=True`. If `cache=True` is used without a cache file set, a `ValueError` is raised.

## Performance and Limitations

 - **AST Graph Construction**: The internal `_ast_to_graph` function performs a depth‑first traversal of the AST, collecting all nodes and their serializable attributes. This is efficient for typical AST sizes (up to thousands of nodes). For extremely large ASTs (tens of thousands), the generated HTML may be large and slow to render.

 - **Cache File Size**: The cache file stores the full content of vis.js and its CSS, which is around several hundred kilobytes. It is downloaded only once (unless the cache file is deleted).

 - **Browser Compatibility**: The generated HTML uses modern JavaScript and CSS; it works in all major browsers (Chrome, Firefox, Edge, Safari).

 - **Offline Use**: With `cache=True` and a cache file, the HTML works fully offline.

## Summary

The `visual` module is a convenient, self‑contained visualization tool that transforms PyLGEN's core data structures into interactive HTML graphs. It is built with the same philosophy as the rest of PyLGEN: **practical, performant, and easy to use**. Whether you are debugging a tricky grammar, presenting your language design, or simply admiring the beauty of an automaton, this module provides a one‑stop solution. With the visual module, PyLGEN offers a complete development experience, from language definition to interactive visualization, all within a single, cohesive framework.