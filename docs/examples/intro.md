# Example Projects

You've followed the compiler pipeline from end to end: lexer, parser, AST, semantic analysis, and execution. You've seen how PyLGEN's pieces fit together. Now it's time to see what happens when those pieces are applied to **real problems**.

In this section, we'll walk through two complete projects, each one designed to stress a different aspect of the framework. They're not toy snippets, they're self‑contained interpreters with their own grammars, ASTs, error handling, and user interfaces.

## What you'll find here

> ### [`idented_dsl`](idented_dsl/idented_dsl.md)

An interpreter for an **indentation‑sensitive configuration language**. Think of it as INI with true nesting: sections, subsections, atoms, and indentation that actually means something. This example shows how PyLGEN handles significant whitespace without forcing the grammar to count spaces, and how a small DSL can be built in just a few hundred lines of declarative code.

> ### [`mini-python`](mini-python/mini-python.md)

A complete interpreter with a **GUI included**, capable of handling a **subset of the Python language**. This example pushes the framework further: more grammar rules, more AST nodes, and a richer evaluation model. It's the natural next step after the [arithmetic REPL](../section-1/example-1-first-approach.md).

## How to read these examples

Each example is self‑contained, but they share the same philosophy:

 - **Declarative first**: grammar rules, token definitions, and reducers describe *what* the language is, not *how* to process it.

 - **Layered responsibility**: the lexer classifies, the parser structures, the reducers build, and the visitors evaluate. Each layer trusts the one before it.

 - **Right tool for the scale**: not every project needs visitors, selectors, or semantic analysis. These examples show when to use them, and when a simple recursive function is enough.

!!! note "Sources"
    All example projects are available on the [github repository](https://github.com/YonyUk/pylgen/tree/master/examples)

Let's dive in and see PyLGEN in action.