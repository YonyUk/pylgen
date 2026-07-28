# Getting to know VecLang (A Test Language)

To stress-test an interpreter, you need a language that exercises all stages of the pipeline: lexing, parsing, semantic analysis, and evaluation. **VecLang** is exactly that, a small but expressive DSL that supports:

 - Complex numbers (`complex(2,3)`).
 - Function definitions and calls.
 - Arithmetic with `+`,`-`,`*`,`/`,`**`,`%`.
 - Vector literals (`[1,4.5,var]`) and range generation (`[4:10]`).
 - Indexing (`vec[2]`) and multi-level slicing (`[0:30][5:25][10:15]`).
 - Built-in functions: `sum`, `mean`, `dot`, `print`.

**VecLang** is expressive enough to write non-trivial programs, yet simple enough to implement in a few hundred lines. It's the perfect testbed for benchmarking because it forces the interpreter to exercise **every stage** of the pipeline: lexing, parsing, semantic validation, and evaluation.

## Why VecLang is a Good Benchmark Language

Before diving into the code, let's examine why VecLang is an excellent choice for measuring performance:

 - **Diverse Syntax**: It includes many token types (numbers, operators, keywords, identifiers,symbols like `[` and `]`, etc.).
 - **Rich Grammar**: Operator precedence, function definitions, vector literals, and slicing require a non-trivial LALR(1) grammar with many productions. This tests the parser's efficiency.
 - **Multiple AST Node Types**: The parser builds many different AST classes (binary ops, function calls, vector literals, indexing, slicing, etc.). This forces the reducer functions to work with diverse structures.
 - **Semantic Checks**: function argument count, and variable declaration validation stress the visitor pattern.
 - **Heavy Evaluation**: Vectors and operations on them (element-wise arithmetic, dot product, mean) involve loops and array operations, which are computationally intensive and test the evaluator.
 - **Realistic code size**: The benchmark file (**~2 million lines**) simulates a production-scale input, revealing performance bottlenecks that only appear under load.
 - **Complete pipeline**: Unlike parser-only tools, VecLang includes the entire interpreter cycle, making it a realistic measure of end-to-end performance.

Example code in VecLang:
```txt
// testing complex numbers creation
complex_number = complex(2,3)

// testing function declarations
f(x:complex,y:float) = x / (y - 5)

// testing functions call
var_a = f(complex_number,10)

// more functions declarations
g(x:int,y:int) = x ** y / 10 - 100

// more functions calls
var_b = g(20,4)

// arithmetic operations
var_c = (var_a + var_b) / (var_a - var_b)

// combining calls and operations
var_d = g(50,4) % 7

// testing vectors
vector_1 = [1,4.5,complex_number,var_b]
vector_2 = vector_1 / 5

// testing range
vector_3 = [4:10]

// testing indexing
var_e = vector_1[1]
var_f = vector_2[2]
var_g = vector_3[3]

var_slice = vector_3[1:3]
var_slice_1 = var_slice[0:1]

// testing multiple slicing
var_slice_2 = [0:30][5:25][10:15]

// testing built-in functions
print(var_slice_2)
print(vector_1)
print(vector_2)
print(vector_3)

var_sum = sum(vector_1)
var_mean = mean(vector_3)
var_dot = dot(vector_1,vector_2)

print(var_sum)
print(var_mean)
print(var_dot)
```

With these points in mind, let's start building VecLang from scratch.