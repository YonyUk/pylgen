# Module `regex`

## Submodule `regex.engine`

> ### `RegexParsingException`

Exception raised when a regex can't be parsed. Inherits from `Exception` (`RegexParsingException(Exception)`).

#### Properties

 - `errors (List[RuntimeError])`

> ### `RegexEngine`

Static class.

#### Methods

 - `Parse(re)`: returns the `DFA` equivalent to `re`.
    - Args:
        - `re (str)`
    
    - Raises: `RegexParsingException` if there are runtime errors.

 - `GetAutomaton(g)`: returns the `DFA` equivalent to the language described by `g`.
    - Args:
        - `g (Grammar)`
    
    - Raises: `ValueError('g must be a regular grammar')` if `g` is not a regular grammar.

 - `GetGrammar(automaton)`: returns the grammar equivalent to `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `GetRegex(automaton)`: returns an equivalent regex to `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `BuildRegexParser()`: returns a parser for regex expressions.

 - `BuildRegexLexer()`: returns a lexer for regex expressions.