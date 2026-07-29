# A Practical Tour for PyLGEN Framework

Welcome to the core of PyLGEN. Up to this point, we have explored the high-level vision, the benchmark results, and the step-by-step construction of a production‑grade interpreter for VecLang. Now, we shift our focus from using PyLGEN to understanding it, from the inside out.

PyLGEN is not a black box; it is a modular, layered framework designed to give you full control over every stage of language processing: from tokenization to parsing, from semantic analysis to execution. Its architecture draws from classic compiler theory (the "Dragon Book" approach) while embracing the Python ecosystem and the performance boost of Cython.

## Why a Modular Tour?

If you have followed the VecLang tutorial, you have already seen PyLGEN in action. But that was a top‑down view: you learned what to write to build an interpreter. Now we are going bottom‑up: we will dissect the building blocks that make that possible. This tour is essential for:

 - **Advanced customization**: When you need to extend PyLGEN beyond the standard patterns.

 - **Performance tuning**: Understanding where optimizations happen and how to exploit them.

 - **Debugging and introspection**: Knowing how the internals work helps you diagnose issues faster.

 - **Contributing or forking**: If you want to add new features to PyLGEN itself.

## The Module Landscape

PyLGEN is organized into seven cohesive submodules, each with a well‑defined responsibility:

| **Submodule** | **Responsability** |
| :---: | :---: |
| **`common`** | Core data types: `Symbol`, `AST`, `Token`, `ASTListView`, `Table`. The foundation. |
| **`automaton`** | Finite automata construction, determinization (NFA → DFA), minimization (Hopcroft). |
| **`grammar`** | Grammar definition (productions, first/follow sets), attributed grammars with reducers. |
| **`regex`** | Regular expression engine: parse patterns, build automata, convert between regex and automata. |
| **`lexer`** | Lexical analysis: regex‑based tokenization, prioritization, validation, and error handling. |
| **`parser`** | LALR(1) parser generator and runtime: conflict detection, error recovery, AST construction. |
| **`analysis`** | Semantic analysis framework: visitors, traversal strategies, contexts, and error hierarchies. |
| **`visual`** | Interactive graph visualization for automata, ASTs, and parse trees (via HTML/pyvis). |

Each module builds upon the ones above it. The `common` module stands alone; every other module depends on it. This layered design ensures that you can use, say, the `automaton` module independently of the `parser`, if all you need is a DFA minimizer.

## Python-First, Cython-Accelerated

One of PyLGEN's distinctive traits is its **dual‑nature API**. Every class and function is designed to work seamlessly in pure Python (for rapid prototyping and debugging) and, when compiled with Cython, to deliver **near‑C performance**. This is not an afterthought; it is baked into the architecture:

 - `.pyx` files contain the implementation, with `cdef` classes and typed attributes.

 - `.pxd` files expose the C‑level interface to other Cython modules.

 - `.pyi` files provide type stubs for Python type checkers and IDEs.

As we go through each module, we will highlight both the Python and Cython faces, and explain when and why you might prefer one over the other.

## How to Read This Tour

Each module section is self‑contained but builds on the previous ones. We recommend reading them in order, but feel free to jump ahead if you are already familiar with a particular area. For each module, we will:

 - `1`: **State its purpose** in the broader framework.

 - `2`: **Present its key classes and functions** with their API.

 - `3`: **Show concrete code examples** (in both Python and Cython).

 - `4`: **Discuss performance considerations** and best practices.

 - `5`: **Illustrate integration** with other modules.

We will keep the tone technical yet accessible, with plenty of inline examples and practical tips. Where appropriate, we will reference the VecLang implementation to ground the theory in something you have already seen.

## Starting with `common` (The Bedrock)

We begin with the common submodule because it is the ***lingua franca*** of PyLGEN. Understanding `Symbol`, `AST`, `Token`, `ASTListView`, and `Table` is a prerequisite for everything else. Once you master these, the rest of the framework will feel like a natural extension.

So, without further ado, let's open `pylgen/common/` and inspect its contents, piece by piece.