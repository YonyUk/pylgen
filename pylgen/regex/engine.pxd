from ..automaton.automaton cimport DFA,NFA,Automaton,State
from ..grammar.grammar cimport Grammar
from ..analysis.error cimport RuntimeError

cdef class RegexEngine:
    pass

cdef class RegexParsingException(Exception):

    cdef list[RuntimeError] _errors

cdef DFA _left_regular_automaton(Grammar g)
cdef DFA _right_regular_automaton(Grammar g)
cdef DFA _get_automaton(Grammar g)
cdef Grammar _get_grammar(Automaton dfa)
cdef bint _is_normalized(Automaton automaton)
cdef NFA _normalize(Automaton automaton)
cdef tuple[dict[tuple[str,str],str],list[tuple[str,str]]] _build_tags_for_regex_reduction(Automaton automaton)
cdef tuple[dict[str,set[str]],dict[str,set[str]]] _get_predecessors_and_successors(Automaton automaton)
cdef str _get_regex(Automaton automaton)
cdef DFA _parse(str re)