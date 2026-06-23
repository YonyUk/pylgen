from pylgen.common.types import Symbol
from pylgen.parser.lr0_parser import LR0State,LR0Item

class TestLR0State:

    def test_lr0_state_creation(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)

        item1 = LR0Item(E,[E,p],[T])
        item2 = LR0Item(E,[T],[])

        state = LR0State({item1,item2})

        assert len(state.items) == 2
        assert item1 in state.items
        assert item2 in state.items
    
    def test_lr0_state_equality(self):
        E = Symbol('E')
        T = Symbol('T')
        p = Symbol('+',True)

        item1 = LR0Item(E,[E,p],[T])
        item2 = LR0Item(E,[],[T])

        item3 = LR0Item(E,[],[E,p,T])
        item4 = LR0Item(E,[],[T])

        state1 = LR0State({item1,item2})
        state2 = LR0State({item3,item4})
        state3 = LR0State({item1,item2})
        state4 = LR0State({item3,item4})

        assert state1 == state3
        assert state2 == state4
        assert state1 != state2
        assert state3 != state4