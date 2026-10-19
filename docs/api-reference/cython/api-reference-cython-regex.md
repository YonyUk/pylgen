# Module `regex`

## Submodule `regex.engine`

> ### `RegexParsingException`

Exception raised when a regex can't be parsed. Inherits from `Exception` (`RegexParsingException(Exception)`).

#### Properties

 - `_errors (cdef list[RuntimeError])`

> ### Internal Functions

 - `cdef DFA _left_regular_automaton(g)`: returns a `DFA` equivalent to `g` (specific for left-regular grammars).
    - Args:
        - `g (Grammar)`

 - `cdef DFA _right_regular_automaton(g)`: returns a `DFA` equivalent to `g` (specific for right-regular grammars).
    - Args:
        - `g (Grammar)` 

 - `cdef DFA _get_automaton(g)`:  returns the `DFA` equivalent to the language described by `g`.
    - Args:
        - `g (Grammar)`
    
    - Raises: `ValueError('g must be a regular grammar')` if `g` is not a regular grammar.

 - `cdef Grammar _get_grammar(dfa)`: returns the grammar equivalent to `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `cdef str _get_regex(automaton)`: returns an equivalent regex to `automaton`.
    - Args:
        - `automaton (Automaton)`

 - `cdef DFA _parse(re)`: returns the `DFA` equivalent to `re`.
    - Args:
        - `re (str)`
    
    - Raises: `RegexParsingException` if there are runtime errors.

## Submodule `regex.regex_parser`

 - `cdef set[str] get_latin_punctuation()`, `cdef set[str] get_latin_letters()`: gets latin letters and punctuation characters.

 - `cdef BottomUpParser _build_regex_parser()`: returns a parser for regex expressions.

 - `cdef BaseLexer _build_regex_lexer()`: returns a lexer for regex expressions.