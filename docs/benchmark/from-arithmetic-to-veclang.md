# Language Evolution: From Arithmetic to VecLang

The journey from the simple arithmetic language in the tutorial to VecLang is a testament to the extensibility of the visitor-based architecture. In the pure-Python version, adding a new feature like vectors or functions required:

 - `1`: Creating new AST classes (e.g., `VectorAST`,`FunctionCallAST`).
 - `2`: Adding new visitors for semantic checks and evaluation.
 - `3`: Updating the grammar and reductors.
 - `4`: Possibly extending the context to handle new data types.

The process was straightforward because the codebase was small and all in Python. The visitor pattern decoupled the AST structure from operations, so existing visitors remained untouched, we simply added new ones.

In VecLang, we've scaled that same approach to a much richer language. The key insight is that **the visitor patterns makes the system open for extension but closed for modification**. To add a new construct (say, a `map` function), we would:

 - `1`: Add a new AST class (e.g., `MapAST`) and its corresponding symbol in `asts.pxd` and `asts.pyx`.
 - `2`: Add production rules in the grammar (`parser.pyx`) to parse it.
 - `3`: Add a reductor to build the AST.
 - `4`: Add semantic error collectors (if needed) as new visitor classes.
 - `5`: Add an evaluator visitor.

Crucially, **existing visitors, selectors, and the traversal strategy remain unchanged**. The new visitors simply register with the existing walkers. In Cython, we also need to declare the new classes in `.pxd` files and recompile, but the logical steps are identical to the pure-Python case.

The added complexity in Cython comes from managing type declarations and ensuring that all new classes are properly `cdef`-ed for performance. However, this is a one-time cost per new feature; the runtime performnce benefits far outweigh the development overhead. Moreover, because the framework is generic and type-aware, the compiler catches many mistakes early (e.g., mismatched types in visitor signatures), reducing debugging time.

## Reflection: Is it ***always*** that easy?

Not quite. If a new feature requires changes to the traversal strategy (e.g., a different visiting order) or to the context (e.g., a new kind of storage), then we might need to modify existing code. But in practice, most language extensions fit cleanly into the existing visitor skeleton. The design we've built is robust enough to accommodate a wide range of features without forcing rewrites, a string indicator of a well-architected system.

## Leveraging the Python Ecosystem

One of the strongest arguments for building a language on top of Python (and Cython) is the access to the vast Python ecosystem. VecLang uses **NumPy** extensively for vector operations. Without NumPy, we would have to implement array operations in pure Python loops, which would be painfully slow. With NumPy, operations like element-wise addition, dot product, and slicing are delegated to highly optimised C/Fortran libraries.

This is not just a convenience; it's a strategic advantage. It allows VecLang to be a high-performance DSL for numerical computing, similar to what NumPy does for Python itself, but with a custom syntax tailored to the problem domain. The ability to call any Python library from within VecLang (if we exposed it) would be trivial, thanks to the seamless integration.

The pure-Python arithmetic interpreter didn't need NumPy because it only handled scalars. But as soon as we introduced vectors, NumPy became essential. This illustrates how the ecosystem can be leveraged incrementally as the language grows. Moreover, we could easily add support for `matplotlib` to plot vectors, or `scipy` for advanced statistics, simply by calling those libraries from within our evaluator visitors.

> ### Trade-offs:

Relying on NumPy adds a dependency and increases the interpreter's footprint. For environments where NumPy is not avialable, this would be a problem. However, for a DSL aimed at data science or numerical computing, it's a natural fit. Additionally, for very small vectors (size < 10), the overhead of calling NumPy might outweigh the benefits; in such cases, a pure-Python loop could be faster. VecLang could be enhanced to choose the implementation based on vector size, but we haven't implemented that optimisation.

> ### Counter-argument

Some might argue that using NumPy ties the language to a specific library, making it less portable. However, the design is modular: the visitors could be swapped to use a different array library (e.g., `array` module or `list`) without changing the grammar or AST. This is another benefit of the visitor pattern, the evaluation logic is isolated.

## Next Steps

With semantic analysis and evaluation in place, our interpreter is functionally complete. The only missing piece is a user interface, but this step is very similar to the final step of the earlier tutorial. Let's do it!