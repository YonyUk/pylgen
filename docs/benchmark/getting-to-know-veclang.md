# Getting to know VecLang (A Test Language)

To stress-test an interpreter, you need a language that exercices all stages of the pipeline: lexing, parsing, semantic analysis, and evaluation. **VecLang** is exactly that, a small but expressive DSL that supports:

 - Compex numbers (`complex(2,3)`).
 - Function definitions and calls.
 - Arithmetic with `+`,`-`,`*`,`/`,`**`,`%`.
 - Vector literals (`[1,4.5,var]`) and range generation (`[4:10]`).
 - Indexing (`vec[2]`) and multi-level slicing (`[0:30][5:25][10:15]`).
 - Built-in functions: `sum`, `mean`, `dot`, `print`.

**VecLang** is expressive enough to write non-trivial programs, yet simple enough to implement in a few hundred lines. It's the perfect testbed for benchmarking because it forces the interpreter to exercice **every stage** of the pipeline: lexing, parsing, semantic validation, and evaluation.

## Why VecLang is a Good Benchmark Language

Before diving into the code, let's examine why VecLang is an excellent choice for measuring performance:

 - **Diverse Syntax**: It includes many token types (numbers, operators, keywords, identifiers,symbols like `[` and `]`, etc.).
 - **Rich grammar**: Operator precedence, function definitions, vector literals, and slicing require a non-trivial LALR(1) grammar with many productions. This tests the parser's efficiency.
 **Multiple AST node types**: The parser builds many different AST classes (binary ops, function calls, vector literals, indexing, slicing, etc.). This forces the reducer functions to work with diverse structures.
 - **Semantic checks**: function argument count, and variable declaration validation stress the visitor pattern.
 - **Heavy evaluation**: Vectors and operations on them (element-wise arithmetic, dot product, mean) involve loops and array operations, which are computationally intensive and test the evaluator.
 - **Realistic code size**: The benchmark file (**~2 million lines**) simulates a production-scale input, revealing performance bottlenecks that only appear under load.
 - **Complete pipeline**: Unlike parser-only tools, VecLang includes the entire interpreter cycle, making it a realistic measure of end-to-end performance.

With these points in mind, let's start building VecLang from scratch.