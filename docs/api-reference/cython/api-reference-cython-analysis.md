# Module `analysis`

## Submodule `analysis.context`

> ### `Context`

Base Context class.

 - `__init__()`

#### Properties

 - `cdef list[SemanticError] _errors`

 - `cdef list[str] _stack`

#### Methods

 - `cpdef void push_trace(str trace)`: appends trace to the stack.
    - Args:
        - `trace (str)`

 - `cpdef void pop_trace()`: removes the last trace.

 - `cpdef void push_new_scope()`: push a new scope into the context. (not implemented, raises `NotImplementedError`).

 - `cpdef void pop_scope()`: pops the current scope. (not implemented, raises `NotImplementedError`).

 - `cpdef void clear_runtime_errors()`: clear all the runtime errors. (not implemented, raises `NotImplementedError`).

 - `cpdef list[RuntimeError] get_runtime_errors()`: returns all detected runtime errors. (not implemented, raises `NotImplementedError`).

 - `cpdef void clear_semantic_errors()`: Clear all the semantic errors.

 - `cpdef void reset()`: reset the context.

 - `cpdef void clear_errors()`: clear all errors.

 - `cpdef void add_semantic_error(error)`: adds a semantic error.
    - Args:
        - `error`: instance of a subclass of `SemanticError`.

 - `cpdef void add_runtime_error(ast, error)`: Adds a new `RuntimeError` from the given ast. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: instance of a subclass of `AST`. 
        - `error`: instance of a subclass of `RuntimeError`.

## Submodule `analysis.lexical`

> ### `LexicalRule`

Abstract class for a lexical validation rule.

 - `__init__(str msg)`: initializes the instance with the message of the error validation.
    - Args:
        - `msg (str)`

#### Properties

 - `cdef str _msg`: the message of the error validation.

#### Methods

 - `cpdef bool _check(str text)`: text validation logic. (not implemented, raises `NotImplementedError`).
    - Args:
        - `text (str)`

 - `cpdef LexicalError check(Token token)` — returns a `LexicalError` if `_check` fails, otherwise returns `None`.
    - Args:
        - `token (Token)`

## Submodule `analysis.visitor`

> ### `ASTVisitor`

Base class of a visitor on the ***Visitor Pattern***.

 - `__init__(type context_type)`
    - Args:
        - `context_type (type)`: the type of the subclass of `Context` for which this visitor is intended. 

#### Properties

 - `cdef type _context_type`

#### Methods

 - `cpdef void _check_context_type(context)`: validates `context`.
    - Args:
        - `context`: the instance to be validated.
    
    - Raises: `TypeError` if `context` is not an instance of `_context_type`.

 - `cpdef void visit(ast, context)`: the logic of visit an AST node. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: (instance of a subclass of `AST`).
        - `context`: instance of `_context_type`.

> ### `ASTChildrenSelector`

Base class for AST children selectors.

 - `__init__(type context_type)`
    - Args:
        - `context_type (type)`: the type of the subclass of `Context` for which this visitor is intended.

#### Properties

 - `cdef type _context_type`

#### Methods

 - `cpdef void _check_context_type(context)`:
    - Args:
        `context`: the instance to be validated.
    
    - Raises: `TypeError` if `context` is not an instance of `_context_type`.

 - `cpdef list[AST] select_children(ast, context)`: returns a list of children in the order they will be visited. (not implemented, raises `NotImplementedError`).
    - Args:
        - `ast`: instance of a subclass of `AST`.
        - `context`: instance of `_context_type`.

> ### `TraversalStrategy`

Base class for traversal strategies for walking over ASTs.

 - `__init__(type context_type)`
    - Args:
        - `context_type (type)`: the type of the subclass of `Context` for which this visitor is intended.
    
    - Raises: `ValueError(f'context_type must be a subclass of {Context}')` if `context_type` is not a subclass of `Context`.

#### Properties

 - `cdef type _context_type`
 - `cdef AST _root`
 - `cdef dict[type,ASTChildrenSelector] _selectors`
 - `cdef ASTChildrenSelector _default_selector`

