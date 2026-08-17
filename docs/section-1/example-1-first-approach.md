# First approach

For our first example, let's create a simple [**REPL**](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) for arithmetic expressions that supports variable declarations and a few built-in functions. By the end, you'll have a working interpreter and a clear understanding of how PyLGEN's components fit together.

> ## What we're building
A **REPL** that evaluates expressions like:

```python
>>> x = 10
>>> y = x * 2 + 5
>>> y
25
>>> exit()
```

The language supports:

 - Arithmetic: `+`,`-`,`*`,`/`,`**`,`%`.
 - Parentheses and operator precedence.
 - Variables (assignment and usage).
 - Built-in commands: `exit()` and `clear()`.

We'll build it in four steps, following the classic compiler pipeline: **Lexer** -> **Parser** -> **Semantic Analysis** -> **Execution**. The project file structure is organized as follows:

    arithmetic_interpreter
        |--- asts.py
        |--- context.py
        |--- errors.py
        |--- grammar_symbols.py
        |--- grammar.py
        |--- lexer.py
        |--- reductors.py
        |--- semantic.py
        |--- visitors.py
    main.py

Let's dive in and start building!