# PyLGEN: The Python-Native Compiler Framework for Building Interpreters and DSLs


[![GitHub Repo](https://img.shields.io/badge/View%20on-GitHub-black?logo=github)](https://github.com/yonyuk/pylgen)
[![PyPI 0.6.0](https://img.shields.io/pypi/v/pylgen-core.svg)](https://pypi.org/project/pylgen-core?cache=1)
![PyPI - 3.12](https://img.shields.io/pypi/pyversions/pylgen-core?cache=1)
![PyPI - LICENSE](https://img.shields.io/pypi/l/pylgen-core?cache=1)
[![CI](https://github.com/YonyUk/pylgen/actions/workflows/ci.yml/badge.svg)](https://github.com/YonyUk/pylgen/actions/workflows/ci.yml?cache=1)
![Supported OS](https://img.shields.io/badge/Platforms-macOS%20%7C%20Windows%20%7C%20Linux-blue)

*From prototype to production: A **Python-native [compiler](https://en.wikipedia.org/wiki/Compiler-compiler) framework** that brings the ["**Dragon Book**"](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools) to life in Python with clarity throughout. A high-performance tool to build interpreters and [Domain-Specific Languages (DSLs)](https://en.wikipedia.org/wiki/Domain-specific_language). Master every step of the compilation pipeline, from lexing to semantic analysis, with full control and clarity.*

 - Build **interpreters** and **compilers** from scratch, without leaving the **Python's ecosystem**
 - Keep total control of what's going on at every step
 - Build **fast and easy** with python for prototyping and debugging
 - Compile and get more speed with cython

> ## What is PyLGEN?

[PyLGEN](https://pypi.org/project/pylgen-core/#description) is a toolbox for building **interpreters and compilers** from scratch, without leaving the [Python](https://www.python.org/) ecosystem. It's not a magical code generator, it's a cohesive set of modules that guide you through every stage: from lexical analysis to semantic evaluation, including [**LALR(1)**](https://en.wikipedia.org/wiki/LALR_parser) parsing and **Abstract Syntax Tree (AST)** construction.

> **TL;DR:** PyLGEN is a powerful Python-native toolkit for creating fast interpreters, compilers, and DSLs. It gives you complete control over the compilation process, from lexical analysis to AST evaluation, and is optimized with Cython for near-C performance. Ideal for students, software engineers, and anyone exploring compiler theory. Explore the complete source code, open issues, and contribute on [GitHub](https://github.com/yonyuk/pylgen).

<hr>

> ## Why PyLGEN?

*What makes PyLGEN different from other parser generators or compiler frameworks?*

 - **Prototype fast, optimize smart**: Write your entire language logic in pure python first. Only when performance becomes critical, compile your critical path with [Cython](https://cython.org/#:~:text=Cython%20is%20an%20optimising%20static,and%20C%20to%20let%20you).
 - **Full visibility, zero magic**: See exactly what happens at each stage. You build your own **ASTs**, define your own visitors, and control traversal order. There are no hidden transformations, you own the pipeline.
 - **Enterprise-ready parsing**: A robust LALR(1) engine with built-in conflict detection and ***panic-mode error recovery*** means  your **DSL** handles real-world, messy input without falling over.
 - **Instant visual feedback**: Turn your **automata, ASTs** and **parse trees** into interactive HTML graphs with a single command. Debug visually, not just via logs, a game changer for understanding and teaching.
 - **Feels like Python**: No weird configuration files, no custom DSLs for your grammar. Just Python code, all the way down. Use your favorite libraries, test with pytest, and deploy as a standard package.

> ## Philosophy: Clarity and control

Building a language should be **fun, educational and productive**. That's why PyLGEN focuses on:

 - **Transparency**: No black boxes. Every step, from token definitions to AST visitation, is under your control.
 - **Python native**: Write your logic in pure Python, leverage its ecosystem, and debug just as you always do.
 - **Performance on demand**: The framework's core is optimized in Cython, giving you significant speedups. And if you need more, you can compile your own extensions in Cython to squeeze out every last drop of performance.

> ## What you get out of the box

 -  **A lexer that does the job**: Define tokens with regex, set priorities, and attach semantic validation rules, straightforward control, no hidden surprises.
 - **A parser that tells you when things go wrong**: Build attributed grammars with reducers that produce ASTs directly. Conflict detection and panic-mode recovery keep you informed and in charge.
 - **Semantic analysis on your terms**: Walk the AST with visitors and traversal strategies you define. Maintain a context manage runtime errors, and keep your logic clean.

> ## Who is it for?

 - **Students and teachers**: PyLGEN follows the classic compiler course flow, but with hands-on approach.
 - **Software engineers**: Need a DSL for your product, an advanced configuration language, or a code analysis tool? PyLGEN gives you the power and flexibility you need without locking you into monolithic generators.
 - **Curious explorers**: Always wanted to know how a compiler works under the hood? Here's a perfect playground to experiment.


> ## Intention

PyLGEN has the intention to be the **meeting point** between classic compiler theory and modern software engineering practice. It's not trying to be the only framework or the fastest in every case, but to be the one that lets you **understand, modify, and optimize** every piece with confidence.

> ## Where to Go Next?

 - **[Quick Start Guide](section-1/quick_start.md):** Get started building your first interpreter in minutes.
 - **[Benchmark: PyLGEN vs Lark](benchmark/benchmark-conclusion.md):** See how PyLGEN outperforms other tools in real-world tests.
 - **[Architecture Deep Dive](api/intro.md):** Understand the modular design and each component of the framework.
 - **API Reference:** Explore the details of the [`automaton`](api/automaton/intro.md), [`grammar`](api/grammar/intro.md), [`parser`](api/parser/parser.md), and other modules.
 - **[GitHub Repository](https://github.com/yonyuk/pylgen):** Star the project, report issues, and explore the source code.
 - **[Examples](https://github.com/yonyuk/pylgen/tree/master/examples):** See practical examples of using PyLGEN to build interpreters and DSLs.