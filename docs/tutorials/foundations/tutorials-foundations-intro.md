# Foundations

Before you build a language, it helps to know what's happening underneath. The **Foundations** tutorials take the core pieces of the compilation pipeline (the lexer and the parser) and build them from scratch, using only PyLGEN's low-level API. No `Lexer`, no `ParserBuilder.build_parser`, no hidden machinery. Just the algorithms and the data structures, exposed for you to inspect, modify, and understand.

This is the path for anyone who wants to know why a lexer is fast, how an LR parser decides what to do, or what a DFA actually looks like when it's recognizing your tokens. It's also the path that connects PyLGEN to the classic compiler literature: if you've read the Dragon Book, or you're taking a course on compiler construction, this is where the theory meets the code.