#### Methods

 - `cpdef void _check_context_type(context)`:
    - Args:
        - `context`: the instance to be validated.
    
    - Raises `TypeError` if `context` is not an instance of `_context_type`.
 
 - `cpdef void init(root)`: initializes the traversal with the root AST.
    - Args:
        - `root`: instance of  subclass of `AST`.

 - `cpdef bint has_next()`: returns `True` if there is a next AST node to visit. (not implemented, raises `NotImplementedError`).

 - `cpdef AST current(context)`: returns the current AST node to visit. (not implemented, raises `NotImplementedError`).
    - Args:
        - `context`: instance of `_context_type`.

 - `cpdef void reset()`: resets the traversal. (not implemented, raises `NotImplementedError`).

 - `cpdef ASTChildrenSelector _get_selector(ast)`: looks up by type; if not found and a default exists, uses it.
    - Args:
        - `ast`: instance of a subclass of `AST`.

 - `cpdef void add_selector(ast_type:type, selector:ASTChildrenSelector)`: sets the selector for the given type `ast_type`.
    - Args:
        - `ast_type`: subclass of `AST`.
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

    - Raises: `TypeError` if the signature of the 2nd parameter of `selector.select_children` is not annotated or does not match `_context_type`.

 - `cpdef void set_default_selector(selector)`: sets the default selector.
    - Args:
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

    - Raises: analogous to `add_selector`.

 - `cdef void add_selector_without_signature_checking(ast_type,selector)`
    - Args:
        - `ast_type`: subclass of `AST`.
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

 - `cdef void set_default_selector_without_signature_checking(selector)`
    - Args:
        - `selector`: instance of a subclass of `ASTChildrenSelector`.

> ### `ASTWalker`

Class for an AST walker.

 - `__init__(context, strategy)`
    - Args:
        - `context`: instance of a subclass of `Context`.
        - `strategy`: instance of a subclass of `TraversalStrategy`.

#### Properties

 - `cdef Context _context`
 - `cdef dict[type,ASTVisitor] _visitors`
 - `cdef TraversalStrategy _strategy`
 - `cdef ASTVisitor _default_visitor`

#### Methods

 - `cpdef void add_visitor(ast_type, visitor)`: sets the visitor for the given type `ast_type`.
    - Args:
        - `ast_type`: subclass of `AST`.
        - `visitor`: instance of a subclass of `ASTVisitor`.
    
    - Raises: `TypeError` if the signature of the 2nd parameter of `visitor.visit` is not annotated or does not match `_context_type`.

 - `cpdef void set_default_visitor(visitor)`: sets the default visitor.
    - Args:
        - `visitor`: instance of a subclass of `ASTVisitor`.
    - Raises: analogous to `add_visitor`.

 - `cpdef void walk(ast)`: initializes the strategy and iterates until `has_next` is false; for each node it finds the visitor and invokes it. Finally calls `reset` on the strategy.
    - Args:
        - `ast`: instance of a subclass of `AST`.

 - `cdef void add_visitor_without_signature_checking(ast_type,visitor)`
    - Args:
        - `ast_type`: subclass of `AST`.
        - `visitor`: instance of a subclass of `ASTVisitor`.

 - `cdef void set_default_visitor_without_signature_checking(visitor)`
    - Args:
        - `visitor`: instance of a subclass of `ASTVisitor`.

> ### Note on Typing and Genericity in the `analysis` Module

At the time the PyLGEN code was written, Cython lacked a **full-fledged generics system** that would have allowed extension classes (`cdef class`) (such as `ASTVisitor`, `ASTChildrenSelector`, `TraversalStrategy`, and `ASTWalker`), to statically infer the concrete types of the `Context` and `AST` subclasses with which they operate. Cython’s "fused types", the closest equivalent to generics, cannot be applied to extension classes. Consequently, it was not possible to create a type-safe generic hierarchy without sacrificing the performance benefits that justify the use of Cython in PyLGEN.

To maintain the advantages of static typing, the arguments were typed using the base classes (`Context` and `AST`), and `_check_context_type` was implemented as a runtime safeguard. While not strictly mandatory, this function verifies that the provided context is of the expected type; its use is a recommended practice for any contributor extending these classes.

It is important to emphasize that this is a **temporary compromise**. Recent versions of Cython (such as 3.3) have introduced support for generics and parameterized container types, and it is expected that support for generic extension classes will continue to mature. Once that happens, `_check_context_type` can be gradually replaced by native generic typing, rendering it obsolete. Until then, it should neither be removed nor dismissed as an unnecessary artifact, as it serves as the guarantee for type safety in the compiled version of PyLGEN.