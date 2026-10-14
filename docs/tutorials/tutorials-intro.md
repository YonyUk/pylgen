# Tutorials

You've installed PyLGEN, you've seen the quick start, and you have a rough idea of what each module does. Now it's time to actually build something. This section is a collection of hands-on, step-by-step tutorials that walk you through real implementations, from a bare-bones lexer to a full interpreter with a GUI. Each tutorial is self-contained, but they're designed to be read in a certain order, depending on what you're trying to learn.

## Two paths, one destination

The tutorials are split into two blocks, each with a different goal:

 - **Foundations**: you build the core pieces of the pipeline from scratch, using the **low-level API**. You write a lexer that scans tokens by hand, a parser that constructs its own **LR(0) automaton**, and you see the algorithms that PyLGEN uses internally. This is the path for anyone who wants to understand how a compiler works, not just how to use one.

 - **Complete Languages**: you build working interpreters and DSLs end to end, using the **high-level API**. You write a lexer, a grammar, an AST, semantic checks, and an evaluator, and you see how everything fits together. This is the path for anyone who wants to build a language, whether for production or for fun.

Both paths meet in the same place: a functional interpreter built on PyLGEN. The difference is how much of the machinery you see along the way.

## Where to start

If you're not sure which tutorial to begin with, find yourself in the table below.

| **Tutorial** | **Best for** | **Prerequisites** | **What you'll build** |
| :---: | :---: | :---: | :---: |
| [**Building a Lexer from Scratch**](./tutorials-foundations-building-a-lexer.md) | Understanding tokenization, DFAs, and maximal munch | Basic regex, basic automata | A maximal-munch tokenizer using raw DFAs |
| [**Building a Parser from Scratch**](./tutorials-foundations-building-a-parser.md) | Understanding LR parsing, closure, and goto | The lexer tutorial | An SLR parser built by hand from LR(0) states |
| **Arithmetic Interpreter** | Your first end-to-end interpreter | None | A REPL that evaluates arithmetic expressions |
| **Config DSL** | A small, indentation-sensitive DSL | None | A config parser that emits JSON |
| **Python Subset** | A full language with control flow and a GUI | The Arithmetic tutorial | A subset of Python with functions, loops, and a Tkinter GUI |
| **VecLang** | A production-grade, Cython-compiled interpreter | The Arithmetic tutorial | A vector language compiled to native code |

## How to read a tutorial

Every tutorial follows the same shape:

 - **Goal**: what you'll have when you're done.

 - **Prerequisites**: what you should already know or have installed.

 - **Steps**: the actual walkthrough, with code you can run.

 - **Recap**: a summary of what you built and what you learned.

 - **Next steps**: where to go from there.

You don't have to read them in order, but the two blocks are designed to be read linearly within themselves. The **Foundations** block builds on itself: the parser tutorial assumes you've read the lexer tutorial, or at least that you understand what a token is. The **Complete Languages** block also builds on itself, though more loosely: the Arithmetic tutorial is the smallest, and each subsequent tutorial adds features on top of the same pipeline.

!!! tip "Read the code, then run it"
    Every tutorial ends with a complete, runnable script. Don't just read it, copy it into a file, run it, and modify it. The fastest way to learn a compiler framework is to break it and see what happens.

!!! note "The examples are on GitHub"
    All the source code for these tutorials lives in the examples/ directory of the repository. If you get stuck, you can always compare your code against the reference implementation.

## A word of advice

PyLGEN gives you a lot of control, and that means a lot of decisions. You can build a language with a single grammar and a handful of reducers, or you can write custom traversal strategies, visitors, and selectors for every node type. Both are valid, and the tutorials show both extremes. The point isn't to use every feature, it's to use the right features for your language.

So pick a tutorial, open your editor, and start building. And when you're done, come back and try another one. Each one teaches something different, and together they cover every stage of the compilation pipeline.