from pylgen.parser.lalr_parser import LALRItem
from pylgen.common.types import Symbol

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
        L = Symbol('L')

        id_ = Symbol('id',True)
        eq = Symbol('=',True)
        end = Symbol('$',True)

        item1 = LALRItem(L,[],[id_],{eq,end})
        item2 = LALRItem(L,[],[id_],{eq,end})

        assert item1 == item2
        assert item1 in {item2}

    def test_lalr_item_hashing(self):
        L = Symbol('L')
        
        id_ = Symbol('id',True)
        eq = Symbol('=',True)
        eq2 = Symbol('=')
        end = Symbol('$',True)

        item1 = LALRItem(L,[],[id_],{eq,end})
        item2 = LALRItem(L,[],[id_],{eq,end})
        item3 = LALRItem(L,[],[id_],{eq2,end})

        assert hash(item1) == hash(item2)
        assert hash(item1) != hash(item3)