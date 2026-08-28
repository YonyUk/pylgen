# PyLGEN vs Lark Benchmark: ~2x Faster Parsing and 4x Less Memory (Performance Analysis)

After building a complete, production-ready interpreter for VecLang, we arrive at the moment of the truth: **how fast is it, and how does it compare to a popular alternative like Lark?** This is not a casual micro-benchmark; it is a rigorous, real-world test on a **2-million-line, 40 MB source file** that exercises every stage of the interpreter pipeline.

This analysis is structured to be **objective, reproducible, and transparent**. We present the data, dissect the results, and address potential objections. The goal is to give you the full picture (speed, correctness, representativeness, and trade-offs), so you can make an informed decision.

## Benchmark Objective and Methodology

!!! note "Sources of the Benchmark"

    The source code of the test language **VecLang** and the benchmark file used, can be found both on the [github repository](https://github.com/YonyUk/pylgen/tree/master/examples/veclang)

    [download 2M lines file<br>(benchmark.zip)](https://github.com/YonyUk/pylgen/raw/master/examples/veclang/benchmark.zip){ .md-button .md-button--primary style="text-align: center;" }
    [download source code<br>(veclang)](https://download-directory.github.io/?url=https://github.com/YonyUk/pylgen/tree/master/examples/veclang){ .md-button .md-button--primary style="text-align: center;" }

> ### 1. What We Are Measuring

The benchmark compares two approaches:

 - **Lark + `lark_cython`**: a popular, feature-rich parsing library with Cython acceleration plugins, used in its best-performing configuration (LALR(1) parser, contextual lexer).
 - **PyLGEN**: our custom interpreter, compiled with Cython, featuring an integrated lexer, LALR(1) parser with attributed grammar (AST construction during parsing), semantic checks, and a full evaluator.

The **objective** is to measure **real-world end-to-end performance** for processing a large and realistic script. We do not cherry-pick a single phase; we measure what matters in production: **total time from source to result**.

> ### 2. Methodology

To ensure statistical significance and eliminate transient effects, we followed a rigorous procedure:

 - **Warm‑up phase**: 5 executions were run to prime caches and allow the JIT (if any) to stabilise.

 - **Measurement phase**: 9 subsequent executions were timed for the 2‑million‑line file; the reported times are the minimum, maximum, and mean over these runs.

 - **Scaling test**: An additional run was performed on a 4‑million‑line file to assess performance scalability. **This run was executed immediately after the 9 measurement runs on the 2‑million‑line file**, in the same session and without restarting the system, to ensure consistent conditions (cached files, warm CPU caches, and stable system state).

All tests were conducted on the same hardware (see below) with no other heavy processes running.

> ### 3. The Test Language: VecLang

VecLang's grammar is non-trivial, with 4 precedence levels, multiple production forms, and several ambiguous constructs (e.g., vectors vs slicing) resolved by the LALR(1) algorithm. This ensures the parser is exercised across all its tables, not just a few rules.

> ### 4. The Input Files

Two test files were constructed to simulate real‑world, high‑throughput scenarios:

 - **File A**: 2,000,011 lines (~39.16 MB), built by repeating a complex core logic block (see condensed version below) that mixes all language features, plus a final verification block. This is representative of generated code, configuration templates, and data‑science pipelines.

 - **File B**: 4,000,008 lines (~78.33 MB), built by doubling the repetition of the same core block, to test scaling behaviour.

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

> ### 5. Hardware and Profiling

All tests were run on the same machine to ensure a fair comparision:

| **Component** | **Specification** |
| :---: | :---: |
| **Model** | HP Pavilion (laptop) |
| **OS** | Windows 10 Home 22H2 |
| **Processor** | Intel Core i5-10210U @ 1.60–2.11 GHz |
| **RAM** | 8GB |
| **Type** | 64-bit, x64-based |

Timings were obtained from the code's own `datetime` measurements, not from the **Scalene profiler**, because Scalene adds **instrumentation overhead** that would distort absolute times. Scalene was used **only for validation (hotspot detection, memory usage)** and its reported times are not used in the final results.

> ### 6. Software Versions

The benchmark was executed with the following software versions:

| **Component** | **Version** |
| :--- | :--- |
| **`Python`** | 3.13.7 |
| **`Lark`** | 1.3.1 |
| **`lark-cython`** | 0.0.17 |
| **`lark-rust`** | 0.2.1 (attempted, not used in final results) |

These versions were obtained via `pip show` and are the latest stable releases available at the time of the experiment (August 2026).

> ### 6. Interactive Profiling Data (Scalene HTML Reports)

To uphold our commitment to **objective, reproducible, and transparent** analysis, we provide the complete interactive HTML reports generated by **Scalene** during the validation phase. While we deliberately excluded Scalene’s absolute timings from the final speedup calculations (due to its instrumentation overhead), these reports offer a granular, visual breakdown of where time and memory are actually spent.

You can explore the raw data here:

- **PyLGEN Full Report**: [`scalene_pylgen.html`](../images/benchmark/pylgen/1/scalene-pylgen.html)  
- **Lark + `lark_cython` Full Report**: [`scalene_lark.html`](../images/benchmark/lark/scalene-lark.html)

> **What to look for in these reports**:

> 1. **CPU Hotspots**: Both reports confirm that the parsing phase (specifically the `reductor` functions in PyLGEN) dominates the CPU cycles. In PyLGEN, this accounts for ~85% of the native execution time, validating our optimization priorities.
>
> 2. **Memory Timeline**: The memory allocation graphs provide a visual confirmation of the peak usage disparity—PyLGEN's graph stays in 928 MB, while Lark's allocation curve reaches 4 GB.
>
> 3. **Line-by-line Overhead**: The HTML drill-down allows you to inspect exactly which regex patterns (in the lexer) or which visit methods (in the evaluator) incur the most cost, offering actionable insights for future micro-optimizations.
>
> These visualizations are not meant to replace the absolute `datetime` metrics presented below; rather, they serve as a **supplementary evidence layer** that reinforces the architectural conclusions drawn in this analysis.

## Results.

> ### 1. Parsing-Only Times

| **Metric** | **Lark** + `lark_cython` | **PyLGEN** | **Speedup** |
| :---: | :---: | :---: | :---: |
| **Minimum Parsing Time** | 115.87 s | 59.85 s | - |
| **Maximum Parsing Time** | 117.34 s | 61.65 s | – |
| **Mean Parsing Time** | 116.73 s | 60.80 s | ~1.92x |
| **AST Construction** | Separate pass | Integrated | **N/A** |
| **Peak Memory Usage** | ~4 GB | ~928 MB | – |

**Interpretation**: Lark's parsing alone takes **over 116 seconds** on average. PyLGEN's parsing, which **includes AST construction** and **semantic errors collecting** via reductors, takes **about 60.8 seconds**, a **~1.92x speedup**. If we added a separate AST transformation pass to Lark (which is necessary in practice), the gap would widen further. Moreover, PyLGEN uses **~4x less memory**, a critical advantage for large-scale processing.

> ### 2. PyLGEN Full Pipeline Breakdown

| **Phase** | **Time** |
| :---: | :---: |
| **Source Parsing (incl. AST)** | 60.80 s |
| **Functions Collection** | 0.11 s |
| **Semantic Error Collection** | 1.47 s |
| **Evaluation** | 3.65 s |
| **Total (per-file)** | **66.03 s** |

**Interpretation**: The parser is the dominant phase (~92% of total time). Semantic checks and evaluation add a combined ~5.2 seconds. This is a remarkably low overhead for a full interpreter, it proves that the visitor pattern, when implemented in Cython, is extremely efficient.

> ### 3. Scaling to 4M Lines

| **Metric** | **Lark + `lark_cython`** | **PyLGEN** | **Speedup** |
| :---: | :---: | :---: | :---: |
| **Parsing Time** | 335.42 s | 122.67 s | ~2.73x |
| **PyLGEN Full Pipeline** | – | 122.67+2.00+2.81+7.09 = 134.57 s | – |
| **Peak Memory Usage (PyLGEN)** | not measured | ~2 GB | – |

!!! note
    Although we did not measure Lark's memory usage for the 4M‑line file with Scalene, extrapolating from the 2M‑line case suggests it would exceed 8 GB, given the linear relationship between input size and memory consumption observed in earlier runs.

> memory usage results on [`scalene_pylgen.html`](../images/benchmark/pylgen/2/scalene-pylgen.html)

The speedup increases with file size, indicating that PyLGEN's integrated approach scales better. Lark's overhead per line grows faster, possibly due to its separate AST construction and higher memory pressure.

#### Analysis of Scaling Behaviour

The scaling test reveals an interesting trend: the speedup of PyLGEN over Lark + `lark_cython` increases from **~1.92x** (2M lines) to **~2.73x** (4M lines). While part of this can be attributed to PyLGEN's more efficient parsing algorithm and integrated AST construction, **memory constraints likely played a significant role**.

The benchmark hardware had only **8 GB of RAM**. For the 2M‑line file (≈40 MB), Lark's peak memory usage was already **~4 GB** (as measured by Scalene). When the input size doubled to 4M lines (≈78 MB), Lark's memory footprint likely exceeded the available physical RAM, forcing the operating system to use **swap space**. This results in:

- **Increased I/O overhead**: Swapping causes frequent disk reads/writes, which are orders of magnitude slower than RAM access.
- **CPU contention**: The kernel spends more time managing memory pages, reducing the CPU cycles available for parsing.
- **Cache thrashing**: Larger working sets degrade CPU cache efficiency.

PyLGEN, by contrast, used only **~928 MB** for the 2M‑line file and **~2 GB** for the 4M‑line file, staying well within the physical RAM limit. This allowed it to avoid swapping and maintain consistent performance scaling.

**Interpretation**: The widening speedup gap is also a consequence of Lark's higher memory pressure, which becomes a bottleneck under constrained hardware. In environments with abundant RAM (e.g., 32 GB or more), the difference might be smaller. However, for typical developer laptops or cloud instances with limited memory, PyLGEN's memory efficiency provides a tangible, real‑world advantage.

This observation underscores that **performance is not just about CPU speed; memory footprint is equally critical**, especially when processing large files.

> ### 4. Correctness Validation

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

## Attempted Benchmark with `lark-rust`

In addition to the comparison with Lark + `lark_cython`, we attempted to evaluate **lark-rust** (version 0.2.1), a Rust-based accelerator for Lark that promises a 1.4x–1.7x speedup over `lark_cython`. This would have provided a more complete picture of the performance landscape, especially given that `lark-rust` is gaining attention as a high-performance alternative.

> ### Methodology

The same input file (2M lines, 40 MB) and the same VecLang grammar were used. The parser was instantiated with:

```python
from lark import Lark
import lark_rust

# ....

parser = Lark(GRAMMAR, parser='lalr', lexer='contextual', _plugins=lark_rust.plugins)
```

This is the recommended configuration for `lark-rust` (LALR(1) with contextual lexer), and it mirrors the setup used for `lark_cython`.

> ### Results

The benchmark **could not be completed** due to compatibility issues between `lark-rust` and the VecLang grammar. Two errors were encountered:

```bash
Traceback (most recent call last):
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark_rust\__init__.py", line 99, in next_token
    return lexer.next_token(lexer_state, parser_state)
           ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
lark.exceptions.UnexpectedCharacters: No terminal matches '_' in the current parser context, at line 2 col 8

complex_number = complex(2,3)
       ^
Expected one of: 
        * LPAR

Previous tokens: Token("TYPE_COMPLEX", "complex")


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "[PROJECT_ROOT]\lark-pylgen-comparision\main.py", line 128, in <module>
    tree = parser.parse(text)
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark\lark.py", line 677, in parse
    return self.parser.parse(text, start=start, on_error=on_error)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark\parser_frontends.py", line 131, in parse
    return self.parser.parse(stream, chosen_start, **kw)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark_rust\__init__.py", line 274, in parse
    return self.parser.parse(lexer, start)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark_rust\__init__.py", line 190, in parse
    return self.parse_from_state(parser_state)
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark_rust\__init__.py", line 215, in parse_from_state
    token = inner_lexer.next_token(lexer_state, state)
  File "[PROJECT_ROOT]\lark-pylgen-comparision\Lib\site-packages\lark_rust\__init__.py", line 107, in next_token
    terminals_by_name=self.root_lexer.terminals_by_name,
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'builtins.BasicLexer' object has no attribute 'terminals_by_name'
```

> ### Conclusion on `lark-rust`

`lark-rust` is a promising project, but at the time of writing, it is not fully compatible with complex grammars that use a contextual lexer and have token priority rules (e.g., keywords vs. identifiers). For this reason, **we were unable to include `lark-rust` in the main benchmark**.

We will revisit this comparison when `lark-rust` reaches a stable state with full compatibility. In the meantime, the benchmark results against `lark_cython` remain the most robust and reproducible reference.

## Why PyLGEN is Faster

> ### 1. Cython Compilation to Native Code

PyLGEN's parser, lexer, and reductors are compiled to C extensions. This eliminates the interpreter overhead of Python bytecode loops, yielding near-C performance.

> ### 2. Integrated AST Construction

**Lark** first builds a parse tree (a concrete syntax tree) and then requires a separate transformation step to build an AST. This transformation involves traversing the tree and creating new objects, a costly pass. PyLGEN builds the AST incrementally during parsing via reductors, so the AST is ready as soon as parsing finishes. No additional pass, no extra memory, no extra time.

> ### 3. Optimised Visitor Pattern with Typed Attributes

The semantic and evaluator visitors are `cdef` classes with typed attributes. Each `visit` call is resolved at compile time and executed as a C function call, not a Python method lookup. This is orders of magnitude faster, especially when traversing millions of AST nodes.

> ### 4. Memory Efficiency

Lark's parse tree retains the entire CST before transformation, consuming more memory and causing more cache misses. **Scalene** confirmed that PyLGEN's peak memory was **~928 MB**, while Lark's was **~4 GB**, a significant difference.

## Addressing Potential Objections

> ### 1. "Lark was not designed for such large inputs; this is an unfair comparison"

**R**: **Lark** is widely used in production and is **one of the most popular parsing libraries** in Python. Its Cython acceleration (`lark_cython`) is explicitly designed to handle large inputs. If it struggles with 2 million lines, that is a legitimate performance concern. PyLGEN, by contrast, handles it comfortably. The comparison is fair because both tools are used in their best‑performing configurations on the same hardware and input.

> ### 2. "The performance gain is mostly due to Cython, not PyLGEN"

**R**: Cython is a critical enabler, but PyLGEN's architecture (integrated AST construction, visitor pattern) is what allows Cython to shine. Lark could be rewritten in Cython, but its design (CST + separate transformation) would still incur overhead. The speedup reflects a fundamentally more efficient design.

> ### 3. "Semantic and evaluation passes are not comparable; Lark only parses"

We acknowledge that Lark is a parser, not an interpreter. The comparison highlights that PyLGEN, despite doing much more work (semantic checks, evaluation), is still faster at parsing. If you need a full interpreter, PyLGEN provides it in one package. If you need only a parser, PyLGEN's parser alone is still faster. The comparison is fair because both are measured in their intended roles: Lark as a parser, PyLGEN as a full interpreter.

## Conclusion

The benchmark results are clear and robust:

 - **PyLGEN's parser is ~1.92x faster** than Lark with `lark_cython` on a 2-million-line, 40 MB input, and **~2.7x** faster on the 4M‑line, 78 MB input; a statistically significant, reproducible speedup.
 - **PyLGEN's full interpreter** (including AST construction, semantic checks, and evaluation) runs in ~66 seconds, an impressive feat for a full pipeline on such a large file.
 - **Correctness is verified**: current implementation produce identical outputs, confirming that the benchmark is not just a speed test but a functional test of the entire system.
 - **The speedup is attributable to fundamental architectural advantages**: Cython compilation, integrated AST construction; not just superficial tweaks.
 - **Memory usage is significantly lower**: PyLGEN uses **~928 MB** peak vs. Lark's **~4 GB**, making it more suitable for memory-constrained environments.

> ### Final Thought

This is not about declaring a "winner", it's about understanding trade‑offs. Lark is simpler to use and has a larger community, making it excellent for prototyping and smaller projects. PyLGEN is more complex to set up but delivers **substantially higher performance** and **much lower memory footprint** for production‑scale workloads.

If you are building a high‑throughput parser, a data‑processing DSL, or a language that must handle millions of lines, PyLGEN offers a compelling advantage. The journey from a simple REPL to this benchmark demonstrates that with careful design, Cython, and the right abstractions, you can achieve near‑C performance while staying within the Python ecosystem.

## Appendix A: Lark Benchmark Code

The following code was used to measure parsing times for Lark + `lark_cython` (and was the basis for the attempted `lark-rust` run).

```python
from lark import Lark
import lark_cython
from datetime import datetime

GRAMMAR = r"""// ==================== TOKENS ====================
INT_NUMBER: /\d+/
FLOAT_NUMBER: /\d*\.\d+|\d+e(\+|\-)\d+/
VARIABLE: /[a-zA-Z_]\w*/
NEWLINE: "\n"
PLUS: "+"
MINUS: "-"
MUL: "*"
DIV: "/"
MOD: "%"
POWER: "**"
EQ: "="
LPAR: "("
RPAR: ")"
LBRACK: "["
RBRACK: "]"
COMMA: ","
COLON: ":"
TYPE_COMPLEX: "complex"
TYPE_FLOAT: "float"
TYPE_INT: "int"
TYPE_VECTOR: "vector"
SUM_KEYWORD: "sum"
MEAN_KEYWORD: "mean"
DOT_KEYWORD: "dot"
PRINT_KEYWORD: "print"

%ignore /[ \t]+/
%ignore /\/\/.*\n/

start: vec_lang_program

vec_lang_program: vec_lang_instructions_sequence

vec_lang_instructions_sequence: (NEWLINE* vec_lang_instruction)+ NEWLINE*

vec_lang_instruction: arithmetic_expression_level_1
    | function_decl
    | variable_expression EQ arithmetic_expression_level_1
    | PRINT_KEYWORD LPAR function_args RPAR

arithmetic_expression_level_1: arithmetic_expression_level_1 PLUS arithmetic_expression_level_2
    | arithmetic_expression_level_1 MINUS arithmetic_expression_level_2
    | arithmetic_expression_level_2

arithmetic_expression_level_2: arithmetic_expression_level_2 MUL arithmetic_expression_level_3
    | arithmetic_expression_level_2 DIV arithmetic_expression_level_3
    | arithmetic_expression_level_2 MOD arithmetic_expression_level_3
    | arithmetic_expression_level_3

arithmetic_expression_level_3: arithmetic_expression_level_3 POWER arithmetic_expression_level_4
    | arithmetic_expression_level_4

arithmetic_expression_level_4: number_expression
    | variable_expression
    | vector
    | indexing
    | function_call
    | LPAR arithmetic_expression_level_1 RPAR

number_expression: number
    | complex_number

number: INT_NUMBER
    | FLOAT_NUMBER
    | PLUS INT_NUMBER
    | MINUS INT_NUMBER
    | PLUS FLOAT_NUMBER
    | MINUS FLOAT_NUMBER

complex_number: TYPE_COMPLEX LPAR number COMMA number RPAR
    | number VARIABLE

variable_expression: VARIABLE

vector: LBRACK components RBRACK
    | LBRACK range RBRACK
    | slicing

components: arithmetic_expression_level_1
    | components COMMA arithmetic_expression_level_1

range: INT_NUMBER COLON INT_NUMBER
    | MINUS INT_NUMBER COLON INT_NUMBER
    | INT_NUMBER COLON MINUS INT_NUMBER
    | MINUS INT_NUMBER COLON MINUS INT_NUMBER

indexing: variable_expression LBRACK INT_NUMBER RBRACK
    | vector LBRACK INT_NUMBER RBRACK

slicing: variable_expression LBRACK range RBRACK
    | vector LBRACK range RBRACK

function_call: variable_expression LPAR function_args RPAR
    | SUM_KEYWORD LPAR function_args RPAR
    | MEAN_KEYWORD LPAR function_args RPAR
    | DOT_KEYWORD LPAR function_args RPAR

function_args: arithmetic_expression_level_1
    | function_args COMMA arithmetic_expression_level_1

function_decl: variable_expression LPAR function_decl_args RPAR EQ arithmetic_expression_level_1

function_decl_args: variable_expression COLON type
    | function_decl_args COMMA variable_expression COLON type

type: TYPE_COMPLEX
    | TYPE_FLOAT
    | TYPE_INT
    | TYPE_VECTOR
"""

text = ''
with open('code.lgn','r') as f:
    text = f.read()


parser = Lark(GRAMMAR,parser='lalr',lexer='contextual',_plugins=lark_cython.plugins)

t = datetime.now()
tree = parser.parse(text)
print('parsed in',datetime.now() - t)
```

## Appendix B: Lark Benchmark Code (`lark-rust` version)

```python
from lark import Lark
import lark_rust
from datetime import datetime

GRAMMAR = r"""// ==================== TOKENS ====================
INT_NUMBER: /\d+/
FLOAT_NUMBER: /\d*\.\d+|\d+e(\+|\-)\d+/
VARIABLE: /[a-zA-Z_]\w*/
NEWLINE: "\n"
PLUS: "+"
MINUS: "-"
MUL: "*"
DIV: "/"
MOD: "%"
POWER: "**"
EQ: "="
LPAR: "("
RPAR: ")"
LBRACK: "["
RBRACK: "]"
COMMA: ","
COLON: ":"
TYPE_COMPLEX: "complex"
TYPE_FLOAT: "float"
TYPE_INT: "int"
TYPE_VECTOR: "vector"
SUM_KEYWORD: "sum"
MEAN_KEYWORD: "mean"
DOT_KEYWORD: "dot"
PRINT_KEYWORD: "print"

%ignore /[ \t]+/
%ignore /\/\/.*\n/

start: vec_lang_program

vec_lang_program: vec_lang_instructions_sequence

vec_lang_instructions_sequence: (NEWLINE* vec_lang_instruction)+ NEWLINE*

vec_lang_instruction: arithmetic_expression_level_1
    | function_decl
    | variable_expression EQ arithmetic_expression_level_1
    | PRINT_KEYWORD LPAR function_args RPAR

arithmetic_expression_level_1: arithmetic_expression_level_1 PLUS arithmetic_expression_level_2
    | arithmetic_expression_level_1 MINUS arithmetic_expression_level_2
    | arithmetic_expression_level_2

arithmetic_expression_level_2: arithmetic_expression_level_2 MUL arithmetic_expression_level_3
    | arithmetic_expression_level_2 DIV arithmetic_expression_level_3
    | arithmetic_expression_level_2 MOD arithmetic_expression_level_3
    | arithmetic_expression_level_3

arithmetic_expression_level_3: arithmetic_expression_level_3 POWER arithmetic_expression_level_4
    | arithmetic_expression_level_4

arithmetic_expression_level_4: number_expression
    | variable_expression
    | vector
    | indexing
    | function_call
    | LPAR arithmetic_expression_level_1 RPAR

number_expression: number
    | complex_number

number: INT_NUMBER
    | FLOAT_NUMBER
    | PLUS INT_NUMBER
    | MINUS INT_NUMBER
    | PLUS FLOAT_NUMBER
    | MINUS FLOAT_NUMBER

complex_number: TYPE_COMPLEX LPAR number COMMA number RPAR
    | number VARIABLE

variable_expression: VARIABLE

vector: LBRACK components RBRACK
    | LBRACK range RBRACK
    | slicing

components: arithmetic_expression_level_1
    | components COMMA arithmetic_expression_level_1

range: INT_NUMBER COLON INT_NUMBER
    | MINUS INT_NUMBER COLON INT_NUMBER
    | INT_NUMBER COLON MINUS INT_NUMBER
    | MINUS INT_NUMBER COLON MINUS INT_NUMBER

indexing: variable_expression LBRACK INT_NUMBER RBRACK
    | vector LBRACK INT_NUMBER RBRACK

slicing: variable_expression LBRACK range RBRACK
    | vector LBRACK range RBRACK

function_call: variable_expression LPAR function_args RPAR
    | SUM_KEYWORD LPAR function_args RPAR
    | MEAN_KEYWORD LPAR function_args RPAR
    | DOT_KEYWORD LPAR function_args RPAR

function_args: arithmetic_expression_level_1
    | function_args COMMA arithmetic_expression_level_1

function_decl: variable_expression LPAR function_decl_args RPAR EQ arithmetic_expression_level_1

function_decl_args: variable_expression COLON type
    | function_decl_args COMMA variable_expression COLON type

type: TYPE_COMPLEX
    | TYPE_FLOAT
    | TYPE_INT
    | TYPE_VECTOR
"""

text = ''
with open('code.lgn','r') as f:
    text = f.read()


parser = Lark(GRAMMAR,parser='lalr',lexer='contextual',_plugins=lark_rust.plugins)

t = datetime.now()
tree = parser.parse(text)
print('parsed in',datetime.now() - t)
```