# From configuration file to JSON: the story of `idented_dsl`

## An everyday problem

Imagine you have to design a configuration format for an application. You could use [**JSON**](https://www.json.org), [**YAML**](https://yaml.org), [**TOML**](https://toml.io), or [**INI**](https://en.wikipedia.org/wiki/INI_file). Each has its advantages, but they all share one thing: the user writes text, and the application must understand it. The interesting question isn't *which* format to use, it's *how* you teach a machine to read it. And that is where PyLGEN comes into play.

`idented_dsl` is a small, indentation‑sensitive configuration language, similar to INI but with true nesting. It's compact enough to fit in a single sitting, yet rich enough to exercise every stage of the compiler pipeline. By the end of this walkthrough, you'll have seen how each piece is assembled: the lexer, the grammar, the reducers, the AST, code generation, and the CLI.

!!! note "Sources"
    The source code of the entire example can be found on the [github repository](https://github.com/YonyUk/pylgen/tree/master/examples/idented_dsl)

    [download source code<br>(idented_dsl)](https://download-directory.github.io/?url=https://github.com/YonyUk/pylgen/tree/master/examples/idented_dsl){ .md-button .md-button--primary style="text-align: center;"}

## The starting point: the configuration file

It all begins with text like this:

```yaml
[database]
    name: "mydatabase"
    host: "localhost"
    port: 5432

    -options:
        security_level:1
        onfail:"report"
        
    -extra:
        important: true

[users]

    max: 10
    min: 5

    - options:
        onfull:"denegate"
        overflow:"expulse"
```

At first glance, it looks like an INI file on steroids. There are sections in brackets, hyphenated subsections, key-value pairs, and indentation-based nesting. But look closely at the details: `security_level:1` has no space after the colon, `- options:` has a space after the hyphen, and `important: true` mixes a key with a boolean value. The language is lenient regarding spacing but strict about indentation. That combination is precisely what makes it interesting to parse.

## First stop: the indentation-aware lexer

Before there is grammar, there must be tokens. The `lexer.py` file constructs an `IndentedLexer`, the PyLGEN class specialized for languages ​​where indentation is significant.

The configuration is deliberately minimalist:

```python
from pylgen.common.enums import TokenType
from pylgen.common.types import Symbol
from pylgen.lexer.lexer import IdentedLexer

from .grammar_symbols import (
    newline,
    number,
    boolean,
    string,
    indent,
    dedent,
    variable
)

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'
    NEWLINE = 'NEWLINE'
    SYMBOL = 'SYMBOL'
    EOF = 'EOF'
    VARIABLE = 'VARIABLE'
    IDENTATION = 'IDENTATION'
    WHITESPACEMARKER = 'WHITESPACEMARKER'
    SINGLEWHITESPACE = 'SINGLEWHITESPACE'

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NEWLINE:
        return newline
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.BOOLEAN:
        return boolean
    if t == TokenTypeEnum.STRING:
        return string
    if t == TokenTypeEnum.IDENTATION:
        return indent
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    return Symbol(tx,True)

def sanitaze_text(text:str) -> str:
    lines = text.split('\n')
    lines = list(map(lambda line:line if not line.strip() == '' else '#ignore#', lines))
    return '\n'.join(lines)

lexer = IdentedLexer(get_symbol_function,'#ignore#\n?')
lexer.set_text_sanitize_function(sanitaze_text)
lexer[0,TokenTypeEnum.NUMBER] = r'\d+(\.\d+)?'
lexer[1,TokenTypeEnum.BOOLEAN] = 'true|false'
lexer[2,TokenTypeEnum.VARIABLE] = r'[a-zA-Z_]\w*'
lexer[3,TokenTypeEnum.IDENTATION] = '    |\t'
lexer[4,TokenTypeEnum.NEWLINE] = '\n'
lexer[5,TokenTypeEnum.SYMBOL] = r'\-|:|\[|\]'
lexer[6,TokenTypeEnum.STRING] = '".*"'
lexer[7,TokenTypeEnum.WHITESPACEMARKER] = '#ignore#\n'
lexer[8,TokenTypeEnum.SINGLEWHITESPACE] = ' '

lexer.set_ident(TokenTypeEnum.IDENTATION)
lexer.set_indent_symbol(indent)
lexer.set_dedent_symbol(dedent)
lexer.set_eof_token('$',TokenTypeEnum.SYMBOL)
```

Three things deserve attention.

 - First: `set_indent_symbol` and `set_dedent_symbol` instruct the lexer to emit `indent` and `dedent` tokens whenever the indentation changes. This means the grammar doesn't have to worry about counting spaces; it receives tokens that already signal *"a block starts here"* and *"it ends here."*

 - Second: `set_ident` specifies which token represents an indentation unit. In this case, it is `INDENTATION` with the pattern `'    |\t'`, four consecutive spaces or a tab. The lexer groups these tokens and compares their quantity across lines to decide whether to emit `indent` or `dedent`.

 - Third: `sanitize_function`. This function replaces empty lines with `#ignore#`, a marker the lexer disregards. Why? Because in an indentation-based language, a blank line could confuse the lexer, making it think the indentation level has changed. By substituting it with an ignorable token, the structure is preserved without introducing noise.

The tokens themselves are diverse: integers and floats, booleans (`true`/`false`), variables (`[a-zA-Z_]\w*`), quoted strings, symbols (`-`, `:`, `[`, `]`), and line breaks. There are no keywords; the language is so minimal that everything is distinguished by its form rather than by reserved words.

A design choice is evident here: the lexer does not attempt to be *"smart."* It has no concept of sections or atoms; it simply classifies characters and detects changes in indentation. The intelligence comes later, within the grammar.

!!! tip "The empty-line trick"

    In an indentation-sensitive language, the lexer needs to compare the indentation level of each line to decide when to emit `indent` and `dedent`. An empty line has no content, but it may have zero spaces or accidental spaces; if it were processed as a normal line, its indentation could be interpreted as an unexpected `dedent` (or a spurious `indent`) and break the block structure.

    Simply deleting empty lines is also problematic: it shifts `line` and `column` numbers, and it can alter the sequence of `newlines` that the lexer uses to delimit instructions. That is why they are replaced with a marker (`#ignore#`) that the lexer discards via the skip pattern (`'#ignore#\n?'`). This way the line still counts for position tracking, but it produces no tokens and does not interfere with the indentation logic.

    It is a simple but effective trick: it turns an empty line into an ignorable token, preserving the structure and preventing whitespace from contaminating the analysis.

## Second stop: the attributed grammar

The `grammar.py` file is the heart of the example. Here, the language structure is defined, and each production is associated with a function that constructs the AST.

The grammar has seven non-terminals:

 - `Config`: the root.

 - `ConfigSequence`: a sequence of sections.

 - `Section`: a section enclosed in brackets.

 - `SubSection`: a subsection marked with a hyphen.

 - `SectionConfigSequence`: the content within a section or subsection.

 - `ConfigAtom`: a key-value pair.

And the grammar is as follows:

file: `grammar.py`
```python
from pylgen.grammar.grammar import AttributedGrammar
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType

from .grammar_symbols import (
    Config,
    ConfigSequence,
    Section,
    SectionConfigSequence,
    SubSection,
    ConfigAtom,
    lbracket,
    rbracket,
    variable,
    newline,
    indent,
    dedent,
    colon,
    string,
    boolean,
    number,
    minus
)

from .reductors import (
    config_configsequence_reductor,
    configsequence_section_reductor,
    configsequence_direct_reductor,
    section_reductor,
    sectionconfigsequence_configatom_reductor,
    sectionconfigsequence_sectionconfigsequence_configatom,
    configatom_variable_colon_boolean_reductor,
    configatom_variable_colon_number_reductor,
    configatom_variable_colon_string_reductor
)

G = AttributedGrammar(Config,'$')

G[Config] += (ConfigSequence,),config_configsequence_reductor

G[ConfigSequence] += (ConfigSequence,Section),configsequence_section_reductor
G[ConfigSequence] += (Section,),configsequence_direct_reductor

G[Section] += (lbracket,variable,rbracket,newline,indent,SectionConfigSequence,dedent),section_reductor

G[SectionConfigSequence] += (ConfigAtom,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SubSection,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SectionConfigSequence,ConfigAtom),sectionconfigsequence_sectionconfigsequence_configatom
G[SectionConfigSequence] += (SectionConfigSequence,SubSection),sectionconfigsequence_sectionconfigsequence_configatom

G[ConfigAtom] += (variable,colon,string,newline),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean,newline),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number,newline),configatom_variable_colon_number_reductor
G[ConfigAtom] += (variable,colon,string),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number),configatom_variable_colon_number_reductor

G[SubSection] += (minus,variable,colon,newline,indent,SectionConfigSequence,dedent),section_reductor

parser = ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1)
```

Let’s focus on `Section`. The production consists of: a left bracket, a variable, a right bracket, a line break, an indent, a sequence of internal configurations, and a dedent. In other words, the grammar relies on the lexer to ensure the `indent` and `dedent` tokens appear in the right place. It does not count spaces or verify nesting depth; it simply expects the lexer to have done its job.

This is elegance through delegation: each layer performs its own task and trusts the preceding one.

The `ConfigAtom` productions are repeated for each value type: string, boolean, and number. It is somewhat verbose, but each has a specialized reducer that converts the token text into the corresponding Python type. This verbosity is the price paid for having distinct types without a semantic analysis phase to infer them.

The parser is built at the end. LALR(1) is more than sufficient for this grammar. There is no ambiguity, no conflicts, and no need for backtracking. PyLGEN builds the tables at import time, and the parser is ready for use.

## Third stop: the AST

This is where the example determines how to represent the knowledge extracted from the text. `asts.py` defines five classes:

```python
from typing import List

from pylgen.common.types import AST

from .grammar_symbols import (
    Config,
    ConfigSequence,
    Section,
    ConfigAtom
)

class ConfigsAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(Config, start_line, start_column,end_line,end_column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSequenceAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigSequence, start_line,start_column,end_line,end_column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSectionAST(AST):

    def __init__(self, section_name:str,start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(Section, start_line,start_column,end_line,end_column)
        self._name = section_name
        self._configs = []

    @property
    def section_name(self) -> str:
        return self._name
    
    def children(self) -> List[AST]:
        return self._configs

class SectionConfigSequenceAST(AST):

    def __init__(self, start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigSequence, start_line,start_column,end_line,end_column)
        self._configs = []

class AtomConfigAST(AST):

    def __init__(self, name:str,value:str | float | bool,start_line: int, start_column: int, end_line:int, end_column:int):
        super().__init__(ConfigAtom, start_line,start_column,end_line,end_column)
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str | float | bool:
        return self._value

    def children(self) -> List[AST]:
        return []
```

 - `ConfigsAST`: the root node, containing a list of sections.

 - `ConfigSequenceAST`: a sequence of sections.

 - `ConfigSectionAST`: a section with a name and content.

 - `SectionConfigSequenceAST`: the content of a section.

 - `AtomConfigAST`: a key-value pair, with a name and a value.

Each node inherits from `AST` and passes a `Symbol` that identifies it. Symbols are the common currency of the analysis: they allow visitors and selectors to distinguish types without using `isinstance` or reflection.

The nodes are deliberately simple. There are no visitor methods, no logic. They are data containers. The logic resides in the reducers and the code generator. That separation is intentional: the AST describes what is there, not what to do with it.

## Fourth stop: the reducers

Each grammar production has an associated reduction function. Reducers receive an ASTListView (a list of already constructed child nodes) and return a new node.

Let's look at a representative one:

```python
def configatom_variable_colon_string_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text[1:-1],sl,sc,el,ec)
    return config
```

The reducer takes the variable at index 0 and the string at index 2 (index 1 is the colon), extracts the name and value, and constructs an `AtomConfigAST`. It is straightforward, predictable, almost mechanical. And that is the idea: reducers don't think; they only transform.

The number and boolean reducers are just as simple:

```python
def configatom_variable_colon_boolean_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text == 'true',sl,sc,el,ec)
    return config

def configatom_variable_colon_number_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,float(val.text),sl,sc,el,ec)
    return config
```

Note the detail: the number is converted to a float, not an int. The DSL does not distinguish between the two, so it is unified as a float. And the boolean is compared against `'true'`. These are small decisions, yet they define the language's semantics.

file: `reductors.py`

```python
from pylgen.common.types import ASTListView,AST

from .asts import (
    ConfigsAST,
    ConfigSequenceAST,
    ConfigSectionAST,
    SectionConfigSequenceAST,
    AtomConfigAST
)

def config_configsequence_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = ConfigsAST(sl,sc,el,ec)
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config._configs = config_sequence._configs
    return config

def configsequence_section_reductor(asts:ASTListView) -> AST:
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config_sequence._configs.append(asts[1])
    config_sequence.end_position = asts[1].end_position
    return config_sequence

def configsequence_direct_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = ConfigSequenceAST(sl,sc,el,ec)
    config._configs.append(asts[0])
    return config

def section_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[5].end_position
    configs:SectionConfigSequenceAST = asts[5] # type:ignore
    var:Token = asts[1] # type:ignore
    config = ConfigSectionAST(var.text,sl,sc,el,ec)
    config._configs = configs._configs
    return config

def sectionconfigsequence_configatom_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = SectionConfigSequenceAST(sl,sc,el,ec)
    config._configs.append(asts[0])
    return config

def sectionconfigsequence_sectionconfigsequence_configatom(asts:ASTListView) -> AST:
    config:SectionConfigSequenceAST = asts[0] # type:ignore
    config._configs.append(asts[1])
    config.end_position = asts[1].end_position
    return config

def configatom_variable_colon_string_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text[1:-1],sl,sc,el,ec)
    return config

def configatom_variable_colon_boolean_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text == 'true',sl,sc,el,ec)
    return config

def configatom_variable_colon_number_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,float(val.text),sl,sc,el,ec)
    return config
```

## Fifth stop: code generation

With the AST in hand, the next step is to convert it into something useful. `codegen.py` implements two functions: `ast_to_dict` and `to_json`.

`ast_to_dict` traverses the AST recursively and constructs a nested dictionary. For `ConfigsAST`, it returns a dictionary containing the sections. For `ConfigSectionAST`, it returns a dictionary with the name as the key and the content as the value. For `AtomConfigAST`, it returns `{name: value}`.

The traversal is manual, without using PyLGEN visitors or selectors. It consists of a series of `isinstance` checks:

file: `codegen.py`

```python
import json
from .asts import ConfigsAST,AtomConfigAST

def ast_to_dict(ast):
    result = {}
    if isinstance(ast,ConfigsAST):
        for child in ast.children():
            result[child.section_name] = ast_to_dict(child) # type:ignore
        return result
    for child in ast.children():
        if isinstance(child,AtomConfigAST):
            result[child.name] = child.value
        else:
            result[child.section_name] = ast_to_dict(child) # type:ignore
    return result

def to_json(ast) -> str:
    json_ast = ast_to_dict(ast)
    return json.dumps(json_ast)
```

To be fair: for a five-node AST, a traversal using `isinstance` is clearer than setting up a visitor system. PyLGEN offers visitors and selectors but does not mandate their use. The example demonstrates that one can choose the right tool for the scale at hand.

`to_json` simply wraps `json.dumps` with indentation, and with that the `config.conf` file becomes

file: `out.json`

```json
{
    "database": {
        "name": "mydatabase",
        "host": "localhost",
        "port": 5432.0,
        "options": {
            "security_level": 1.0,
            "onfail": "report"
        },
        "extra": {
            "important": true
        }
    },
    "users": {
        "max": 10.0,
        "min": 5.0,
        "options": {
            "onfull": "denegate",
            "overflow": "expulse"
        }
    }
}
```

## Sixth stop: the CLI

`main.py` acts as the glue. It uses `argparse` to define four options: input, output, AST visualization, and cache. 

```python
from argparse import ArgumentParser
from idented_dsl.lexer import lexer
from idented_dsl.grammar import parser
from idented_dsl.codegen import to_json

import os

arg_parser = ArgumentParser()
arg_parser.add_argument('-input','-i',help='file input',required=True)
arg_parser.add_argument('-draw','-d',help='draw the result ast',default=False,required=False,action='store_true')
arg_parser.add_argument('-cache','-c',help='especify the cache file an use it (ONLY VALID WITH -d flag)',required=False)
arg_parser.add_argument('-output','-o',help='output file',default='out.json',required=False)
args = arg_parser.parse_args()

file = args.input
draw_flag = args.draw
cache = args.cache
output_file = args.output

if not os.path.exists(file) or not os.path.isfile(file):
    raise ValueError()

with open(file,'r') as f:
    lexer.load_text(f.read())
    ast = parser.parse(lexer.tokens)
    errors = list(lexer.errors) + parser.errors
    if errors:
        for error in errors:
            print(error)
    elif draw_flag:
        if cache and (not os.path.exists(cache) or not os.path.isfile(cache)):
            raise ValueError()
        from pylgen.visual import draw_ast,set_cache_file

        if cache:
            set_cache_file(cache)
        draw_ast(ast,show=True,cache=True if cache else False)

    if not errors:
        json = to_json(ast)
        with open(output_file,'w') as f:
            f.write(json)
```

The flow is linear:

 - Read the file.

 - Load it into the lexer.

 - Parse the tokens.

 - Check for errors.

 - If there are no errors, generate JSON or visualize the AST.

Error handling is straightforward:

```python
    lexer.load_text(f.read())
    ast = parser.parse(lexer.tokens)
    errors = list(lexer.errors) + parser.errors
    if errors:
        for error in errors:
            print(error)
```

Lexer and parser errors are collected; if any exist, they are printed, and the process aborts. For an example, this suffices.

## What this example teaches

`idented_dsl` is a small example, but it encapsulates important lessons on how to use PyLGEN.

> ### Lesson 1:

Each layer has its own role. The lexer classifies characters and detects indentation. The grammar describes the structure. Reducers build the AST. The code generator transforms the AST. The CLI orchestrates the process. No layer encroaches on another.

> ### Lesson 2:

Indentation is a lexer concern, not a grammar concern. Thanks to `IdentedLexer`, the grammar can completely ignore whitespace and work with `indent` and `dedent` tokens as if they were curly braces. This greatly simplifies the production rules.

> ### Lesson 3:

Reducers are mechanical, not creative. Their job is to translate one form (a list of child nodes) into another (a parent node). All the creativity lies in the grammar, which determines which combinations are valid.

> ### Lesson 4:

You don't need to use all of PyLGEN. The example uses `IdentedLexer`, `AttributedGrammar`, `ParserBuilder`, and `draw_ast`. It does not use visitors, selectors, traversal strategies, or semantic analysis. And that is fine. PyLGEN offers a range of tools; each project selects the ones it needs.

> ### Lesson 5:

A small DSL can be implemented in just a few lines. All told, the example contains around 300 lines of code. Most of it is declarative: lexical rules, grammar productions, and one-line reducers. The imperative part (CLI, code generation) is minimal. That is exactly what one wants from a compiler framework: for language knowledge to be declarative and for imperative code to be incidental.

## What's next?

You've seen how a complete, working DSL can be built with PyLGEN in just a few hundred lines. The next example, `mini-python`, takes the same principles and applies them to a much larger language: a subset of Python with its own GUI. If `idented_dsl` is a sketch, `mini-python` is a full painting.

Ready to see it? Let's go.