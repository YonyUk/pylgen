# `pylgen.regex` Module (The Regular Expression Engine)

Regular expressions are the *lingua franca* of pattern matching. They provide a concise, declarative way to describe sets of strings, and they are the foundation upon which lexical analyzers are built. The `regex` module in PyLGEN is a complete, standalone regular expression engine that bridges the gap between regex patterns, finite automata, and context‑free grammars.

This module is unique in the PyLGEN ecosystem: it is the only one that ingests a string (the regex pattern) and produces an executable artifact (a DFA) without requiring manual grammar definition. It does this by embedding a full parser for regular expressions, complete with its own lexer, grammar, AST, and semantic evaluator. The result is a powerful, self‑contained engine that can:

 - Parse a regex string into an AST.

 - Evaluate the AST to construct an NFA or DFA.

 - Convert between automata and regular grammars.

 - Extract a regex string from a given automaton (regex synthesis).

In this section, we will explore the architecture, API, and internal workings of this module, showing how it integrates the concepts from the [`automaton`](../automaton/intro.md) and [`grammar`](../grammar/intro.md) modules to provide a seamless **regex‑to‑automaton pipeline**.

## Purpose in the Framework

The `regex` module serves three primary roles:

 - **`1` [Lexer](../lexer/lexer.md#code-examples) Foundation**: The lexer uses this module internally to convert token patterns (provided as regex strings) into DFAs that can efficiently scan input text.

 - **`2` Standalone Regex Engine**: You can use it independently to parse and evaluate regular expressions, obtain their equivalent automata, or even generate a regex from an automaton (useful for debugging or minimization).

 - **`3` Grammar $\leftrightarrow$ Automaton Bridge**: The module provides methods to convert a regular grammar into an equivalent automaton and vice versa, completing the circle of equivalence established by Kleene's theorem.

This modularity means you can use the regex engine even if you don't need a full lexer or parser, it's a self‑contained tool for any application that requires pattern matching or automata manipulation.

## Formal Foundations: Regular Expressions and Automata

At its core, the regex module implements the **Kleene algebra** of regular expressions. A regular expression over an alphabet $\Sigma$ is defined inductively:

 - **Empty Language**: $\varnothing$ (matches nothing).
 - **Empty String**: $\epsilon$ (matches the empty string).
 - **Single Symbol**: $a$ for $a \in \Sigma$ (matches the symbol $a$).
 - **Union**: $R$ $|$ $S$ (matches either $R$ or $S$).
 - **Concatenation**: $RS$ (matches $R$ followed by $S$).
 - **Kleene Star**: $R^*$ (matches zero or more repetitions of $R$).

By **Kleene's theorem**, every regular expression has an equivalent finite automaton (DFA or NFA), and every finite automaton corresponds to a regular expression. The `regex` module implements constructive proofs of this theorem:

 - **Regex → Automaton**: builds an NFA using a construction method equivalent to the **standard Thompson construction** (with $\epsilon$‑transitions), then determinizes and minimizes it.

 - **Automaton → Regex**: The module implements the **state elimination algorithm** (also known as the **Brzozowski‑McCluskey method** or **Arden's lemma**) to derive a regular expression from a DFA.

The module also supports **regular grammars**: a grammar is regular if all productions have the form $A \rightarrow a$ or $A \rightarrow aB$ (right-linear), or $A \rightarrow a$ or $A \rightarrow Ba$ (left-linear). By converting such grammars to automata and vice versa, the module provides a complete translation between the three formalisms: regex, automata, and regular grammars.

## Core Classes

> ### `RegexParsingException`

Exception raised when the regex parser encounters errors during lexical or syntactic analysis.

> ### `RegexEngine` (The Main Interface)

`RegexEngine` is a static class that provides the primary API for working with regular expressions. All methods are stateless and thread‑safe.

#### Static Methods

| **Method** | **Description** |
| :---: | :---: |
| **`Parse(re: str) -> DFA`** | Parses a regex string and returns an equivalent **minimized DFA**. This is the workhorse method: it handles lexing, parsing, AST evaluation, and automaton construction. Raises `RegexParsingException` on invalid input. |
| **`GetAutomaton(g: Grammar) -> DFA`** | Converts a **regular grammar** (left‑ or right‑linear) into an equivalent minimized DFA. Raises `ValueError` if the grammar is not regular. |
| **`GetGrammar(automaton: Automaton) -> Grammar`** | Converts an automaton (DFA or NFA) into an equivalent **regular grammar**. |
| **`GetRegex(automaton: Automaton) -> str`** | Derives a regular expression from the given automaton using the state elimination algorithm. |
| **`BuildRegexParser() -> Parser`** | Returns a LALR(1) parser for regular expressions. This is used internally but exposed for advanced use cases. |
| **`BuildRegexLexer() -> BaseLexer`** | Returns a lexer for regular expressions. Useful if you need to tokenize regex strings separately. |

## Grammar → Automaton Conversion

The `GetAutomaton(g: Grammar)` method converts a regular grammar into a DFA. It supports both left‑linear and right‑linear grammars. The method first checks if the grammar is regular, it then builds an NFA, determinizes it, and minimizes the result.

## Automaton → Grammar Conversion

The GetGrammar(automaton: Automaton) method converts a DFA or NFA into an equivalent **right‑linear grammar**. This conversion is useful for debugging, testing, or integrating with other grammar‑based tools.

## Automaton → Regex Synthesis

The `GetRegex(automaton: Automaton) -> str` method implements the state elimination algorithm, one of the most elegant results in automata theory.

## Code Examples

> ### Parsing a Regex into a DFA

=== "Python"

    ```python
    from pylgen.regex import RegexEngine

    # Parse a simple regex
    dfa = RegexEngine.Parse('a(b|c)*d')
    # dfa is a DFA that accepts strings like "ad", "abcd", "abbbccd", etc.

    # Test the DFA
    assert dfa.accept(['a', 'b', 'c', 'd'])  # True
    assert dfa.accept(['a', 'd'])            # True
    assert dfa.accept(['a', 'b', 'd'])       # True
    assert dfa.accept(['a', 'c', 'd'])       # True
    assert dfa.accept(['a', 'b', 'b'])       # False (missing final 'd')
    ```
=== "Cython"

    ```cython
    from pylgen.regex.engine cimport _parse
    from pylgen.automaton.automaton cimport DFA 

    # Parse a simple regex
    cdef DFA dfa = _parse('a(b|c)*d')
    # dfa is a DFA that accepts strings like "ad", "abcd", "abbbccd", etc.

    # Test the DFA
    assert dfa.accept(['a', 'b', 'c', 'd'])  # True
    assert dfa.accept(['a', 'd'])            # True
    assert dfa.accept(['a', 'b', 'd'])       # True
    assert dfa.accept(['a', 'c', 'd'])       # True
    assert dfa.accept(['a', 'b', 'b'])       # False (missing final 'd')
    ```

#### Supported Syntax

 - **Character classes**: `[abc]`, `[^abc]`, `[a-z]`.

 - **Predefined constants**: `\d`, `\D`, `\s`, `\S`, `\w`, `\W`, .

 - **Quantifiers**: `*`, `+`, `?`, `{min,max}`.

 - **Grouping**: `(regex)`.

 - **Escape special characters**: `\(`, `\)`, `\[`, `\]`, `\{`, `\}`, `\-`, `\*`, `\+`, `\?`, `\^`, `\|`, `\.`, `\,`.

> ### Converting a Regular Grammar to a DFA

Suppose you have a grammar that recognizes the language $a^*b$:

=== "Python"
    ```python
    from pylgen.common.types import Symbol
    from pylgen.grammar.grammar import Grammar
    from pylgen.regex import RegexEngine

    S = Symbol('S')
    A = Symbol('A')
    a = Symbol('a', True)
    b = Symbol('b', True)

    G = Grammar(S)
    G[S] += (a, S)   # S -> a S
    G[S] += (b,)     # S -> b

    dfa = RegexEngine.GetAutomaton(G)
    # dfa accepts strings like "b", "ab", "aab", etc.
    ```
=== "Cython"
    ```cython
    from pylgen.common.types cimport Symbol
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.regex.engine cimport _get_automaton
    from pylgen.automaton.automaton cimport DFA

    cdef Symbol S = Symbol('S')
    cdef Symbol A = Symbol('A')
    cdef Symbol a = Symbol('a', True)
    cdef Symbol b = Symbol('b', True)

    cdef Grammar G = Grammar(S)
    G._add_production(S,[a, S])   # S -> a S
    G._add_production(S,[b])     # S -> b

    cdef DFA dfa =_get_automaton(G)
    # dfa accepts strings like "b", "ab", "aab", etc.
    ```

> ### Deriving a Regex from an Automaton

=== "Python"

    ```python
    from pylgen.automaton.automaton import DFA, State
    from pylgen.regex import RegexEngine

    # Build a DFA for the language (a|b)*
    dfa = DFA('q0', None, {'a', 'b'}, True)  # start state is also final
    q0 = dfa.start_state
    dfa += q0, 'a', q0
    dfa += q0, 'b', q0

    # Get the regex
    regex = RegexEngine.GetRegex(dfa)
    print(regex)  # Output: (a|b)*
    ```
=== "Cython"
    ```cython
    from pylgen.automaton.automaton cimport DFA, State
    from pylgen.regex.engine cimport _get_regex

    # Build a DFA for the language (a|b)*
    cdef DFA dfa = DFA('q0', None, {'a', 'b'}, True)  # start state is also final
    cdef State q0 = dfa.start_state
    dfa.add_transition(q0, q0, 'a')
    dfa.add_transition(q0, q0, 'b')

    cdef str regex = _get_regex(dfa)
    print(regex)  # Output: (a|b)*
    ```

## Summary

The `regex` module is a testament to PyLGEN's self‑sufficiency: it implements a full regular expression engine from scratch, complete with its own lexer, parser, and automata algorithms. It provides a clean, efficient API that can be used both as a standalone tool and as the foundation for the lexer module. With it, PyLGEN provides a complete, consistent stack for language processing, from regular expressions and lexers to context‑free grammars and parsers. In the next module, we will explore the lexer itself, which builds upon this foundation to tokenize real source code.