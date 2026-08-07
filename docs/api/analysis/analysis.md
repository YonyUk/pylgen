# `pylgen.analysis` Module (The Semantic Framework)

Welcome to the `analysis` module, the gateway between syntax and meaning. If the lexer and parser are concerned with *structure*, this module is concerned with *semantics*. It provides the infrastructure for walking the Abstract Syntax Tree (AST), performing semantic checks, and executing computations. This is where your language truly comes to life.

The analysis module is designed around two powerful design patterns that together enable flexible, extensible AST processing:

 - **The Visitor Pattern**: Separates algorithms from the data structures they operate on. Adding a new operation (e.g., type checking, code generation, evaluation) does not require modifying existing AST node classes.

 - **The Strategy Pattern**: Encapsulates different traversal algorithms (pre‑order, post‑order, in‑order, or custom walks) that can be swapped at runtime without changing the visitors.

Together, these patterns provide a clean, maintainable foundation for all semantic analysis tasks. In the REPL tutorial, you saw them in action: the same `PostOrderStrategy` was used first for semantic error collection (a static analysis pass) and then for evaluation (a dynamic computation pass), simply by swapping the set of visitors.

## Purpose in the Framework

The `analysis` module serves as the **semantic processing** layer of PyLGEN. Its responsibilities are:

 - **Error Management**: A unified hierarchy of errors (`LexicalError`, `SyntaxError`, `SemanticError`, `RuntimeError`) that carry location information and messages.

 - **Context Management**: A base `Context` class that tracks stack traces, error collections, and scopes. Subclass it to add language‑specific state (e.g., symbol tables, variable bindings).

 - **Lexical Rules**: A pluggable validation framework for token‑level checks (e.g., numeric ranges, identifier formats).

 - **AST Visitor Framework**: A complete implementation of the Visitor pattern, with support for:

    - Visitors that operate on specific AST node types.

    - Default visitors for unhandled node types.

    - Children selectors that determine which child nodes to visit.

    - Traversal strategies that control the order of visitation (pre‑order, post‑order, etc.).

    - A walker that orchestrates the traversal and applies visitors.

This module is **generic and extensible**: it does not impose any particular semantic analysis strategy. Instead, it provides the building blocks that you assemble to suit your language's needs.

## Error Hierarchy

A robust error handling system is essential for any language implementation. PyLGEN provides a unified, hierarchical error model that spans all phases of the compilation pipeline, from lexing to runtime execution. Every error carries precise location information (line and column) and a descriptive message, making it easy to report problems directly to the user.

The hierarchy is built around a common base class `Error`, with specialized subclasses for each stage of processing. All errors are collected in the `Context` (semantic and runtime) or in the lexer/parser themselves (lexical and syntax), allowing you to aggregate and report multiple issues in a single pass.

> ### `ErrorType` (Enumeration)

The `ErrorType` enum categorises errors by their origin:

```python
from enum import StrEnum

class ErrorType(StrEnum):
    LEXICAL = 'LEXICAL'
    SYNTAX = 'SYNTAX'
    SEMANTIC = 'SEMANTIC'
    RUNTIME = 'RUNTIME'
```

These values are used internally to tag each error and to format user‑friendly messages.

> ### The `Error` Base Class

`Error` is the abstract base class for all compile‑time errors (lexical, syntax, semantic) and also for runtime errors. It provides the common attributes and formatting logic.

| **Attribute/Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`line`** | `int` | The source line number where the error occurred (1‑indexed). |
| **`column`** | `int` | The source column number where the error occurred (1‑indexed). |
| **`type`** | `ErrorType` | The category of the error. |
| **`message`** | `str` | A human‑readable error message, formatted as `"{type} ERROR at line {line}, column {column}: {msg}"`. |

The constructor accepts the error type, line, column, and a custom message. The `message` property builds a standardised string that is also returned by `__str__` and `__repr__`.

> ### Concrete Error Classes

| **Class** | **Description** |
| :---: | :---: |
| **`LexicalError`** | Raised during lexing when a token does not match any pattern or fails a lexical rule (e.g., malformed number, invalid character). |
| **`SyntaxError`** | Raised during parsing when the token stream does not conform to the grammar (e.g., unexpected token, missing semicolon). |
| **`SemanticError`** | Raised during semantic analysis for violations that cannot be detected by the grammar (e.g., undeclared variable, type mismatch, duplicate definition). |
| **`RuntimeError`** | Raised during evaluation or execution of the AST (e.g., division by zero, invalid operation, out‑of‑bounds access). Unlike the other errors, it includes a stack trace to help debug the execution context. |

