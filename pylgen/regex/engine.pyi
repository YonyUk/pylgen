from ..automaton.automaton import DFA,Automaton
from ..grammar.grammar import Grammar
from ..parser.parser import Parser
from ..lexer.base_lexer import BaseLexer

class RegexEngine:

    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA: ...

    @staticmethod
    def GetGrammar(automaton: Automaton) -> Grammar: ...

    @staticmethod
    def BuildRegexParser() -> Parser: ...

    @staticmethod
    def BuildRegexLexer() -> BaseLexer: ...

    @staticmethod
    def Parse(re:str) -> DFA: ...

    @staticmethod
    def GetRegex(automaton:Automaton) -> str: ...