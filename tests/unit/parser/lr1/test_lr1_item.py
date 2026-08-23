from pylgen.parser.lr1_parser import LR1Item
from pylgen.common.types import Symbol

class TestLALRItem:

    def test_lalr_item_creation(self):
        E = Symbol('E')
        T = Symbol('T')

        p = Symbol('+',True)
        end = Symbol('$',True)

        item = LR1Item(E,[E,p],[T],end)

        assert item.head == E
        assert item.left == [E,p]
        assert item.right == [T]
        assert item.lookahead == end

        item = LR1Item(E,[E,end],[T],p)

        assert item.head == E
        assert item.left == [E,end]
        assert item.right == [T]
        assert item.lookahead == p
    
    def test_lalr_item_equality_1(self):
        E = Symbol('E')
        T = Symbol('T')

        p = Symbol('+',True)
        end = Symbol('$',True)
        m = Symbol('-',True)

        item1 = LR1Item(E,[E,p],[T],m)
        item2 = LR1Item(E,[E,p],[T],end)
        item3 = LR1Item(E,[E,p],[T],end)

        assert item1 != item2
        assert item1 != item3
        assert item2 == item3
    
    def test_lalr_item_equality_2(self):
        L = Symbol('L')

        id_ = Symbol('id',True)
        eq = Symbol('=',True)

        item1 = LR1Item(L,[],[id_],eq)
        item2 = LR1Item(L,[],[id_],eq)

        assert item1 == item2
        assert item1 in {item2}