# Step 4: Running VecLang from a File

Our interpreter is now fully functional: we have a lexer, a parser, an AST, semantic checks, and evaluator. But an interpreter that only works in an interactive console is just a toy, a real world languages are used to process files, run scripts, and produce output. In this final step, we'll build a **batch-mode interpreter** that reads a VecLang source file, executes it, and reports results or errors.

Unlike the previous tutorial, which ended with a REPL (Read-Eval-Print-Loop), VecLang is designed for production-scale workloads: processing millions of lines of code, running complex numerical computations, or generating data. The REPL is great for experimentation, but for automationand performance, we need a file-based runner.

## From Interactive to Batch

The REPL from the earlier tutorial worked as follows:

 - `1`: Prompt the user for input.
 - `2`: For each line, tokenize, parse, run semantic checks, evaluate, and print the result.
 - `3`: Repeat until the user types `exit()`.

This is fine for learning and experimenting, but it has limitations:

 - **Performance**: The pipeline is re-initialised for each line, which is wasteful for large programs.
 - **State persistence**: Variables persist across lines, but the context must be carefully managed.
 - **No batch processing**: You cannot run a script without manual intervention.

VecLang takes a different approach: it expects a single file, parses the entire file as a **sequence of instructions**, and executes them in a single pass. This is similar to how Python, Ruby, or JavaScript run scripts.

## The Command-Line Interface

We'll create a single entry point, a `main.py` that accepts a filename as a command-line argument. For example:

```bash
python main.py main.vcl
```

The main function will:

 - `1`: Build the lexer, parser, and walkers with the context.
 - `2`: Read the file content.
 - `3`: Tokenize and parse the content.
 - `4`: If lexical or syntax errors, run the semantic error collector.
 - `5`: If no semantic error, run the evaluator.
 - `6`: Show the runtime errors (if any).

We'll also support the `--help` flag and optionally print the AST for debugging.

!!! note "Error Handling in Batch Mode"
    In a REPL, a syntax error can be caught and the user can retry. In batch mode, any error should abort execution and report the error clearly.

## Modifications to the Pipeline

The core pipeline (lexer -> parser -> semantic checks -> evaluator) remains unchanged. The difference lies in how we orchestrate the passes and manage the context.

> ### 1. Reading the file

We'll use Python's built-in function `open()` to read the file as a string. The lexer expects a string input, so we pass the entire content at once.

> ### 2. Parsing the Whole Program

The grammar's start symbol is `VecLangProgram`, which is a sequence of instructions separated by newlines. The parser will produce a `VecLangInstructionsSequenceAST` containing all top level statements.

> ### 3. Semantic Analysis Passes

We'll run the `functions_collector` first to register all function definitions, then the `error_collector_walker` to perform static checks. If any semantic errors are found, we print them.

> ### 4. Evaluation Pass

If all checks pass, we run the `evaluator_walker` on the program AST. The evaluator will process each instruction in order, updating the context (variables, scopes, etc.).

## Implementation Skecth

Before write our main runner, we must to compile **veclang**, this is made through a `setup.py`.

```python
from setuptools.extension import Extension
from setuptools import setup
from Cython.Build import cythonize

interpreter_extensions = Extension(
    name='veclang.parser',
    sources=[
        'veclang/parser.pyx'
    ]
)

asts_extensions = Extension(
    name='veclang.asts',
    sources=[
        'veclang/asts.pyx'
    ]
)

visitors_extensions = Extension(
    name='veclang.visitors',
    sources=[
        'veclang/visitors.pyx'
    ]
)

errors_extension = Extension(
    name='veclang.errors',
    sources=[
        'veclang/errors.pyx'
    ]
)

lexer_extensions = Extension(
    name='veclang.lexer',
    sources=[
        'veclang/lexer.pyx'
    ]
)

setup(
    ext_modules=cythonize([
        interpreter_extensions,
        asts_extensions,
        visitors_extensions,
        errors_extension,
        lexer_extensions
    ]),
    language_level=3
)
```
Then run this command in your terminal inside the `veclang` folder:

```bash
python setup.py build_ext --inplace
```

This will compile the `.pyx` files into `.pyd` files extensions that Python can import by `import` statement.

Here's how the main runner might look.

File: `main.py`

```python
import os
from sys import argv

from veclang.lexer import build_lexer
from veclang.parser import build_parser
from veclang.visitors import build_walkers,get_ast_value

lexer = build_lexer()
VecLangParser = build_parser()
context,error_collector,functions_collector,evaluator = build_walkers()

if len(argv) < 2:
    raise ValueError('not input provided')

file = argv[1]

if not (os.path.exists(file) or os.path.isfile(file)):
    raise ValueError('Invalid argument')

help_flag = False
if len(argv) >= 3 and argv[2] == '--help':
    from pylgen.visual import set_cache_file,draw_ast
    help_flag = True
    set_cache_file('cache')

with open(file,'r') as f:
    text = f.read()
    lexer.load_text(text)
    ast = VecLangParser.parse(lexer.tokens)
    errors = []
    errors += list(lexer.errors)
    errors += VecLangParser.errors

    if not errors:
        if help_flag:
            draw_ast(ast,show=True,cache=True,select_menu=True) # type: ignore
        functions_collector.walk(ast)

    if not errors:
        error_collector.walk(ast)

    errors += context.errors

    if not errors:
        evaluator.walk(ast)
        errors += context.errors

    if not errors:
        result = get_ast_value(ast,context)
        if result is not None:
            print(result)

    if errors:
        for error in errors:
            print(error)
```

> ### Differences from the REPL

| **Aspect** | **REPL (tutorial)** | **Batch (VecLang)** |
| :---: | :---: | :---: |
| **Input** | User lines | Whole file |
| **Context persistence** | Across lines | Across the entire file, then discarded |
| **Error handling** | Print error and continue | Collects as many as it can, and abort execution |
| **Output** | Print result of each expression | Print final result (if any) |
| **Performance** | Re-parses each line | Single parse for the whole program |
| **Use case** | Learning, experimentation | Scripting, automation, large-scale processing |

## Performance Considerations

In batch mode, the entire file is parsed and processed in one go. This allows the lexer and parser to be built only once, and the context is reused for all instructions. The evaluator benefits from having the full AST in memory, enabling optimisations like constant folding or dead-code elimination (which we haven't implemented, but could be added later). The use of Cython ensures that all passes are fast. The semantic checks and evaluation run in native code, making VecLang suitable for processing larga datasets.

## Access to the Python Ecosystem in Batch Mode

The batch interpreter inherits all the ecosystem advantages we discussed earlier: it can call NumPy, SciPy, Matplotlib, or any other Python library. This makes VecLang a powerful glue language for scientific computing. You can write a script that reads data from a file, performs vectorised operations, and plot the results, all within VecLang syntax, while leveraging Python's extensive libraries underneath.

## Error Reporting in Batch Mode

In batch mode, it's crucial to report errors with enough context to fix them. The error classes we defined carry line and column numbers, and the stack trace helps locate the source of runtime errors. The main script prints each error with its location, making easy to identify issues.

For example:

```bash
RUNTIME ERROR: Division by zero not allowed at line 11, column 25
```

This is much more useful than a cryptic traceback.