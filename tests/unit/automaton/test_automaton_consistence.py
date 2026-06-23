import pytest
from typing import Set

from pylgen.automaton import Automaton,DFA,NFA,State

class TestAutomatonConsistence:

    @pytest.fixture
    def alphabet(self) -> Set[str]:
        return {'1','0'}
    
    @pytest.fixture
    def zero_terminated_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0',True)
        q1 = State('q1','q1')

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_transition(q0,q1,'1')
        aut.add_transition(q0,q0,'0')
        aut.add_transition(q1,q1,'1')
        aut.add_transition(q1,q0,'0')

        return aut
    
    @pytest.fixture
    def zero_terminated_alternate_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0',True)
        q1 = State('q1','q1')

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_transition(q0,q1,'1')
        aut.add_transition(q1,q0,'0')

        return aut

    @pytest.fixture
    def alternate_dfa(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0',True)
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_transition(q0,q1,'1')
        aut.add_transition(q1,q0,'0')

        return aut
    
    @pytest.fixture
    def empyt_dfa_1(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0')

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(q0,q0,'1')
        return aut
    
    @pytest.fixture
    def no_empty_nfa(self,alphabet:Set[str]) -> NFA:
        aut = NFA('start','start',alphabet)

        q0 = State('q0','q0')
        q1 = State('q1','q1')

        q2 = State('q2','q2',True)

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(aut.start_state,q1,'1')

        aut.add_epsilon_transition(aut.start_state,q2)
        return aut

    @pytest.fixture
    def finite_dfa_1(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q0,'0')
        aut.add_transition(q0,q1,'1')
        return aut
    
    @pytest.fixture
    def finite_dfa_2(self,alphabet:Set[str]) -> DFA:
        aut = DFA('start','start',alphabet)

        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        aut.add_transition(aut.start_state,q0,'1')
        aut.add_transition(q0,q1,'0')
        return aut

    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_1(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa)
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_2(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_3(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa)
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_4(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa)
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2}).to_deterministic()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_5(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa)
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2}).to_deterministic().minimize()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_6(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa)
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c).minimize()

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_7(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_8(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2}).to_deterministic()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_9(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2}).to_deterministic().minimize()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_10(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa)

        c = Automaton.Union({c_1,c_2})

        intersection = Automaton.Complement(c).minimize()

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_11(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2}).to_deterministic()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_12(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2}).to_deterministic().minimize()

        intersection = Automaton.Complement(c)

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_13(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2}).to_deterministic()

        intersection = Automaton.Complement(c).minimize()

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    @pytest.mark.parametrize("string",[
        '',
        '0',
        '1',
        '00',
        '01',
        '10',
        '11',
        '001',
        '010',
        '100',
        '011',
        '101',
        '110',
        '000',
        '111',
        '000101010010',
        '110101100110',
        '0101010101010',
        '101010101010101',
        '010101',
        '0101010'
    ])
    def test_intersection_regular_languages_proof_by_construction_14(
        self,
        string:str,
        zero_terminated_dfa:DFA,
        alternate_dfa:DFA
    ):
        
        if not zero_terminated_dfa.is_complete:
            zero_terminated_dfa.make_complete()
        
        if not alternate_dfa.is_complete:
            alternate_dfa.make_complete()
        
        c_1 = Automaton.Complement(zero_terminated_dfa).minimize()
        c_2 = Automaton.Complement(alternate_dfa).minimize()

        c = Automaton.Union({c_1,c_2}).to_deterministic().minimize()

        intersection = Automaton.Complement(c).minimize()

        assert intersection.accept(list(string)) == (zero_terminated_dfa.accept(list(string)) and alternate_dfa.accept(list(string)))
    
    def test_is_empty_method(self,zero_terminated_dfa:DFA,empyt_dfa_1:DFA,no_empty_nfa:NFA):

        assert not zero_terminated_dfa.is_empty
        assert empyt_dfa_1.is_empty
        assert not no_empty_nfa.is_empty
    
    def test_is_finite_method(self,zero_terminated_dfa:DFA,finite_dfa_1:DFA,finite_dfa_2:DFA):

        assert not zero_terminated_dfa.is_finite
        assert finite_dfa_1.is_finite
        assert finite_dfa_2.is_finite

        uni = Automaton.Union({finite_dfa_1,finite_dfa_2})

        assert uni.is_finite
        assert uni.to_deterministic().is_finite
        assert uni.to_deterministic().minimize().is_finite
    
    def test_subset_consistency(self,zero_terminated_dfa:DFA,zero_terminated_alternate_dfa:DFA):

        inter = Automaton.Intersection({zero_terminated_alternate_dfa,Automaton.Complement(zero_terminated_dfa)})

        assert inter.is_empty