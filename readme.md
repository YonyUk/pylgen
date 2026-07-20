# PyLGEN
![PyPI - 0.3.5](https://img.shields.io/pypi/v/pylgen)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/yonyuk/pylgen/ci.yml)
![PyPI - 3.8](https://img.shields.io/pypi/pyversions/pylgen)
![PyPI - LICENSE](https://img.shields.io/pypi/l/pylgen)

![Codecov](https://img.shields.io/codecov/c/github/yonyuk/pylgen)

*From prototype to production: a **Python-native compiler framework** that brings the "**Dragon Book**" to life in Python, with clarity throughout.*

 - Build **interpreters** and **compilers** from scratch, without leaving the **Python's ecosystem**
 - Keep total control of what's going on at every step
 - Build **fast and easy** with python for prototyping and debugging
 - Compile and get more speed with cython

> [!NOTE]
> **Cython compilation** requires a **C** compiler installed on system to compile the code

> ## Summary
 - [🚀 Installation](#-installation)
 - [📖 Minimal example](#-minimal-example)
 - [🧬 Architecture](#-architecture)

> ## 🚀 Installation

### Fast installation with pip

***PyLGEN*** is a python library, so can be installed via ***pip install*** command

```bash
pip install pylgen
```

### Install from source code

 - Download the source code.
 - Install all build's dependencies.
```bash
pip install -r requirements.txt
```
 - In the root folder, run this command for a local installation
```bash
python setup.py build_ext --inplace
```

> ## 📖 Minimal example

You can find examples of how to use ***pylgen*** in <-link-to-the-minimal-example->

> ## 🧬 Architecture

***PyLGEN*** is a collection of Python modules featuring a high-performance core written in Cython. Together, they offer comprehensive tools for constructing interpreters and compilers from scratch, all while maintaining full compatibility with the broader Python ecosystem

 - [`🔎 pylgen.analisis`](#-analisis)
 - [`🤖 pylgen.automaton`](#-automaton)
 - [`🧱 pylgen.common`](#-common)
 - [`📚 pylgen.grammar`](#-grammar)
 - [`📚 pylgen.lexer`](#-lexer)
 - [`📚 pylgen.parser`](#-parser)
 - [`📚 pylgen.regex`](#-regex)
 - [`📉 pylgen.visual`](#-visual)

### 🔎 analisis

Provides the essential infrastructure for **semantic analysis, validation, and execution** of languages built with ***pylgen***. It bridges the gap between raw syntax (**ASTs**) and meaningful behavior

> #### Core Components
 - `Context`: Provides a base class with basic behavior, designed to be extended by users. Its purpose is to manage global state (variables,functions,scopes,errors,stacks,etc.) across AST traversals.
 - `ASTVisitor`: Base class for each specific AST node type visitor.
 - `TraversalStrategy`:  Defines an interface for every traversal strategy.
 - `ASTWalker`: Base class for an AST walker.
 - `LexicError,SintaxError,SemanticError`: Base errors implementations for each phase of code analysis.
 - `RuntimeError`: Base class for every error raised in run time.
 - `LexicRule`: Abstraction for a lexical rule. Used in ***pylgen.lexer*** module to define rules for ***Token*** pylgen's objects.

### 🤖 automaton

Provides the **core finite automata infrastructure** for pattern matching, forming the bedrock of the lexer and lexical analysis pipeline. It bridges regular expressions to executable state machines

> #### Core capabilities
 - `Automaton Construction`: Provides several ways for DFAs and NFAs constructing, and support for standard operations: ***union*** ( | ), ***concatenation*** ( . ), and ***Kleene star*** ( * )
 - `Determinization and Minimization`: Transforms NFAs to DFAs ( ***to_deterministic()*** ) and minimizes them ( ***minimize()*** ) to produce the most efficent tokenization engine, drastically reducing state count and lookup overhead. 

### 🧱 common

Provides the ***core data types*** that are shared across all modules of the framework, forming the common language that ties parsing,analysis, and code generation together

> #### Core types
 - `Symbol`: Represents grammar symbols ( both terminals and non-terminals ). Used throughout the grammar definition, parser, tables, and AST nodes.
 - `AST`: The abstract base class for all ***Abstract Syntax Tree*** nodes. Every AST node inherits from it and stores its symbol, source location ( line/column ), and provides a ***children()*** method to get its children nodes.
 - `Token`: Encapsulates lexical tokens, carrying the token type, text, symbol, and position information. Used by the lexer and parser.
 - `ASTListView`: A ligthweight, read-only view over a list of AST nodes, passed to reductor functions during parsing to build the AST from production reductions.

### 📚 grammar

Provides the ***formal language definition framework*** that underpins the entire parsing pipeline. It bridges context-free grammar ( CFG ) specification to executable LR parser tables, with native support for attributed productions that build Abstract Syntax Trees ( ASTs ) directly during parsing, and provides basic utilities to work with context-free grammars.

> #### Core Components
 - `Production`: A rule (***head -> production(list of symbols)***)
 - `ProductionsSet`: A container for all productions sharing the same head
 - `Grammar`: The base class storing start symbol, end-of-input marker, and all productions.
 - `AttributedGrammar`: Extends ***Grammar*** by associating a reductor function ( ***ASTListView -> AST*** ) with each production. This is the core for AST construction during parsing.

> #### Key Features
- `Intuitive API`: Define productions in a Pythonic style
```python
# E,T,plus must be instances of Symbol class

# AttributedGrammar
G[E] += (E,plus,T),binary_reductor
G[E] += (T,),single_reductor

# Basic Grammar
G[E] += E,plus,T
G[E] += T,
```

### 📚 lexer

Provides a ***flexible and efficient lexical analysis framework*** that transforms raw source code into a stream of tokens, ready for parsing. It combines regex-based pattern with automata theory to deliver both correctness and performance.

> #### Core components
 - `Lexer`: The main class that manages token definitions, input text, and token streaming. Extends ***BaseLexer*** with error handling, rule management, and adds tokens definition from regular expressions.
 - `BaseLexer`: The foundational class that handles the automaton-based scanning, with DFA-driven token matching and the ability to skip ignored patterns.

> #### Key features
 - `Regex-Based Pattern Definition`: Define tokens with standard regex strings, automatically compiled into efficent automata:
```python
lexer[0,TokenTypeEnum.INTEGER] = r'\d+'
lexer[1,TokenTypeEnum.FLOAT] = r'\d*\.\d+'
```
 - `Prioritized Matching`: Tokens are matched in the order they are added, allowing disambiguation of overlapping patterns.
 - `Custom Symbol Mapping`: A user-provided function ( ***get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol*** ) maps token types and texts to Symbol objects, enabling tight integration with the grammar.
 - `Ignore Patterns`: Automata for ignored characters ( ***whitespaces,comments*** ) can be supplied to skip irrelevant input.
 - `EOF Handling`: Explicit token for end-of-file with configurable type and symbol. 

### 📚 parser

Provides a **production-ready LALR(1) parser framework that transforms** token streams into ***Abstract Syntax Trees ( ASTs )*** through attributed grammar reductions. It bridges grammar definitions and AST construction with both performance and flexibility.

> #### Core components
 - `Parser`: Base class for every parser.
 - `BottomUpParser`: The main parser class that executes **LALR(1)** parsing on a token stream, invoking reductors to build **AST** nodes during each reduction.
 - `ParserBuilder`: A utility that consumes an ***AttributtedGrammar ( from pylgen.grammar )*** and generates the **LALR(1)** parsing tables **( ACTION/GOTO )** and the associated automaton.
 - `ParseTreeNode`: A parse tree for represents the concrete syntax tree ( optional, for debugging ), representing each production reduction.

> #### Key features
 - `LALR(1) Parsing`: Standard algorithm that handles most context-free grammars, with conflict detection ( ***shift/reduce, reduce/reduce*** ).
 - `Error Handling`: Collects syntax errors with line/column information.
 - `Parser State`: Supports resetting the parser for interactive **REPL** environments.

### 📚 regex

### 📉 visual