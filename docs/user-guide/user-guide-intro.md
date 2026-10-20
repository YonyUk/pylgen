# User Guide

This section explains how to use PyLGEN's modules. For the full signature and attribute listing of each class, see the [API Reference](../api-reference/table_of_contents.md).

## How to read this section

- If this is your first time here, start with the [First Steps](../getting-started/installation.md). This guide assumes you have already built something.
- If you are coming from the [Quick Start](../getting-started/quick-start.md) guide, read `Lexer` → `Grammar` → `Parser` → `Analysis`. The `Common` module serves as a cross-reference for the types that appear throughout all those modules; consult it whenever you need to check an exact signature. `Regex` and `Automaton` are independent modules, useful if you want to build automata or work directly with regular expressions. `Visual` is intended for debugging and presentation purposes.

## Module Map

| Module | Responsibility | Page |
| :--- | :--- | :--- |
| `lexer` | Tokenization using regex and lexical rules. | [Lexer](user-guide-lexer.md) |
| `grammar` | Productions, attributed grammars, reducers. | [Grammars](user-guide-grammar.md) |
| `parser` | Construction and execution of the LALR(1) parser. | [Parser](user-guide-parser.md) |
| `analysis` | Visitors, walkers, context, semantic analysis. | [Semantic Analysis](user-guide-analysis.md) |
| `common` | Base types: `Symbol`, `AST`, `Token`, `Error`, `ASTListView`. | [common](user-guide-common.md) |
| `regex` | Regular expression engine. | ​​[Regular Expressions](user-guide-regex.md) |
| `automaton` | DFA, NFA, and language operations. | [Automata](user-guide-automaton.md) |
| `visual` | Interactive HTML visualization. | [Visualization](user-guide-visual.md) |