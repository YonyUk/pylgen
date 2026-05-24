from automaton.automaton import DFA,Automaton
from grammar.grammar import Grammar

class RegexEngine:

    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA: ...

    @staticmethod
    def GetGrammar(automaton: Automaton) -> Grammar: ...