# Formal Foundations

PyLGEN is a practical framework, but it doesn't hide its mathematics. Every module (the lexer, the regex engine, the parser) is a direct implementation of a well-known formal model. Understanding those models makes the framework predictable, debuggable, and extensible. It also lets you reason about why a grammar works, why a lexer is fast, and why a parser rejects an input.

This section collects the theory behind the framework. It's not a replacement for a compiler course, and it doesn't cover everything. It covers the parts you'll actually encounter when using PyLGEN:

 - **Automata theory**: the DFA and the hybrid ε-DFA, the two models that power the lexer.

 - **Regular languages**: Kleene's theorem, the equivalence between regex, automata, and regular grammars.

 - **Context-free grammars**: the formalism behind every parser in PyLGEN.

 - **LR parsing**: LR(0), SLR, LR(1), and LALR(1), the algorithms that build the parsing tables.

 - **Tokenization theory**: maximal munch, and why the lexer uses a single combined DFA.

You don't need to read this section to use PyLGEN. But if you've ever wondered what `Lexer.initialize()` does or why `ParserBuilder.build_parser_from_attributed` can fail with a conflict, this is where the answers live.

## How to read this section

Each page is self-contained, but they build on each other:

| **Page** | **Prerequisites** | **What it covers** |
| :---: | :---: | :---: |
| [**Automata**](./formal-foundations-automata.md) | `None`	| DFA, hybrid ε-DFA, acceptance, regular languages |
| [**Context-Free Grammars**](./formal-foundations-context-free-grammars.md) | `None` | CFG definition, derivations, language of a grammar |
| [**Regular Languages**](./formal-foundations-regular-languages.md) | **Automata** and **Context-Free Grammars** | Kleene algebra, Kleene's theorem, regex ↔ automaton |
| [**LR Parsing**](./formal-foundations-lr-parsing.md) | **CFG** | LR items, SLR, LR(1), LALR(1), lookahead propagation |
| [**Tokenization**](./formal-foundations-tokenization.md) | **Automata** | Maximal munch, combined DFA, linear-time scanning |