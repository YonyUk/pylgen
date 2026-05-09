from typing import Any

import pytest

from automaton import State

class TestState:

    @pytest.mark.parametrize("id,value,is_accepting",[
        ('id','id',True),
        ('id','id',False),
        ('id',1,True),
        ('id',1,False),
        ('1',1,True),
        ('1',1,False),
        ('True',True,True),
        ('False',False,False),
    ])
    def test_state_creation(self,id:str,value:Any,is_accepting:bool):
        state = State(id,value,is_accept=is_accepting)

        assert state.id == id
        assert state.value == value
        assert state.is_accept == is_accepting
    
    def test_state_initialization_error(self):
        with pytest.raises(TypeError):
            state = State(0,0) #type:ignore
        with pytest.raises(TypeError):
            state = State(True,0) #type:ignore
        with pytest.raises(TypeError):
            state = State([0,1,2],0) #type:ignore
    
    def test_state_inmutability(self):
        state = State('id','id')

        with pytest.raises(AttributeError):
            state.id = 'new_id' #type:ignore
        with pytest.raises(AttributeError):
            state.value = 'new_value' #type:ignore
        with pytest.raises(AttributeError):
            state.is_accept = True #type:ignore