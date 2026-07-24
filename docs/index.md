# PyLGEN

*From prototype to production: a **Python-native compiler framework** that brings the "**Dragon Book**" to life in Python, with clarity throughout.*

 - Build **interpreters** and **compilers** from scratch, without leaving the **Python's ecosystem**
 - Keep total control of what's going on at every step
 - Build **fast and easy** with python for prototyping and debugging
 - Compile and get more speed with cython

> ## What is PyLGEN?

PyLGEN is a toolbox for building **interpreters and compilers** from scratch, without leaving the Python ecosystem. It's not a magical code generator, it's a cohesive set of modules that guide you through every stage: from lexical analysis to semantic evaluation, including **LALR(1)** parsing and **Abstract Syntax Tree (AST)** construction.

> ## Why PyLGEN?

*What makes PyLGEN different from other parser generators or compiler frameworks?*

 - **`Prototype fast, optimize smart`**: Write your entire language logic in pure python first. Only when performance becomes critical, compile your critical path with Cython.
 - **`Full visibility, zero magic`**: See exactly what happens at each stage. You build your own **ASTs**, define your own visitors, and control traversal order. There are no hidden transformations, you own the pipeline.
 - **`Enterprise-ready parsing`**: A robust LALR(1) engine with built-in conflict detection and ***panic-mode error recovery*** means  your **DSL** handles real-world, messy input without falling over.
 - **`Instant visual feedback`**: Turn your **automata,ASTs** and **parse trees** into interactive HTML graphs with a single command. Debug visually, not just via logs, a game changer for understanding and teaching.
 - **`Feels like Python`**: No weird configuration files, no custom DSLs for your grammar. Just Python code, all the way down. Use your favorite libraries, test with pytest, and deploy as a standard package.

> ## Philosophy: Clarity and control

Building a language should be **fun,educational and productive**. That's why PyLGEN focuses on:

 - **`Transparency`**: No black boxes. Every step, from token definitions to AST visitation, is under your control.
 - **`Python native`**: Write your logic in pure Python, leverage its ecosystem, and debug just as you always do.
 - **`Performance on demand`**: The framework's core is optimized in Cython, giving you significant speedups. And if you need more, you can compile your own extensions in Cython to squeeze out every last drop of performance.

> ## What you get out of the box

 -  **`A lexer that does the job`**: Define tokens with regex, set priorities, and attach semantic validation rules, straightforward control, no hidden surprises.
 - **`A parser that tells you when things go wrong`**: Build attributed grammars with reducers that produce ASTs directly. Conflict detection and panic-mode recovery keep you informed and in charge.
 - **`Semantic analysis on your terms`**: Walk the AST with visitors and traversal strategies you define. Maintain a context manage runtime errors, and keep your logic clean.

> ## Who is it for?

 - **`Students and teachers`**: PyLGEN follows the classic compiler course flow, but with hands-on approach.
 - **`Software engineers`**: Need a DSL for your product, an advanced configuration language, or a code analysis tool? PyLGEN gives you the power and flexibility you need without locking you into monolithic generators.
 - **`Curious explorers`**: Always wanted to know how a compiler works under the hood? Here's a perfect playground to experiment.


> ## Intention

PyLGEN has the intention to be the **meeting point** between classic compiler theory and modern software engineering practice. It's not trying to be the only framework or the fastest in every case, but to be the one that lets you **understand, modify, and optimize** every piece with confidence.