All of these classes inherit directly from `Error` and simply forward their arguments to the base class constructor, providing a consistent interface.

> ### Runtime Errors and Stack Traces

`RuntimeError` adds a `stack_trace` property, which is a list of strings representing the call stack at the point where the error occurred. This is particularly useful for debugging interpreted languages, as it allows you to trace back through nested function calls or expression evaluations. The stack trace is maintained by the `Context` (via `push_trace` and `pop_trace`) and can be passed to the error when it is raised.

## Context Management

The `Context` class is the central repository for all state during semantic analysis and evaluation. It is designed to be subclassed to add language‑specific data (like symbol tables, variable values, or type environments).

> ### Base `Context`

#### Methods

| **Method** | **Description** |
| :---: | :---: |
| **`push_trace(trace: str)`** | Adds a trace entry to the stack (used for debugging). |
| **`pop_trace()`** | Removes the top trace entry. |
| **`push_new_scope()`** | Pushes a new lexical scope. Must be overridden. |
| **`pop_scope()`** | Pops the current lexical scope. Must be overridden. |
| **`add_semantic_error(error: SemanticError)`** | Adds a semantic error to the context. |
| **`add_runtime_error(ast: AST, error: RuntimeError)`** | Associates a runtime error with an AST node. Must be overridden. |
| **`clear_semantic_errors()`** | Clears all semantic errors. |
| **`clear_runtime_errors()`** | Clears all runtime errors. Must be overridden. |
| **`clear_errors()`** | Clears both semantic and runtime errors. |
| **`reset()`** | Resets the context (clears stack trace and all errors). |
| **`get_runtime_errors()`** | Returns the list of runtime errors. Must be overridden. |

#### Properties

| **Property** | **Type** | **Description** |
| :---: | :---: | :---: |
| **`errors`** | `list[SemanticError | RuntimeError]` | All errors (semantic + runtime). |
| **`stack_trace`** | `list[str]` | The current stack trace. |

#### Usage in Practice

In the REPL tutorial, the `ArithmeticExpressionContext` subclass extends `Context` with:

 - A variable table (`_variables`).

 - An AST value cache (`_values`).

 - Methods to define, check, and retrieve variables.

 - Methods to store and retrieve computed AST values.

This demonstrates the extensibility of the context: you add only what you need.

## Lexical Rules

The `LexicalRule` class provides a framework for validating tokens beyond what regex patterns can express. For example, you might want to ensure that numbers are within a certain range, or that identifiers do not start with a digit.

> ### `LexicalRule` (Abstract Base Class)

| **Method** | **Description** |
| :---: | :---: |
| **`_check(text: str) -> bool`** | Abstract method that subclasses must implement. Returns `True` if the token is valid. |
| **`check(token: Token) -> LexicalError | None`** | Called by the lexer. If `_check` returns `False`, a `LexicalError` is returned. |

#### Example

=== "Python"

    ```python
    from pylgen.analysis.lexical import LexicalRule

    class NumberLexicalRule(LexicalRule):
        def __init__(self):
            super().__init__('number must be 0 or start with a non-zero digit')

        def _check(self, text: str):
            if '.' in text:
                return str(float(text)) == text
            return str(int(text)) == text
    ```

=== "Cython"

    ```cython
    from pylgen.analysis.lexical cimport LexicalRule

    cdef class NumberLexicalRule(LexicalRule):
        def __init__(self):
            super().__init__('number must be 0 or start with a non-zero digit')
        
        cpdef _check(self, str text):
            if '.' in text:
                return str(float(text)) == text
            return str(int(text)) == text
    ```

The lexer applies all rules associated with a token type; if any rule fails, a lexical error is reported.

## The Visitor Framework

The visitor framework is the heart of the analysis module. It consists of four collaborating components:

 - **Visitors (`ASTVisitor`)**: Implement operations on AST nodes.

 - **Children Selectors (`ASTChildrenSelector`)**: Decide which child nodes to visit.

 - **Traversal Strategies (`TraversalStrategy`)**: Control the order of visitation.

 - **Walker (`ASTWalker`)**: Orchestrates the traversal, applying visitors to nodes.

> ### `ASTVisitor` (Base Class)

Visitors are the workhorses of semantic analysis. Each visitor implements a visit method for a specific AST node type (or a set of types).

