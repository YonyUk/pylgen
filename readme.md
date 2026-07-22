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

> [!note]
> **Cython compilation** requires a **C** compiler installed on system to compile the code

> ## Summary
 - [:rocket: Fast Installation](#-fast-installation)
 - [:book: Minimal example](#-minimal-example)
 - [Architecture](#-architecture)


> ## :rocket: Fast Installation

### :package: Fast installation with pip

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

> ## :book: Minimal example

You can find examples of how to use ***pylgen*** in <-link-to-the-minimal-example->

> ## Architecture

***PyLGEN*** is a collection of Python modules featuring a high-performance core written in Cython. Together, they offer comprehensive tools for constructing interpreters and compilers from scratch, all while maintaining full compatibility with the broader Python ecosystem

 - [`🔎 pylgen.analysis`](#-analysis)
 - [`🧱 pylgen.common`](#-common)
 - [`🤖 pylgen.automaton`](#-automaton)
 - :books: [`pylgen.grammar`](#-grammar)
 - :books: [`pylgen.lexer`](#-lexer)
 - :books: [`pylgen.parser`](#-parser)
 - :books: [`pylgen.regex`](#-regex)
 - [`📉 pylgen.visual`](#-visual)

### 🔎 analysis

Supplies the essential foundation for **semantic analysis, validation, and execution** of languages built with ***pylgen***. It bridges the gap between raw syntax (the **AST**) and meaningfull program behaviour 

> #### Core Components
 - `Context(abstract base class)`: Manages global state during **AST** traversal: 
> [!important]
`push_new_scope,pop_scope,clear_runtime_errors,add_runtime_error` and `get_runtime_errors` must be implemented by users.
 - `Error and its subclasses (LexicalError,SyntaxError,SemanticError)`: A hierarchy for errors that occur during lexical, syntactic, and semantic analysis. All inherit from `Error`, which includes line, column, a descriptive message, and categorisation via the `ErrorType` enum.
 - `RuntimeError`: Represents errors that happen during program execution. It includes a stack trace to aid debugging.
 - `LexicalRule`: An abstraction to defining validation rules on tokens. Used in `pylgen.lexer` module to check token properties. The `check` method returns a `LexicalError` if the rule is violated, or `None` otherwise.
 - `ASTVisitor(abstract class)`: Defines the contract for visitors that operate on `AST` nodes. Each visitor must implement `visit(ast,context)`, where it can inspect or modify the node and the context.
 - `ASTChildrenSelector(abstract class)`: Specifies which children (or the node itself) should be considered during traversal, and in what order. It is used by the traversal strategy to determine the next node to visit.
 - `TraversalStrategy(asbtract class)`: Defines the interface for traversal strategies (e.g. depth-first, breadth-first, custom-order). Key methods: `init(root),has_next(),current(context)` and `reset()`.
> [!important]
The interface does not explicitly define where the iterator's advance mechanism should be implemented; this responsibility is left to the developer.
 - `ASTWalker`: Orchestrates the **AST** traversal by combining a `TraversalStrategy` with a collection of `ASTVisitor` instances associated with specific node types. During `walk(ast)`, it iterates over nodes according to the strategy and applies the corresponding visitor (or a default visitor if it was supplied and none visitor was registered for a node type).

### 🧱 common

Provides the ***core data types*** that are shared across all modules of the framework, forming the common language that ties parsing,analysis, and code generation together

> #### Core types
 - `Symbol`: Represents grammar symbols ( both terminals and non-terminals ). Used throughout the grammar definition, parser, tables, and AST nodes.
 - `AST`: The abstract base class for all ***Abstract Syntax Tree*** nodes. Every AST node inherits from it and stores its symbol, source location ( line/column ), and provides a ***children()*** method to get its children nodes.
 - `Token`: Encapsulates lexical tokens, carrying the token type, text, symbol, and position information. Used by the lexer and parser.
 - `ASTListView`: A ligthweight, read-only view over a list of AST nodes, passed to reductor functions during parsing to build the AST from production reductions.

### :robot: automaton

Provides the **core finite automata infrastructure** for pattern matching, forming the bedrock of the lexer and lexical analysis pipeline. It efficiently bridges regular expressions to executable state machines.

> #### Core capabilities
 - **Automaton Construction**: Provides several factory methods to build DFAs and NFAs, supporting standard regular language operations out-of-the-box, including **union** ( `|` ), **concatenation** ( `.` ), **intersection** ( `&` ), and **Kleene star** ( `*` ).
 - **Determinization and Minimization**: Transforms NFAs to DFAs via the `to_deterministic()` method and applies **Hopcroft's algorithm** for DFA minimization (`minimize()`). This yields an extremely efficient tokenization engine, drastically reducing state count and lookup overhead.

> #### Usage

 - #### Creating a DFA explicitly

```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

# create the states
q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the transition table
table = Table()
# q0 -- 0 --> q1
table['q0','0'] = 'q1'
# q0 -- 1 --> q0
table['q0','1'] = 'q0'
# q1 -- 0 --> q1
table['q1','0'] = 'q1'
# q1 -- 1 --> q0
table['q1','1'] = 'q0'

# create the dfa

aut = create_dfa({q0,q1},table,'q0',{'0','1'})
```

 - #### Creating a DFA incrementally
```python
from pylgen.automaton import DFA,State

aut = DFA('q0','q0',{'0','1'})

# gets the start state
q0 = aut.start_state
# creates a new state
q1 = State('q1','q1',True)

# adds transitions
aut.add_transition(q0,q1,'0')
aut.add_transition(q0,q0,'1')
aut.add_transition(q1,q1,'0')
aut.add_transition(q1,q0,'1')
```
> [!tip]
 `1` - Alternatively, this can be done this way:
```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the dfa
aut = create_dfa({q0,q1},Table(),'q0',{'0','1'})

# adds transitions
aut.add_transition(q0,q1,'0')
aut.add_transition(q0,q0,'1')
aut.add_transition(q1,q1,'0')
aut.add_transition(q1,q0,'1')
```
> [!tip]
 `2` - More easily
```python
from pylgen.automaton import create_dfa,State
from pylgen.common import Table

q0 = State('q0','q0')
q1 = State('q1','q1',True)

# create the dfa
aut = create_dfa({q0,q1},Table(),'q0',{'0','1'})

# adds transitions
aut += q0,'0',q1
aut += q0,'1',q0
aut += q1,'0',q1
aut += q1,'1',q0
```

### :books: grammar

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

### :books: lexer

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

### :books: parser

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

### :books: regex

Provides a **complete regular expression engine**, its purpose is to offer a unified interface for:
 - Converting a regular expression **as string** into a deterministic finite automata ( ***DFA*** ).
 - Obtaining an equivalent regular grammar from an automata.
 - Generating a regular expression from an automata.

> #### Key features
 - `Regular expression parsing`: Supports clasic regex syntax: concatenation ( | ), repetition ( *, +, ? ), groups ( (...) ), character classes ( [...] ) with ranges and negation, and bounded quantifiers ( {m,n} ).
 - `Conversion to DFA`: The regular expression is parsed into an ***AST***, semantically validated, and then converted into a minimized ***DFA***, ready for string recognition.
 - `Regular grammar generation`: From an automata, obtains a regular grammar that generates exactly the same language.
 - `Regular expression generation`: From an automata, infers an equivalent regular expression

### 📉 visual

Provides interactive graph visualization tools for automata, lexer, **abstract syntax trees (ASTs)**, and parse trees. It leverages **pyvis** to generate standalone **HTML files with embedded resources (CSS/JS)** for offline use. 

> #### Key features
 - `Render automata`: draw an interactive directed graph representing the given automata, with transition labels, accepting states, and ε-transitions.
 - `Visualize the DFA derived from a lexer`
 - `Render AST`: Display **ASTs** as hierarchical trees with node attributes.
 - `Render Parse Trees`: Display **Parse Trees** as hierarchical trees from a ***Parser*** object.
 - `Cache`: Optional caching of external resources (stylesheets and scripts) to avoid repeated downloads.
 - `Sharing`: Export to self-contained HTML files

> #### Usage

#### Setting the cache file

To enable resource caching, specify a cache file path before generating HTML files:

```python
from pylgen.visual import set_cache_file

set_cache_file('vis_cache.pkl')
```

> [!note]
If the cache file path already exists, it will be loaded and updated if necessary, otherwise a new one is created

#### Drawing an automaton

```python
from pylgen.visual import draw_automaton

# ... code to create the automaton

draw_automaton(automaton, 
               filename="my_automaton",
               show=True,
               cache=True,
               physics=False,
               select_menu=False,
               filter_menu=False,
               nodes=False,
               edges=False,
               as_tree=False)

```

#### Drawing a lexer

```python
from pylgen.visual import draw_lexer

# ... code to build the lexer

draw_lexer(lexer, 
               filename="my_automaton",
               show=True,
               cache=True,
               physics=False,
               select_menu=False,
               filter_menu=False,
               nodes=False,
               edges=False,
               as_tree=False)
```

> [!note]
This is a convenience wrapper that calls `draw_automaton(lexer.dfa,**kwargs)`.

#### Drawing an **AST**

```python
from pylgen.visual import draw_ast

# ... code to build the ast

draw_ast(ast_root, 
         filename="ast",
         show=True,
         cache=True,
         physics=False,
         select_menu=False,
         filter_menu=False,
         nodes=False,
         edges=False)
```

#### Drawing a **Parse Tree**

```python
from pylgen.visual import draw_parse_tree_from_parser

# ... code to build the parse tree

draw_parse_tree_from_parser(parser, 
                            filename="parse_tree",
                            show=True,
                            cache=True,
                            physics=False,
                            select_menu=False,
                            filter_menu=False,
                            nodes=False,
                            edges=False)
```

Nodes are labelled with the grammar symbol

> [!note]
`draw_parse_tree_from_parser` uses the `Parser`'s internal parse tree, so the `Parser.set_draw_parse_tree_flag(True)` must be called before the parsing to build the **Parse Tree**.

#### API details

| kwarg | type | description | `draw_automaton` | `draw_lexer` | `draw_ast` | `draw_parse_tree_from_parser` |
|:---:| :---: | :--- | :---: | :---: | :---: | :---: |
| filename | `str` | specifies the name of the HTML file generated | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| show | `bool` | specifies if the file will be opened after creating | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| cache | `bool` | specifies if the cache file will be used to generate the file | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| physics | `bool` | enables the physics options in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| select_menu | `bool` | enables selecting menu in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| filter_menu | `bool` | enables filtering menu in the interactive graphics | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| nodes | `bool` | enables nodes options, see **pyvis**'s official documentation for more information | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| edges | `bool` | enables edges options, see **pyvis**'s official documentation for more information | :white_check_mark: | :white_check_mark: | :white_check_mark:| :white_check_mark: |
| ast_tree | `bool` | displays the graph as a tree | :white_check_mark: | :white_check_mark: | :x:(default) | :x:(default) |