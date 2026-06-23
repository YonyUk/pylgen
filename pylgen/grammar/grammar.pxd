from ..common.types cimport Symbol

cdef class SymbolNotPresentInGrammarException(Exception):
    cdef str _msg

cdef class Production:
    cdef Symbol _head
    cdef list[Symbol] _production
    cdef str _id

cdef class ProductionsSet:
    cdef dict[str,list[Symbol]] _productions
    cdef list[Symbol] _last_production_added

    cdef void _add_production(self,list[Symbol] production)

cdef class AttributedProductionsSet(ProductionsSet):
    cdef object _last_reductor_added
    
    cdef void _add_attributed_production(self,list[Symbol] production,object reductor)

cdef class Grammar:
    cdef Symbol _start_symbol
    cdef Symbol _end_symbol
    cdef set[Symbol] _terminals,_non_terminals
    cdef dict[Symbol,set[Symbol]] _follows,_firsts
    cdef dict[Symbol,ProductionsSet] _productions
    cdef dict[Symbol,set[Production]] _productions_by_symbol
    cdef bint _firsts_computed
    cdef bint _follows_computed
    cdef Symbol _epsilon
    cdef set[Production] _productions_cache
    cdef set[Symbol] _symbols

    cdef bint _derives_in_epsilon(self,Symbol symbol)
    cdef void _make_firsts(self)
    cdef void _make_follows(self)
    cdef void _add_production(self,Symbol head,list[Symbol] production)
    cdef str _id(self)

    cpdef set[Symbol] first(self,list[Symbol] production)
    cpdef set[Symbol] follow(self,Symbol symbol)
    cpdef dict to_dict(self)

cdef class AttributedGrammar(Grammar):
    cdef dict[Production,object] _reductors_by_production

    cdef void _add_attributed_production(self,Symbol head,list[Symbol] production, object reductor)
    cpdef object get_reductor(self,Production production)

cdef bint _is_left_regular(Grammar g)
cdef bint _is_right_regular(Grammar g)
cdef Grammar _augment_grammar(Grammar g)
cdef Grammar _reverse_grammar(Grammar g)