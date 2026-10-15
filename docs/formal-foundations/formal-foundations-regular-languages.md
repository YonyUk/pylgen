# Regular Expressions and Kleene's Theorem

[Regular expressions](https://en.wikipedia.org/wiki/Regular_expression) are the ***lingua franca*** of pattern matching. They provide a concise, declarative way to describe sets of strings, and they are the foundation upon which lexical analyzers are built. This page covers the formal model behind PyLGEN's regex engine.

## Kleene Algebra

At its core, the regex module implements the [**Kleene algebra**](https://en.wikipedia.org/wiki/Kleene_algebra) of regular expressions. A regular expression over an alphabet $\Sigma$ is defined inductively:

 - **Empty Language**: $\varnothing$ (matches nothing).
 - **Empty String**: $\epsilon$ (matches the empty string).
 - **Single Symbol**: $a$ for $a \in \Sigma$ (matches the symbol $a$).
 - **Union**: $R$ $|$ $S$ (matches either $R$ or $S$).
 - **Concatenation**: $RS$ (matches $R$ followed by $S$).
 - **Kleene Star**: $R^*$ (matches zero or more repetitions of $R$).

> ### Kleene's Theorem

By **Kleene's theorem**, every regular expression has an equivalent finite automaton (DFA or NFA), and every finite automaton corresponds to a regular expression. The three formalisms (regular expressions, finite automata, and regular grammars), are all equivalent in expressive power.

PyLGEN implements constructive proofs of this theorem:

 - **Regex → Automaton**: builds an NFA using a construction method equivalent to the **standard Thompson construction** (with $\epsilon$‑transitions), then determinizes and minimizes it.

 - **Automaton → Regex**: The module implements the **state elimination algorithm** (also known as the [**Brzozowski‑McCluskey method** or **Arden's lemma**](https://en.wikipedia.org/wiki/Arden%27s_rule)) to derive a regular expression from a DFA.

## Regular Grammars

A grammar is **regular** if all productions have one of the following forms:

 - **Right-linear**: $A \rightarrow a$ or $A \rightarrow aB$.
 - **Left-linear**: $A \rightarrow a$ or $A \rightarrow Ba$.

By converting such grammars to automata and vice versa, the module provides a complete translation between the three formalisms: regex, automata, and regular grammars.

## The Three-Way Equivalence

| **Formalism** | **Recognizes** | **Conversion** |
| :---: | :---: | :---: |
| **Regular Expression** | **Regular languages** | **↔ Automaton, ↔ Grammar** |
| **Finite Automaton (DFA/NFA/hybrid)** | **Regular languages** | **↔ Regex, ↔ Grammar** |
| **Regular Grammar** | **Regular languages** | **↔ Automaton, ↔ Regex** |

All three are computationally equivalent. The choice of which to use depends on the task:

 - Regex is concise and human-readable, ideal for specifying token patterns.

 - Automata are executable and efficient, ideal for scanning.

 - Regular grammars integrate with the rest of the grammar-based tooling.