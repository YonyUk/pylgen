# The `regex` Module

The `regex` module is a standalone regular expression engine. It parses regex strings into an AST, evaluates them into NFAs or DFAs, converts between automata and regular grammars, and synthesizes regexes from automata. It is the foundation of the lexer.

## `RegexEngine`

Static class providing the primary API. All methods are stateless and thread‑safe.

> ### Methods

| **Method** | **Description** |
| :---: | :---: |
| `Parse(re: str) -> DFA` | Parses a regex and returns a minimized DFA |
| `GetAutomaton(g: Grammar) -> DFA` | Converts a regular grammar into a minimized DFA. Raises `ValueError` if `g` is not regular |
| `GetGrammar(automaton: Automaton) -> Grammar` | Converts an automaton into a right‑linear grammar |
| `GetRegex(automaton: Automaton) -> str` | Derives a regex using state elimination |
| `BuildRegexParser() -> Parser` | Returns a LALR(1) parser for regexes |
| `BuildRegexLexer() -> BaseLexer` | Returns a lexer for regex strings |

## Examples

> ### Parsing a Regex into a DFA

=== "Python"

    ```python
    from pylgen.regex import RegexEngine

    dfa = RegexEngine.Parse('a(b|c)*d')
    assert dfa.accept(['a', 'b', 'c', 'd'])
    assert dfa.accept(['a', 'd'])
    assert dfa.accept(['a', 'b', 'd'])
    assert dfa.accept(['a', 'c', 'd'])
    assert not dfa.accept(['a', 'b', 'b'])
    ```

=== "Cython"

    ```cython
    from pylgen.regex.engine cimport _parse
    from pylgen.automaton.automaton cimport DFA

    cdef DFA dfa = _parse('a(b|c)*d')
    assert dfa.accept(['a', 'b', 'c', 'd'])
    assert dfa.accept(['a', 'd'])
    assert dfa.accept(['a', 'b', 'd'])
    assert dfa.accept(['a', 'c', 'd'])
    assert not dfa.accept(['a', 'b', 'b'])
    ```

#### Supported Syntax

 - Character classes: `[abc]`, `[^abc]`, `[a-z]`

 - Predefined constants: `\d`, `\D`, `\s`, `\S`, `\w`, `\W`, .

 - Quantifiers: `*`, `+`, `?`, `{min,max}`

 - Grouping: `(regex)`

 - Escapes: `\(`, `\)`, `\[`, `\]`, `\{`, `\}`, `\-`, `\*`, `\+`, `\?`, `\^`, `\|`, `\.`, `\,`.

!!! important
    The constants (`\D`, `\S`, `\W`, `.`, and the default negated class) operate over the extended Latin characters alphabet (accented vowels, diaeresis, and eñe: `á é í ó ú ü ñ` and their uppercase forms).

> ### Converting a Regular Grammar to a DFA

=== "Python"

    ```python
    from pylgen.common.types import Symbol
    from pylgen.grammar.grammar import Grammar
    from pylgen.regex import RegexEngine

    S = Symbol('S')
    a = Symbol('a', True)
    b = Symbol('b', True)

    G = Grammar(S)
    G[S] += (a, S)   # S -> a S
    G[S] += (b,)     # S -> b

    dfa = RegexEngine.GetAutomaton(G)
    ```

=== "Cython"

    ```cython
    from pylgen.common.types cimport Symbol
    from pylgen.grammar.grammar cimport Grammar
    from pylgen.regex.engine cimport _get_automaton
    from pylgen.automaton.automaton cimport DFA

    cdef Symbol S = Symbol('S')
    cdef Symbol a = Symbol('a', True)
    cdef Symbol b = Symbol('b', True)

    cdef Grammar G = Grammar(S)
    G._add_production(S, [a, S])   # S -> a S
    G._add_production(S, [b])      # S -> b

    cdef DFA dfa = _get_automaton(G)
    ```

> ### Deriving a Regex from an Automaton

=== "Python"

    ```python
    from pylgen.automaton.automaton import DFA, State
    from pylgen.regex import RegexEngine

    dfa = DFA('q0', None, {'a', 'b'}, True)
    q0 = dfa.start_state
    dfa += q0, 'a', q0
    dfa += q0, 'b', q0

    regex = RegexEngine.GetRegex(dfa)
    print(regex)  # (a|b)*
    ```

=== "Cython"

    ```cython
    from pylgen.automaton.automaton cimport DFA, State
    from pylgen.regex.engine cimport _get_regex

    cdef DFA dfa = DFA('q0', None, {'a', 'b'}, True)
    cdef State q0 = dfa._start_state
    dfa.add_transition(q0, q0, 'a')
    dfa.add_transition(q0, q0, 'b')

    cdef str regex = _get_regex(dfa)
    print(regex)  # (a|b)*
    ```