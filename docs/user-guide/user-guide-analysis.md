# The `analysis` Module

The `analysis` module provides the infrastructure for AST processing, semantic checks, and evaluation. It is built on the **Visitor** and **Strategy** patterns.

## `Context`

The `Context` class is the central state repository. Subclass it to add language-specific data (symbol tables, type environments, etc.).

> ### Attributes and Methods

| **Attribute**/**Method** | **Type** | **Description** |
| :---: | :---: | :---: |
| `push_trace(trace:str)` | `None` | Adds a trace entry |
| `pop_trace()` | `None` | Removes the top trace |
| `push_new_scope()` | `None` | Pushes a new scope. **Must override** |
| `pop_scope()` | `None` | Pops the current scope. **Must override** |
| `add_semantic_error(error:SemanticError)` | `None` | Adds a semantic error |
| `add_runtime_error(ast:AST, error:RuntimeError)` | `None` | Adds a runtime error. **Must override** |
| `clear_runtime_errors()` | `None` | Clears all runtime errors. **Must override** |
| `clear_semantic_errors()` | `None` | Clears all semantic errors |
| `clear_errors()` | `None` | Clears all errors and stack trace. |
| `get_runtime_errors()` | `List[RuntimeError]` | Gets all runtime errors. **Must override** |
| `reset()`	| `None` | Resets the context |
| `errors` | `List[SemanticError | RuntimeError]` | All semantic and runtime errors |
| `stack_trace` | `List[str]` | Current stack trace |

!!! warning
    All methods that must be overridden raise a `NotImplementedError` if called without being overridden.

## Visitor Framework

The framework consists of four collaborating components.

| **Component** | **Key Methods** |
| :---: | :---: |
| **`ASTVisitor`** | `visit(ast:AST, context:Context)`, `_check_context_type(context:Context)` |
| **`ASTChildrenSelector`** | `select_children(ast:AST, context:Context) -> List[AST]` |
| **`TraversalStrategy`** | `init(root:AST)`, `has_next() -> bool`, `current(context:Context) -> AST`, `reset()`,<br> `add_selector(ast_type:type, selector:ASTChildrenSelector)`, `set_default_selector(selector:ASTChildrenSelector)` |
| **`ASTWalker`** | `add_visitor(ast_type:type, visitor:ASTVisitor)`, `set_default_visitor(visitor:ASTVisitor)`, `walk(ast:AST)` |

!!! important
    `add_selector`, `set_default_selector`, `add_visitor`, and `set_default_visitor` use `inspect` to verify that the context type annotation matches the expected type.

> ### Typical Usage

```python
context = MyContext()
strategy = MyStrategy()
strategy.add_selector(MyNode,MyNodeSelector())
strategy.set_default_selector(DefaultSelector())
walker = ASTWalker(context, strategy)
walker.add_visitor(MyNode, MyVisitor())
walker.set_default_visitor(DefaultVisitor())
walker.walk(ast)

if context.errors:
    for error in context.errors:
        print(error)
else:
    print("Analysis OK")
```

!!! note
    The walker applies visitors in the order determined by the traversal strategy. Selectors decide which children are visited.

!!! tip "Best Practices"
    - Always call `_check_context_type` at the start of visit and `select_children`.

    - Keep visitors focused on a single responsibility.

    - Use the default visitor for fallback behavior.

    - Clear the context between independent compilations with `context.reset()`.