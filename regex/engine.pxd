from automaton.automaton cimport DFA,NFA
from grammar.grammar cimport Grammar

cdef class RegexEngine:
    pass

cdef DFA _left_regular_automaton(Grammar g)
cdef DFA _right_regular_automaton(Grammar g)
cdef DFA _get_automaton(Grammar g)
cdef Grammar _get_grammar_from_dfa(DFA dfa)
# cdef Grammar _get_grammar_from_nfa(NFA nfa)