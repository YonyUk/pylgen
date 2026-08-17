# `pylgen.automaton` Module (The Engine Pattern Matching)

Welcome to the `automaton` module, the mathematical powerhouse of PyLGEN. If the [`common`](../common/common.md) module provides the ***vocabulary*** of language processing, the `automaton` module provides the ***grammar***: it implements the finite automata theory that underpins lexical analysis, regular expression matching, and pattern recognition.

This module is where theory meets practice. Here, we implement **deterministic finite automata (DFAs) and nondeterministic finite automata (NFAs)**, complete with subset construction, [Hopcroft's minimization algorithm](https://en.wikipedia.org/wiki/DFA_minimization), and a rich set of set-theoretic operations: union, intersection, complement, concatenation, and Kleene star. These are the building blocks that allow the `lexer` module to turn regex patterns into efficient tokenization engines.

## Purpose in the Framework

The `automaton` module serves a dual role:

 - `1`. **Foundation for Lexical Analysis**: The lexer converts regex patterns (strings) into DFAs that can efficiently scan input text. This module provides the automata that make that possible.

 - `2`. **Standalone Tool for Language Manipulation**: Even if you never use the [lexer](../lexer/lexer.md#lexer-the-userfacing-lexer) or [parser](../parser/parser.md#parser-abstract-base-class), you can use this module to:
    - Build automata from scratch.

    - Perform operations on regular languages (union, intersection, etc.).

    - Test whether a string is accepted by a language.

    - Determine if a language is empty or infinite.

    - Minimize automata for optimal performance.

The module is designed to be both **correct** and **fast**, leveraging Cython to implement computationally intensive algorithms like determinization and minimization at near‑C speed.

Before we dive into the API, let's explore the mathematical theory behind this module to get better understanding of it.