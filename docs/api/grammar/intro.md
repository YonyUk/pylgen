# pylgen.grammar Module (The Syntactic Blueprint)

Having covered the foundational data types and the automata theory, we now reach the heart of syntactic analysis: the `grammar` module. This module provides the tools to define [**context‑free grammars**](https://en.wikipedia.org/wiki/Context-free_grammar) and [**attributed grammars**](https://en.wikipedia.org/wiki/Attribute_grammar), the essential building blocks for constructing parsers. It handles everything from production rules and symbol management to the computation of `FIRST` and `FOLLOW` sets, which are crucial for parser generation and error recovery.

In this section, we will dissect the `grammar` module's API, explore its core classes, and illustrate how it integrates with the parser generator to turn a language specification into a working parser. We'll also show how attributed grammars allow you to attach semantic actions (reductors) directly to productions, bridging syntax and semantics seamlessly.

## Purpose in the Framework

The `grammar` module serves as the **syntactic specification layer** of PyLGEN. Its responsibilities are:

 - **Define grammar symbols** (terminals and non‑terminals) using the `Symbol` class from [`common`](../common/common.md#symbol-the-atom-of-the-grammar).

 - **Model productions** (rules) with left‑hand side (head) and right‑hand side (sequence of symbols).

 - **Group productions** by head symbol using `ProductionsSet` and its attributed variant.

 - **Compute `FIRST` and `FOLLOW` sets** for any sequence of symbols, which are used by the parser generator to build LALR(1) parsing tables.

 - **Support attributed grammars** by associating a reductor (a callable) with each production; the reductor is invoked during parsing to construct AST nodes.

 - **Provide utilities** to test whether a grammar is left‑ or right‑regular, to augment a grammar with a new start symbol, and to reverse a grammar (useful for certain automata constructions).

The module is designed to be used both from Python (for rapid grammar prototyping) and from Cython (for performance‑critical parsing), leveraging the dual‑nature API described in the introduction.