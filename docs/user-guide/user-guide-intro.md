# User Guide

This section documents the PyLGEN public API. It is intended for users who have already installed the library and wish to use it; whether to build a language, query a class, or understand how the modules connect.

## How to read this section

- If this is your first time here, start with the [First Steps](../getting-started/installation.md). This guide assumes you have already built something.
- If you are looking for a specific module, go directly to its page. Each page states its intended audience at the beginning.

## Module Map

| Module | Responsibility | Page |
| :--- | :--- | :--- |
| `common` | Base types: `Symbol`, `AST`, `Token`, `Error`, `ASTListView`. | [common](user-guide-common.md) |
| `grammar` | Productions, attributed grammars, reducers. | [Grammars](user-guide-grammar.md) |
| `lexer` | Tokenization using regex and lexical rules. | [Lexer](user-guide-lexer.md) |
| `parser` | Construction and execution of the LALR(1) parser. | [Parser](user-guide-parser.md) |
| `analysis` | Visitors, walkers, context, semantic analysis. | [Semantic Analysis](user-guide-analysis.md) |
| `regex` | Regular expression engine. | ​​[Regular Expressions](user-guide-regex.md) |
| `automaton` | DFA, NFA, and language operations. | [Automata](user-guide-automaton.md) |
| `visual` | Interactive HTML visualization. | [Visualization](user-guide-visual.md) |