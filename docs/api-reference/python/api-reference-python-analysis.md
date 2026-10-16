# Module `analysis`

## Submodule `analysis.context`

> ### `Context`

Base Context class.

 - `__init__()`

#### Properties

 - `errors -> List[SemanticError | RuntimeError]`: copy of semantic errors + runtime errors.

 - `stack_trace -> List[str]`: copy of the stack.

#### Methods

 - `push_trace(trace)`: appends trace to the stack.
    - Args:
        - `trace (str)`

 - `pop_trace()`: removes the last trace.

 - `push_new_scope()`: push a new scope into the context. (not implemented, raises `NotImplementedError`).

 - `pop_scope()`: pops the current scope. (not implemented, raises `NotImplementedError`).

 - `clear_runtime_errors()`: clear all the runtime errors. (not implemented, raises `NotImplementedError`).

 - `get_runtime_errors() -> List[RuntimeError]`: returns all detected runtime errors. (not implemented, raises `NotImplementedError`).

 - `clear_semantic_errors()`: Clear all the semantic errors.

 - `reset()`: reset the context.

 - `clear_errors()`: clear all errors.

 - `add_semantic_error(error)`: adds a semantic error.
    - Args:
        - `error`: instance of a subclass of `SemanticError`.

 - `add_runtime_error(ast, error)`: Adds a new `RuntimeError` from the given ast. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: instance of a subclass of `AST`. 
        - `error`: instance of a subclass of `RuntimeError`.

## Submodule `analysis.lexical`

> ### `LexicalRule`

Abstract class for a lexical validation rule.

 - `__init__(msg: str)`: initializes the instance with the message of the error validation.
    - Args:
        - `msg (str)`

#### Methods

 - `_check(text: str) -> bool`: text validation logic. (not implemented, raises `NotImplementedError`).
    - Args:
        - `text (str)`

 - `check(token: Token) -> LexicalError` — returns a `LexicalError` if `_check` fails, otherwise returns `None`.
    - Args:
        - `token (Token)`

## Submodule `analysis.visitor`

> ### `ASTVisitor`

Base class of a visitor on the ***Visitor Pattern***.

 - `__init__(context_type: type)`
    - Args:
        - `context_type (type)`: the type of the subclass of `Context` for which this visitor is intended. 

#### Methods

 - `_check_context_type(context)`: validates `context`.
    - Args:
        - `context`: the instance to be validated.
    
    - Raises: `TypeError` if `context` is not an instance of `context_type`.

 - `visit(ast, context)`: the logic of visit an AST node. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: (instance of a subclass of `AST`).
        - `context`: instance of `context_type`.

> ### `ASTChildrenSelector`

Base class for AST children selectors.

 - `__init__(context_type: type)`
    - Args:
        - `context_type (type)`.

#### Methods

 - `_check_context_type(context)`:
    - Args:
        `context`: the instance to be validated.
    
    - Raises: `TypeError` if `context` is not an instance of `context_type`.

 - `select_children(ast, context) -> List[AST]`: returns a list of children in the order they will be visited. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: instance of a subclass of `AST`.
        - `context`: instance of `context_type`.

> ### `TraversalStrategy`

Base class for traversal strategies for walking over ASTs.

 - `__init__(context_type: type)`
    - Args:
        - `context_type (type)`
    
    - Raises: `ValueError(f'context_type must be a subclass of {Context}')` if `context_type` is not a subclass of `Context`.

#### Methods

 - `_check_context_type(context)`:
    - Args:
        - `context`: the instance to be validated.
    
    - Raises `TypeError` if `context` is not an instance of `context_type`.
 
 - `init(root)`: initializes the traversal with the root AST.
    - Args:
        - `root`: instance of  subclass of `AST`.

 - `has_next() -> bool`: returns `True` if there is a next AST node to visit. (not implemented, raises `NotImplementedError`).

 - `current(context) -> AST`: returns the current AST node to visit. (not implemented, raises `NotImplementedError`).
    - Args:
        - `context`: instance of `context_type`.

 - `reset()`: resets the traversal. (not implemented, raises `NotImplementedError`).

 - `_get_selector(ast) -> ASTChildrenSelector`: looks up by type; if not found and a default exists, uses it.
    - Args:
        - `ast`: instance of a subclass of `AST`.

 - `add_selector(ast_type:type, selector:ASTChildrenSelector)`: sets the selector for the given type `ast_type`.
    - Args:
        - `ast_type`: subclass of `AST`.
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

    - Raises: `TypeError` if the signature of the 2nd parameter of `selector.select_children` is not annotated or does not match `context_type`.

 - `set_default_selector(selector)`: sets the default selector.
    - Args:
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

    - Raises: analogous to `add_selector`.

> ### `ASTWalker`

Class for an AST walker.

 - `__init__(context, strategy)`
    - Args:
        - `context`: instance of a subclass of `Context`.
        - `strategy`: instance of a subclass of `TraversalStrategy`.

#### Methods

 - `add_visitor(ast_type, visitor)`: sets the visitor for the given type `ast_type`.
    - Args:
        - `ast_type`: subclass of `AST`.
        - `visitor`: instance of a subclass of `ASTVisitor`.
    
    - Raises: `TypeError` if the signature of the 2nd parameter of `visitor.visit` is not annotated or does not match `context_type`.

 - `set_default_visitor(visitor)`: sets the default visitor.
    - Args:
        - `visitor`: instance of a subclass of `ASTVisitor`.
    - Raises: analogous to `add_visitor`.

 - `walk(ast)`: initializes the strategy and iterates until `has_next` is false; for each node it finds the visitor and invokes it. Finally calls `reset` on the strategy.
    - Args:
        - `ast`: instance of a subclass of `AST`.