| **Method** | **Description** |
| :---: | :---: |
| **`visit(ast: AST, context: Context)`** | Abstract method. Subclasses implement the actual operation. |
| **`_check_context_type(context: Context)`** | Checks that the context is of the expected type. Must be called at the start of visit. |

!!! important
    The visitor is typed to a specific context type via its constructor. This is enforced at runtime by `_check_context_type`, which is a small but crucial safety net.

> ### `ASTChildrenSelector` (Base Class)

Children selectors determine which child nodes a traversal strategy should visit for a given AST node type.

| **Method** | **Description** |
| :---: | :---: |
| **`select_children(ast: AST, context: Context) -> List[AST]`** | Returns the list of child nodes to visit. |

You can have different selectors for different node types, or use a default selector for all nodes. This allows fine‑grained control over the traversal (e.g., skipping certain branches during error collection).

> ### `TraversalStrategy` (Base Class)

Traversal strategies encapsulate the order in which nodes are visited. The `PostOrderStrategy` used in the REPL tutorial visits children before parents, which is essential for evaluators.

| **Method** | **Description** |
| :---: | :---: |
| **`init(root: AST)`**	| Initializes the traversal with the root node. |
| **`has_next() -> bool`** | Returns `True` if there are more nodes to visit. |
| **`current(context: Context) -> AST`** | Returns the next node to visit. |
| **`reset()`** | Resets the traversal to its initial state. |
| **`add_selector(ast_type, selector)`** | Registers a selector for a specific AST node type. |
| **`set_default_selector(selector)`** | Sets a default selector for unregistered node types. |

The strategy maintains internal state (e.g., a stack for post‑order traversal) and uses selectors to determine the children of each node.

> ### `ASTWalker` (Orchestrator)

The walker ties everything together. It holds the context, the traversal strategy, and a collection of visitors.

| **Method** | **Description** |
| :---: | :---: |
| **`add_visitor(ast_type, visitor)`** | Registers a visitor for a specific AST node type. |
| **`set_default_visitor(visitor)`** | Sets a default visitor for unregistered node types. |
| **`walk(ast: AST)`** | Starts the traversal, applying the appropriate visitor to each node. |

When `walk` is called:

 - `1`: The strategy is initialized with the root AST node.

 - `2`: While the strategy has more nodes, the walker:

    - Gets the current node.

    - Looks up the visitor for that node's type (or uses the default visitor).

    - Calls the visitor's `visit` method with the node and context.

 - `3`: The strategy is reset.

!!! important
    `TraversalStrategy.add_selector`, `TraversalStrategy.set_default_selector`, `ASTWalker.add_visitor` and `ASTWalker.set_default_visitor` use `inspect` to check that the second parameter of the `select_children` and `visit` methods is annotated with the expected context type.

## Extensibility and Best Practices

The analysis framework is designed to be extended in several ways:

 - **New Visitor Types**: You can define visitors that perform any operation; type checking, code generation, pretty‑printing, optimization, etc.

 - **New Traversal Strategies**: You can define custom traversal orders (e.g., pre‑order for code generation, in‑order for pretty‑printing).

 - **New Selectors**: You can define selectors that skip certain branches, or that visit nodes in a different order.

 - **New Context Types**: You can add language‑specific state (symbol tables, type environments, etc.) by subclassing Context.

### Best Practices

 - **Always call `_check_context_type`** at the start of your visit or `select_children` methods. This ensures that the context is of the expected type and catches configuration errors early.

 - **Keep visitors focused**: Each visitor should do one thing and do it well. This makes them reusable and testable.

 - **Use the default visitor for fallback behavior**: If a node type doesn't have a dedicated visitor, the default visitor is called. This can be useful for handling generic cases (e.g., evaluating all nodes, or skipping them).

 - **Clear the context** between independent compilations (e.g., in a REPL loop) using `context.reset()`.

## Summary

The `analysis` module is the semantic powerhouse of PyLGEN. It provides a robust, extensible framework for AST processing that is both easy to use and performant. With this module, you can implement sophisticated semantic analyses (e.g., type checking, dataflow analysis, code generation, or interpretation) with clean, maintainable code. The REPL tutorial demonstrated how to use these components to build a complete interpreter; now you have the deeper understanding to extend them for your own languages.

This concludes our tour of PyLGEN's internal architecture. From the foundational common types to the semantic analysis framework, you have seen how each module contributes to a cohesive, efficient, and extensible language processing toolkit. Whether you are building a compiler, an interpreter, a DSL, or a code analysis tool, PyLGEN provides the building blocks you need to succeed.