from automaton.automaton cimport DFA
from grammar.grammar cimport Grammar

cdef class RegexEngine:
    pass

cdef DFA _left_regular_automaton(Grammar g)
cdef DFA _right_regular_automaton(Grammar g)
cdef DFA _get_automaton(Grammar g)