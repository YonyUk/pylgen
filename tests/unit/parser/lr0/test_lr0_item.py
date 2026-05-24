from parser.lr0_parser import LR0Item
from common.types import Symbol

class TestLR0Item:

    def test_lr0_item_cration(self):
        E = Symbol('E')
        p = Symbol('+',True)
        T = Symbol('T')

        item = LR0Item(E,[E,p],[T])

        assert item.head == E
        assert item.left == [E,p]
        assert item.right == [T]

    def test_lr0_item_equality(self):
        E = Symbol('E')
        p = Symbol('+',True)
        T = Symbol('T')

        item1 = LR0Item(E,[E,p],[T])
        item2 = LR0Item(E,[E,p],[T])
        item3 = LR0Item(E,[T],[])

        assert item1 == item2
        assert item1 != item3
        assert item2 != item3