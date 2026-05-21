from automaton.automaton import DFA
from grammar.grammar import Grammar

class RegexEngine:

    @staticmethod
    def get_automaton(g:Grammar) -> DFA: ...