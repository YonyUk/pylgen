from automaton.automaton import DFA
from grammar.grammar import Grammar

class RegexEngine:

    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA: ...