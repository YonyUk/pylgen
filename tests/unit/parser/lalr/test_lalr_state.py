from common.types import Symbol
from parser.lalr_parser import LALRState,LALRItem

class TestLALRState:

    def test_lalr_state_creation(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)
        end = Symbol('$',True)

        item1 = LALRItem(E,[E,p],[T],{end})
        item2 = LALRItem(E,[T],[],{end})

        state = LALRState({item1,item2})

        assert len(state.items) == 2
        assert item1 in state.items
        assert item2 in state.items
    
    def test_lalr_state_equality(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)
        end = Symbol('$',True)

        item1 = LALRItem(E,[E,p],[T],{end})
        item2 = LALRItem(E,[T],[],{end})
        item3 = LALRItem(E,[],[E,p,T])
        item4 = LALRItem(E,[],[T])

        state1 = LALRState({item1,item2})
        state2 = LALRState({item3,item4})
        state3 = LALRState({item1,item2})
        state4 = LALRState({item3,item4})

        assert state1 == state3
        assert state2 == state4
        assert state1 != state2
        assert state3 != state4