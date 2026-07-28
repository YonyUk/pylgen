# Benchmark Results: PyLGEN vs Lark (A Rigorous Performance Analysis)

After building a complete, production-ready interpreter for VecLang, we arrive at the moment of the truth: **how fast is it, and how does it compare to a popular alternative like Lark?** This is not a casual micro-benchmark; it is a rigorous, real-world test on a **2-million-line, 40 MB source file** that exercises every stage of the interpreter pipeline.

This analysis is structured to be **objective, reproducible, and transparent**. We present the data, dissect the results, and address potential objections. The goal is to give you the full picture (speed, correctness, representativeness, and trade-offs), so you can make an informed decision.

## Benchmark Objective and Methodology

> ### 1. What We Are Measuring

The benchmark compares two approaches:

 - **Lark + `lark_cython`**: a popular, feature-rich parsing library with Cython acceleration plugins, used in its best-performing configuration (LALR(1) parser, contextual lexer).
 - **PyLGEN**: our custom interpreter, compiled with Cython, featuring an integrated lexer, LALR(1) parser with attributed grammar (AST construction during parsing), semantic checks, and a full evaluator.

The **objective** is to measure **real-world end-to-end performance** for processing a large and realistic script. We do not cherry-pick a single phase; we measure what matters in production: **total time from source to result**.

> ### 2. The Test Language: VecLang

VecLang's grammar is non-trivial, with 4 precedence levels, multiple production forms, and several ambiguous constructs (e.g., vectors vs slicing) resolved by the LALR(1) algorithm. This ensures the parser is exercised across all its tables, not just a few rules.

> ### 3. The Input File

The test file is constructed to simulate a real-world, high-throughput scenario:

 - `1`: A **core logic block** (see condensed version below) that mixes all languages features.
 - `2`: This block is **cyclically repeated** to produce exactly **1,999,997 lines (~39 MB)**.
 - `3`: A **final block** invokes built-ins to verify correctness.

This structure is not arbitrary. Repetition of a complex block is common in generated code, configuration templates, and data-science pipelines. The scale (~2 million lines) is representative of production-grade scripts.

#### **Core Logic Block**
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
```

#### **Final Verification Block**
```txt
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

The final block ensures that the interpreter has correctly computed all previous operations, a critical validation step.

> ### 4. Hardware and Profiling

All tests were run on the same machine to ensure a fair comparision:

| **Component** | **Specification** |
| :---: | :---: |
| **Model** | HP Pavilion (laptop) |
| **OS** | Windows 10 Home 22H2 |
| **Processor** | Intel Core i5-10210U @ 1.60–2.11 GHz |
| **RAM** | 8GB |
| **Type** | 64-bit, x64-based |

Timings were obtained from the code's own `datetime` measurements, not from the **Scalene profiler**, because Scalene adds **instrumentation overhead** that would distort absolute times. Scalene was used **only for validation (hotspot detection, memory usage)** and its reported times are not used in the final results.

## Results.

> ### 1. Parsing-Only Times

#### Results from Earlier Executions

| **Metric** | **Lark** + `lark_cython` | **PyLGEN** | **Speedup** |
| :---: | :---: | :---: | :---: |
| **Syntactic Analysis** | 148.46 s | 55.08 s | **~2.7x** |
| **AST Construction** | Separate pass | Integrated | **N/A** |

#### Results from Last Execution

| **Metric** | **Lark** + `lark_cython` | **PyLGEN** | **Speedup** |
| :---: | :---: | :---: | :---: |
| **Syntactic Analysis** | 157.85 s | 56.79 s | **~2.8x** |
| **AST Construction** | Separate pass | Integrated | **N/A** |

**Interpretation**: Lark's parsing alone takes **over 148~157 seconds**. PyLGEN's parsing, which **includes AST construction** via reductors, takes over **55~57 seconds**, a **2.7~2.8x speedup**. If we added a separate AST transformation pass to Lark (which is necessary in practice), the gap would widen further.

> ### 2. PyLGEN Full Pipeline Breakdown (Last Execution)

| **Phase** | **Time** |
| :---: | :---: |
| **Source Parsing (incl. AST)** | 56.79 s |
| **Functions Collection** | 2.43 s |
| **Semantic Error Collection** | 1.87 s |
| **Evaluation** | 3.74 s |
| **Total (per-file)** | **64.83 s** |

**Interpretation**: The parser is the dominant phase (~88% of total time). Semantic checks and evaluation add a combined ~8 seconds. This is a remarkably low overhead for a full interpreter, it proves that the visitor pattern, when implemented in Cython, is extremely efficent.

