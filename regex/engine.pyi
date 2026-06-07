from automaton.automaton import DFA,Automaton
from grammar.grammar import Grammar
from parser.parser import Parser
from lexer.lexer import BaseLexer

class RegexEngine:

    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA: ...

    @staticmethod
    def GetGrammar(automaton: Automaton) -> Grammar: ...

    @staticmethod
    def regex_parser() -> Parser: ...

    @staticmethod
    def regex_lexer() -> BaseLexer: ...