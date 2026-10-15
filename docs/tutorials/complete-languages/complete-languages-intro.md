# Complete Languages Tutorials

[**Foundations**](../foundations/tutorials-foundations-intro.md) subsection teaches you how the pipeline works. **Complete Languages** subsection teaches you how to build one.

In this subsection, you'll write four working interpreters, each one a complete language with its own lexer, grammar, AST, and evaluator. You'll start with the smallest possible pipeline (a calculator that evaluates arithmetic expressions) and work your way up to a subset of Python with functions, loops, and a graphical interface. Along the way, you'll use every part of PyLGEN's high-level API: `Lexer`, `AttributedGrammar`, `ParserBuilder`, `ASTVisitor`, `ASTWalker`, `TraversalStrategy`, and more.

This is the path for anyone who wants to build a language, whether for production, for research, or just for the joy of it. Each tutorial is self-contained, but they're designed to be read in order. Each one adds a new feature to the same skeleton, and by the end you'll have seen the full range of what PyLGEN can do.

## What's in this subsection

| **Tutorial** | **What you'll build** | **What you'll learn** |
| :---: | :---: | :---: |
| **Arithmetic Interpreter** | A REPL that evaluates arithmetic expressions | The full pipeline: lexer, grammar, AST, reducers, semantic checks, evaluation |
| **Config DSL** | A parser for an indentation-sensitive configuration language that emits JSON | `IndentedLexer`, indentation tokens, grammar design, code generation |
| **Python Subset** | A subset of Python with functions, loops, and a Tkinter GUI | Control flow, signals, scopes, custom traversal strategies, GUIs |
| **VecLang** | A vector language compiled to native code with Cython | Cython compilation, NumPy integration, performance-first design |

Each tutorial picks a different point in the design space. The Arithmetic Interpreter is minimal and clear; the Config DSL shows how to handle indentation; the Python Subset shows how to scale to a real language; VecLang shows how to make it fast. Together, they cover the decisions you'll face when you build your own language.

!!! tip "Start small, then grow"
    Don't try to build your dream language in one sitting. Start with the Arithmetic Interpreter. Get it working. Then add a feature, and then another. The tutorials show this incremental approach, and it's the same one you should use for your own language.