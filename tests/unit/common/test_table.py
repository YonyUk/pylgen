import pytest

from pylgen.common import Table

class TestTable:

    @pytest.fixture
    def table(self) -> Table: return Table()

    def test_table_creation(self):

        t = Table()

        assert len(t.entries) == 0
        assert len(t.values) == 0
        assert len(t.items) == 0
    
    def test_table_add_data(self,table:Table):
        table['a','b'] = 'c'

        assert len(table.entries) == 1
        assert ('a','b') in table.entries
        assert len(table.values) == 1
        assert 'c' in table.values
        assert len(table.items) == 1
        assert ('a','b','c') in table.items
        assert table['a','b'] == 'c'
    
    def test_table_delete_data(self,table:Table):
        table['a','b'] = 'c'
        del table['a','b']
        
        assert len(table.entries) == 0
        assert len(table.values) == 0
        assert len(table.items) == 0
    
    def test_table_overwrite_data(self,table:Table):
        table['a','b'] = 'c'
        table['a','b'] = 'd'

        assert len(table.entries) == 1
        assert ('a','b') in table.entries
        assert len(table.values) == 1
        assert 'd' in table.values
        assert 'c' not in table.values
        assert len(table.items) == 1
        assert ('a','b','d') in table.items
        assert ('a','b','c') not in table.items
        assert table['a','b'] == 'd'
    
    def test_table_add_many_data(self,table:Table):
        table['a','b'] = 'c'
        table['x','y'] = 'z'

        assert len(table.entries) == 2
        assert ('a','b') in table.entries
        assert ('x','y') in table.entries
        assert len(table.values) == 2
        assert 'c' in table.values
        assert 'z' in table.values
        assert len(table.items) == 2
        assert ('a','b','c') in table.items
        assert ('x','y','z') in table.items
        assert table['a','b'] == 'c'
        assert table['x','y'] == 'z'
    
    def test_table_raise_key_error(self,table:Table):
        with pytest.raises(KeyError):
            table['a','b']

    def test_table_delete_only_one_data(self,table:Table):
        table['a','b'] = 'c'
        table['x','y'] = 'z'

        del table['x','y']

        assert len(table.entries) == 1
        assert ('a','b') in table.entries
        assert ('x','y') not in table.entries
        assert len(table.values) == 1
        assert 'c' in table.values
        assert 'z' not in table.values
        assert len(table.items) == 1
        assert ('a','b','c') in table.items
        assert ('x','y','z') not in table.items
        assert table['a','b'] == 'c'

        with pytest.raises(KeyError):
            table['x','y']