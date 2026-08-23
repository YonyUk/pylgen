from pylgen.common.types import Symbol
from pylgen.parser.lr1_parser import LR1State,LR1Item

class TestLALRState:

    def test_lalr_state_creation(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)
        end = Symbol('$',True)

        item1 = LR1Item(E,[E,p],[T],end)
        item2 = LR1Item(E,[T],[],end)

        state = LR1State({item1,item2})

        assert len(state.items) == 2
        assert item1 in state.items
        assert item2 in state.items
    
    def test_lalr_state_equality(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)
        end = Symbol('$',True)

        item1 = LR1Item(E,[E,p],[T],end)
        item2 = LR1Item(E,[T],[],end)
        item3 = LR1Item(E,[],[E,p,T],p)
        item4 = LR1Item(E,[],[T],p)

        state1 = LR1State({item1,item2})
        state2 = LR1State({item3,item4})
        state3 = LR1State({item1,item2})
        state4 = LR1State({item3,item4})

        assert state1 == state3
        assert state2 == state4
        assert state1 != state2
        assert state3 != state4