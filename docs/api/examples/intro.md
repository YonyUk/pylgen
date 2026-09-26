# Examples: Building a Lexer and Parser from Scratch

Welcome to the construction site. In the previous sections, we explored each module of PyLGEN in isolation: the [`automaton`](../automaton/intro.md) module gave us finite automata, the [`regex`](../regex/regex.md) engine turned patterns into DFAs, the [`lexer`](../lexer/lexer.md) module provided a scanning engine, and the [`parser`](../parser/parser.md) module offered a complete LALR(1) parser generator. We also saw how the convenience classes (`Lexer`, `ParserBuilder.build_parser`) make short work of building a language pipeline.

But there is a difference between driving a car and understanding what happens under the hood. This section is about the latter. We will build a lexer and a parser from scratch, using only the raw API components, exposing every stage of the compilation pipeline without hiding anything. By the end, you will understand exactly how PyLGEN transforms a stream of characters into a structured AST, and you will have the knowledge to customize, extend, or debug any part of the process.

This is the **pedagogical path**. It is more verbose than using the high-level classes, and that is precisely the point. We are trading convenience for comprehension.

## Why Build from Scratch?

PyLGEN is designed with a pedagogical philosophy: every stage of the compilation pipeline is exposed, documented, and accessible. There are no black boxes. The `Lexer` class, for example, is a convenience wrapper around `BaseLexer`, which in turn uses the `automaton` and `regex` modules. By building from scratch, we peel back each layer and see exactly how the pieces fit together.

This approach offers several benefits:

 - **Deep understanding**: You will see how DFAs are combined, how LR(0) states are computed, and how `ACTION`/`GOTO` tables drive the parsing process.

 - **Customization**: When the convenience classes do not fit your needs, you will know which lower-level methods to call.

 - **Debugging**: When something goes wrong, you will be able to trace the problem to its source, whether it is a malformed automaton, an ambiguous grammar, or a misconfigured reductor.

 - **Confidence**: You will no longer treat the framework as magic. You will know exactly what it does and why.

## The Compilation Pipeline

Before we start building, let us recall the stages of the compilation pipeline that we will be constructing:

| **Stage** | **Input** | **Output** | **Module** |
| :---: | :---: | :---: | :---: |
| **Lexical Analysis** | **Character stream** | **Token stream** | **`lexer`** |
| **Syntactic Analysis** | **Token stream** | **Abstract Syntax Tree** | **`parser`** |
| **Semantic Analysis** | **Abstract Syntax Tree** | **Annotated AST** | **`analysis`** |

In this section, we will focus on the first two stages. We will build a lexer that recognizes a simple arithmetic language, and a parser that constructs an AST from the token stream. Along the way, we will use the `automaton`, `regex`, `grammar`, `parser`, and `common` modules directly.