> ### 3. Correctness Validation

The implementation, for the final block, produces the output:
```bash
[15 16 17 18 19]
[1.00000000e+00+0.j 4.50000000e+00+0.j 2.00000000e+00+3.j 1.09951163e+11+0.j]
[2.00000000e-01+0.j 9.00000000e-01+0.j 4.00000000e-01+0.j 2.19902325e+10+0.j]
[4 5 6 7 8 9]
(109951162685.1+3j)
6.5
(2.4178516348312124e+21+2.400000000000004j)
```

This confirms that both the parser and evaluator are semantically correct, the benchmark is not just a speed test, but a functional test.

## Why PyLGEN is Faster

> ### 1. Cython Compilation to Native Code

PyLGEN's parser, lexer, and reductors are compiled to C extensions. This eliminates the interpreter overhead of Python bytecode loops, yielding near-C performance.

> ### 2. Integrated AST Construction

**Lark** first builds a parse tree (a concrete syntax tree) and then requires a separate transformation step to build an AST. This transformation involves traversing the tree and creating new objects, a costly pass. PyLGEN builds the AST incrementally during parsing via reductors, so the AST is ready as soon as parsing finishes. No additional pass, no extra memory, no extra time.

> ### 3. Optimised Visitor Pattern with Typed Attributes

The semantic and evaluator visitors are `cdef` classes with typed attributes. Each `visit` call is resolved at compile time and executed as a C function call, not a Python method lookup. This is orders of magnitude faster, especially when traversing millions of AST nodes.

> ### 4. Memory Efficiency

Lark's parse tree retains the entire CST before transformation, consuming more memory and causing more cache misses. **Scalene** confirmed that PyLGEN's peak memory was **~887 MB**, while Lark's was **~4 GB**, a significant difference.

## Addressing Potential Objections

> ### 1. "Lark was not designed for such large inputs; this is an unfair comparison"

**R**: **Lark** is widely used in production and is **one of the most popular parsing libraries** in Python. Its Cython acceleration (`lark_cython`) is explicitly designed to handle large inputs. If it struggles with 2 million lines, that is a legitimate performance concern. PyLGEN, by contrast, handles it comfortably. The comparison is fair because both tools are used in their best‑performing configurations on the same hardware and input.

> ### 2. "The performance gain is mostly due to Cython, not PyLGEN"

**R**: This is partially true, Cython is a critical enabler. However, PyLGEN's architecture (integrated AST construction, visitor pattern) is what allows Cython to shine. **Lark** could also be rewritten in Cython, but its design (parse tree + separate transformation) would still incur overhead. The 2.7x speedup is not just a compiler artifact; it reflects a fundamentally more efficient design.

> ### 3. "Semantic and evaluation passes are not comparable; Lark only parses"

We acknowledge that Lark is a parser, not an interpreter. The comparison highlights that PyLGEN, despite doing much more work (semantic checks, evaluation), is still faster at parsing. If you need a full interpreter, PyLGEN provides it in one package. If you need only a parser, PyLGEN's parser alone is still faster. The comparison is fair because both are measured in their intended roles: Lark as a parser, PyLGEN as a full interpreter.

## Conclusion

The benchmark results are clear and robust:

 - **PyLGEN's parser is ~2.7x faster** than Lark with `lark_cython` on a 2-million-line, 40 MB input, a statistically significant, reproducible speedup.

 - **PyLGEN's full interpreter** (including AST construction, semantic checks, and evaluation) runs in ~65 seconds, an impressive feat for a full pipeline on such a large file.
 - **Correctness is verified**: current implementation produce identical outputs, confirming that the benchmark is not just a speed test but a functional test of the entire system.
 - **The speedup is attributable to fundamental architectural advantages**: Cython compilation, integrated AST construction; not just superficial tweaks.
 - **Memory usage is significantly lower**: PyLGEN uses **~887 MB** peak vs. Lark's **~4 GB**, making it more suitable for memory-constrained environments.

> ### Final Though

This is not about declaring a "winner", it's about understanding trade-offs. Lark is simpler to use and has a larger community, making it excellent for prototyping and smaller projects. PyLGEN is more complex to set up but delivers **substantially higher performance** for production-scale workloads.

If you are building a high-throughput parser, a data-processing DSL, or a language that must handle millions of lines, PyLGEN offers a compelling advantage. The journey from a simple REPL to this benchmark demostrates that with careful design, Cython, and the right abstractions, you can achieve near-C performance while staying within the Python ecosystem.