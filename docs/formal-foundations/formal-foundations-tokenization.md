# Tokenization Theory

A lexer is essentially a **deterministic finite automaton** that operates over the input character stream. This page covers the formal model behind tokenization: maximal munch, the combined DFA, and the linear-time scanning algorithm.

## The Formal Model

Let $\Sigma$ be the input alphabet (e.g., ASCII characters). Foreach token type $t$, we have a regular language $L_t \subseteq \Sigma^*$. The lexer, given a position in the input, must find the longest prefix $w$ that belongs to some $L_t$ (respecting priority in case of ambiguity). It returns a token $\lparen t,w \rparen$ and advances the position by $|w|$. If no $L_t$ matches, a lexical error is reported.

This is exactly the behavior of a **maximal munch** lexer.

## Maximal Munch

The maximal munch algorithm is the standard strategy for tokenization. It says: at each position in the input, find the longest prefix that matches any token pattern. If two patterns match the same length, the one with the higher priority wins.

To implement this naively, we need a DFA for each token pattern. Then, at each position, we ask each DFA: ***"What is the longest prefix of the remaining input that you accept?"*** The DFA that gives the longest answer wins.

> ### Notes on Complexity

A complete explanation and implementation of this is provided in the [**Building a Lexer from scratch**](../tutorials/foundations/tutorials-foundations-building-a-lexer.md) section.

> ### Why This Matters

The difference between the naive algorithm and the combined DFA is the difference between a toy and a production tool. PyLGEN's `BaseLexer` implements the combined-DFA approach. When you call `Lexer.initialize()`, you're building the union, determinizing, completing, and minimizing a DFA. The result is a scanner that runs in linear time, regardless of how many token patterns you define.