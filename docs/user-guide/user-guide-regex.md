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

## Typical Usage

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