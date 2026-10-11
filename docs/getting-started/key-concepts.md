# Key Concepts

This glossary is not a theoretical overview. It provides the essential vocabulary you need to read the User Guide and Tutorials without getting lost. If you are already familiar with the terms, feel free to skip this section.

## Glossary

| **Term** | **What it is** | Module |
| :---: | :---: | :---: |
| **`Token`** | Piece of text classified by the lexer (`"42"`, `"+"`) | `common` |
| **`TokenType`** |	Enum ​​defining token categories (`NUMBER`, `PLUS`) | `common` |
| **`Symbol`** | Grammar symbol: terminal or non-terminal | `common` |
| **`Terminal`** | Symbol coming from the lexer | `common` |
| **`Non-terminal`** | Abstract category that expands (`E`, `T`, `F`) | `common` |
| **`Production`** | Rule $A \rightarrow \alpha$, where $A$ is a non-terminal and $\alpha$ is a sequence | `grammar` |
| **`Grammar`**	| Set of productions plus a start symbol | `grammar` |
| **`Attributed grammar`** | Grammar where each production has an associated reducer | `grammar` |
| **`Reducer`**	| Function `ASTListView → AST` that constructs a node upon reduction | `grammar` / `parser` |
| **`AST`**	| Abstract Syntax Tree. Each node is an AST subclass | `common` |
| **`children()`** | Method returning the children of an AST node | `common` |
| **`Context`** | State shared between visitors: variables, results, errors | `analysis` |
| **`ASTVisitor`** | Class capable of processing a specific AST node type | `analysis` |
| **`ASTWalker`** | Traverses the AST and applies the corresponding visitor to each node | `analysis` |
| **`TraversalStrategy`** | Traversal order (pre-order, post-order, custom) | `analysis` |
| **`Lexer`** | Converts text into tokens | `lexer` |
| **`Parser`** | Converts tokens into an AST | `parser` |
| **`Error`** | Base class for `LexicalError`, `SyntaxError`, `SemanticError`, `RuntimeError` | `common` |