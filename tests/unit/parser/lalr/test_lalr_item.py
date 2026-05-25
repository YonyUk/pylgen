from parser.lalr_parser import LALRItem
from common.types import Symbol

class TestLALRItem:

    def test_lalr_item_creation(self):
        E = Symbol('E')
        T = Symbol('T')

        p = Symbol('+',True)
        end = Symbol('$',True)

        item = LALRItem(E,[E,p],[T])

        assert item.head == E
        assert item.left == [E,p]
        assert item.right == [T]
        assert len(item.lookaheads) == 0

        item = LALRItem(E,[E,p],[T],{end})

        assert item.head == E
        assert item.left == [E,p]
        assert item.right == [T]
        assert item.lookaheads == { end }
    
    def test_lalr_item_equality_1(self):
        E = Symbol('E')
        T = Symbol('T')

        p = Symbol('+',True)
        end = Symbol('$',True)

        item1 = LALRItem(E,[E,p],[T])
        item2 = LALRItem(E,[E,p],[T],{end})
        item3 = LALRItem(E,[E,p],[T],{end})

        assert item1 != item2
        assert item1 != item3
        assert item2 == item3
    
    def test_lalr_item_equality_2(self):
        S_ = Symbol('S\'')
        S = Symbol('S')
        L = Symbol('L')
        R = Symbol('R')

        id_ = Symbol('id',True)
        eq = Symbol('=',True)
        m = Symbol('*',True)
        end = Symbol('$',True)

        item1 = LALRItem(L,[],[id_],{eq,end})
        item2 = LALRItem(L,[],[id_],{eq,end})

        assert item1 == item2
        assert item1 in {item2}