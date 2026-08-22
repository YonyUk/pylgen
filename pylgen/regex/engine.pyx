from ..automaton.automaton cimport NFA,DFA,State,Automaton
from ..grammar.grammar cimport Grammar,_is_left_regular,_is_right_regular,ProductionsSet
from ..common.types cimport Symbol,Token
from ..parser.parser cimport Parser
from ..lexer.base_lexer cimport BaseLexer
from ..analysis.visitor cimport ASTWalker
from ..analysis.error cimport RuntimeError
from .enums import ReTokenType

from .regex_parser cimport (
    _build_regex_parser,
    _build_regex_lexer,
    _get_regex_ast_walker,
    RegexAST,
    RegexContext
)

from hashlib import sha256

regex_walker,regex_context = _get_regex_ast_walker()

parser:Parser = _build_regex_parser()
lexer:BaseLexer = _build_regex_lexer()

cdef class RegexParsingException(Exception):

    def __init__(self,errors:list[RuntimeError], *args: object) -> None:
        super().__init__(*args)
        self._errors = errors
    
    @property
    def errors(self) -> list[RuntimeError]:
        return self._errors.copy()

cdef class RegexEngine:

    @staticmethod
    def BuildRegexParser() -> Parser:
        return _build_regex_parser()
    
    @staticmethod
    def BuildRegexLexer() -> BaseLexer:
        return _build_regex_lexer()
    
    @staticmethod
    def Parse(str re) -> DFA:
        '''
        Args:
            re (str)
        
        Returns:
            DFA: the automaton wich language is exactly the described by the given regular expression
        '''
        return _parse(re)

    @staticmethod
    def GetAutomaton(g:Grammar) -> DFA:
        '''
        Args:
            g (Grammar)
        
        Returns:
            DFA: the automaton that accepts L(g)
        
        Raises:
            ValueError('g must be a regular grammar')
        '''
        return _get_automaton(g)
    
    @staticmethod
    def GetGrammar(automaton:Automaton) -> Grammar:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            Grammar: the equivalent grammar to the given automaton
        '''
        return _get_grammar(automaton)
    
    @staticmethod
    def GetRegex(Automaton automaton) -> str:
        '''
        Args:
            automaton (Automaton)
        
        Returns:
            str: a regex equivalent to the given automaton
        '''
        return _get_regex(automaton)

cdef DFA _left_regular_automaton(Grammar g):
    cdef NFA result
    cdef State state,from_state,to_state,initial,old_to_state,temp_state
    cdef Symbol nt
    cdef set[str] alphabet = set()
    cdef dict[Symbol,State] state_by_symbol = {}
    cdef ProductionsSet productions
    cdef list[Symbol] production
    cdef dict[State,State] epsilon_transition = {}
    cdef tuple[str,str] transition

    # maps non-terminals to states
    for nt in g._non_terminals:
        state = State(nt._symbol,nt._symbol,nt == g._start_symbol) # type:ignore
        state_by_symbol[nt] = state
    
    # builds the alphabet
    for nt in g._terminals:
        if nt == g._end_symbol or nt._is_epsilon: continue
        alphabet.add(nt._symbol)
    
    # builds the automaton
    result = NFA('start','start',alphabet) # type:ignore
    initial = result._start_state

    # adds the transitions
    for nt,productions in g._productions.items():
        for production in productions._productions.values():
            to_state = state_by_symbol[nt]
            # A -> B b
            if len(production) == 2:
                from_state = state_by_symbol[production[0]]
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[1])._symbol):
                    # if is the first time we face to this for the state
                    if not from_state in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[1])._symbol)
                        old_to_state = result.next(from_state,transition[1])
                        # create an intermediate state
                        epsilon_transition[from_state] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[from_state]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[from_state]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,to_state,(<Symbol>production[1])._symbol)
            # A -> B
            elif not (<Symbol>production[0])._is_terminal:
                from_state = state_by_symbol[production[0]]
                result.add_epsilon_transition(from_state,to_state)
            # A -> b
            elif not (<Symbol>production[0])._is_epsilon:
                if result.has_transition(initial,(<Symbol>production[0])._symbol):
                    if not initial in epsilon_transition:
                        transition = (initial._id,(<Symbol>production[0])._symbol)
                        old_to_state = result.next(initial,transition[1])
                        epsilon_transition[initial] = State(f'{initial._id}-{transition[1]}',f'{initial._id}-{transition[1]}') # type:ignore
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[initial]
                        result.add_transition(initial,temp_state,transition[1])
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[initial]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(initial,to_state,(<Symbol>production[0])._symbol)
            # A -> ε
            else:
                result.add_epsilon_transition(initial,to_state)
    
    return result.to_deterministic().minimize()

cdef DFA _right_regular_automaton(Grammar g):
    cdef NFA result
    cdef State state,final_state,from_state,to_state,temp_state,old_to_state
    cdef Symbol nt
    cdef set[str] alphabet = set()
    cdef dict[Symbol,State] state_by_symbol = {}
    cdef ProductionsSet productions
    cdef list[Symbol] production
    cdef dict[Symbol,State] epsilon_transition = {}
    cdef tuple[str,str] transition

    # creates the final state
    final_state = State('final','final',True) # type:ignore

    # maps the non-terminals to states
    for nt in g._non_terminals:
        state = State(nt._symbol,nt._symbol) # type:ignore
        state_by_symbol[nt] = state
    
    # builds the alphabet
    for nt in g._terminals:
        if nt == g._end_symbol or nt._is_epsilon: continue
        alphabet.add(nt._symbol)

    # builds the NFA
    result = NFA(g._start_symbol._symbol,g._start_symbol._symbol,alphabet) # type:ignore
    # sets the start state
    result._start_state = state_by_symbol[g._start_symbol]
    # sets the current state
    result._current_state = result._start_state
    result._states_by_id[g._start_symbol._symbol] = result._start_state
    
    for nt,productions in g._productions.items():
        for production in productions._productions.values():
            from_state = state_by_symbol[nt]
            # A -> b B
            if len(production) == 2:
                to_state = state_by_symbol[production[1]]
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[0])._symbol):
                    # if is the first time we face to this for the state
                    if not nt in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[0])._symbol)
                        old_to_state = result.next(from_state,transition[1])
                        # create an intermediate state
                        epsilon_transition[nt] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[nt]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,old_to_state)
                    temp_state = epsilon_transition[nt]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,to_state,(<Symbol>production[0])._symbol)
            # A -> B
            elif not (<Symbol>production[0])._is_terminal:
                to_state = state_by_symbol[production[0]]
                result.add_epsilon_transition(from_state,to_state)
            # A -> b
            elif not (<Symbol>production[0])._is_epsilon:
                # if already exists a transition for this state with this symbol
                if result.has_transition(from_state,(<Symbol>production[0])._symbol):
                    # if is the first time we face to this for the state
                    if not nt in epsilon_transition:
                        transition = (from_state._id,(<Symbol>production[0])._symbol)
                        # create an intermediate state
                        epsilon_transition[nt] = State(f'{from_state._id}-{transition[1]}',f'{from_state._id}-{transition[1]}') # type:ignore
                        # delets the transition
                        del result._trans_func._table[transition]
                        temp_state = epsilon_transition[nt]
                        # adds a transition for the current state to the intermediate state
                        result.add_transition(from_state,temp_state,transition[1])
                        # adds an epsilon-transition to the old destination state
                        result.add_epsilon_transition(temp_state,final_state)
                    temp_state = epsilon_transition[nt]
                    result.add_epsilon_transition(temp_state,to_state)
                else:
                    result.add_transition(from_state,final_state,(<Symbol>production[0])._symbol)
            # A -> ε
            else:
                result.add_epsilon_transition(from_state,final_state)
    
    return result.to_deterministic().minimize()

cdef DFA _get_automaton(Grammar g):

    if not (_is_right_regular(g) or _is_left_regular(g)):
        raise ValueError('g must be a regular grammar')
    
    if _is_left_regular(g):
        return _left_regular_automaton(g)
    
    return _right_regular_automaton(g)

cdef Grammar _get_grammar(Automaton automaton):
    cdef Grammar result
    cdef dict[str,Symbol] symbols = {}
    cdef State state
    cdef str symbol,f_id,t_id
    cdef tuple[str,str] transition
    cdef Symbol epsilon = Symbol('epsilon',True,True) # type:ignore
    cdef Symbol head,terminal,non_terminal

    for state in automaton._states_by_id.values():
        if state == automaton._start_state:
            f_id = 'S'
        else:
            f_id = f'A{len(symbols)}'
        symbols[state._id] = Symbol(f_id) # type:ignore

    for symbol in automaton._alphabet:
        symbols[symbol] = Symbol(symbol,True) # type:ignore
    
    result = Grammar(symbols[automaton._start_state._id]) # type:ignore
    
    for transition,t_id in automaton._trans_func._table.items():
        f_id = <str>transition[0]
        symbol = <str>transition[1]
        head = symbols[f_id]
        terminal = symbols[symbol]
        non_terminal = symbols[t_id]
        result._add_production(head,[terminal,non_terminal])
    
    for f_id in automaton._epsilons:
        for t_id in automaton._epsilons[f_id]:
            head = symbols[f_id]
            non_terminal = symbols[t_id]
            result._add_production(head,[non_terminal])

    for state in automaton._states_by_id.values():
        if state._is_accept:
            head = symbols[state._id]
            result._add_production(head,[epsilon])
    
    return result

cdef bint _is_normalized(Automaton automaton):
    cdef str f_id,t_id,symbol
    cdef tuple[str,str] transition
    cdef set[str] finals = set()
    cdef list[str] queue,seen

    stack = [automaton._start_state._id]
    seen = []

    # checks for unreachables states
    # BFS
    while stack:
        f_id = stack.pop(0)
        seen.append(f_id)

        for transition,t_id in automaton._trans_func._table.items():
            if transition[0] != f_id:
                continue
            if not (t_id in stack or t_id in seen):
                stack.append(t_id)
        
        if f_id in automaton._epsilons:
            for t_id in automaton._epsilons[f_id]:
                if not (t_id in stack or t_id in seen):
                    stack.append(t_id)
    
    if len(seen) < len(automaton._states_by_id):
        raise ValueError('unreachables states detected')

    for transition in automaton._trans_func._table:
        f_id = transition[0]
        t_id = automaton._trans_func._table[transition]
        # if there is transition to the start state
        if t_id == automaton._start_state._id:
            return False # type:ignore
        # if there is transition from a final state
        if (<State>automaton._states_by_id[f_id])._is_accept:
            return False # type:ignore
        if (<State>automaton._states_by_id[t_id])._is_accept:
            finals.add(t_id)
        if (<State>automaton._states_by_id[f_id])._is_accept:
            finals.add(f_id)
    
    for f_id in automaton._epsilons:
        if (<State>automaton._states_by_id[f_id])._is_accept:
            return False # type:ignore
        for t_id in automaton._epsilons[f_id]:
            if t_id == automaton._start_state._id:
                return False # type:ignore
            if (<State>automaton._states_by_id[f_id])._is_accept:
                finals.add(f_id)
            if (<State>automaton._states_by_id[t_id])._is_accept:
                finals.add(t_id)
    return len(finals) == 1 # type:ignore

cdef NFA _normalize(Automaton automaton):
    cdef set[str] epsilons
    cdef str symbol,t_id,f_id
    cdef object f_value,t_value
    cdef State from_state,to_state
    cdef NFA result = NFA(f'normalized-start-{automaton._start_state._id}',f'normalized-start-{automaton._start_state._id}',automaton._alphabet) # type:ignore
    cdef int finals_counter = 0
    cdef tuple[str,str] transition
    cdef dict[str,State] states_copy_mapping = {}
    cdef list[str] finals_ids = []

    for from_state in automaton._states_by_id.values():
        if from_state._is_accept:
            finals_counter += 1
    
    if finals_counter == 0:
        raise ValueError('Automaton must have at least one final state')

    # copy all states with _is_accept = False for the new automaton
    for from_state in automaton._states_by_id.values():
        states_copy_mapping[from_state._id] = State(from_state._id,from_state._value) # type:ignore
        if from_state._is_accept:
            finals_ids.append(from_state._id)

    finals_ids.sort()

    # adds an epsilon transition from new start state to old start state
    to_state = states_copy_mapping[automaton._start_state._id]
    result.add_epsilon_transition(result._start_state,to_state)

    # copy all the transitions
    for transition in automaton._trans_func._table:
        f_id = <str>transition[0]
        symbol = <str>transition[1]
        t_id = automaton._trans_func._table[transition]
        from_state = states_copy_mapping[f_id]
        to_state = states_copy_mapping[t_id]
        result.add_transition(from_state,to_state,symbol)
    
    # copy all the epsilon transitions
    for f_id in automaton._epsilons:
        from_state = states_copy_mapping[f_id]
        epsilons = automaton._epsilons[f_id]
        for t_id in epsilons:
            to_state = states_copy_mapping[t_id]
            result.add_epsilon_transition(from_state,to_state)
    
    # makes an epsilon transition from finals to the new final
    f_id = sha256(''.join(finals_ids).encode()).hexdigest()
    to_state = State(f_id,f_id,True) # type:ignore

    for f_id in finals_ids:
        from_state = states_copy_mapping[f_id]
        result.add_epsilon_transition(from_state,to_state)
    
    return result

cdef tuple[dict[tuple[str,str],str],list[tuple[str,str]]] _build_tags_for_regex_reduction(Automaton automaton):
    cdef dict[tuple[str,str],str] tags = {}
    cdef list[tuple[str,str]] epsilons = []
    cdef tuple[str,str] key,transition
    cdef str f_id,t_id

    for transition in automaton._trans_func._table:
        key = (transition[0],automaton._trans_func._table[transition])
        if not key in tags:
            tags[key] = transition[1]
        else:
            tags[key] += f'|{transition[1]}'
    
        if '|' in tags[key]:
            tags[key] = f'({tags[key]})'

    for f_id in automaton._epsilons:
        for t_id in automaton._epsilons[f_id]:
            epsilons.append((f_id,t_id))
    
    return tags,epsilons

cdef tuple[dict[str,set[str]],dict[str,set[str]]] _get_predecessors_and_successors(Automaton automaton):
    cdef dict[str,set[str]] successors = {}
    cdef dict[str,set[str]] predecessors = {}
    cdef tuple[str,str] transition
    cdef str f_id,t_id,inner_f_id,inner_t_id
    cdef bint change = True # type:ignore
    cdef set[str] current_set

    for transition in automaton._trans_func._table:
        f_id = <str>transition[0]
        t_id = automaton._trans_func._table[transition]
        if not f_id in successors:
            successors[f_id] = set()
        successors[f_id].add(t_id)
        if not t_id in predecessors:
            predecessors[t_id] = set()
        predecessors[t_id].add(f_id)
    
    for f_id in automaton._epsilons:
        if not f_id in successors:
            successors[f_id] = set()
        for t_id in automaton._epsilons[f_id]:
            if not t_id in predecessors:
                predecessors[t_id] = set()
            predecessors[t_id].add(f_id)
            successors[f_id].add(t_id)
    
    return predecessors,successors

cdef str _get_regex(Automaton automaton):
    cdef str result,f_id,t_id,current_id,bucle_re,predecesor_current_re,current_successor_re,final_id
    cdef Automaton _regex
    cdef list[str] states = []
    cdef State current_state
    cdef dict[tuple[str,str]] tags
    cdef list[tuple[str,str]] epsilons
    cdef dict[str,set[str]] predecessors,successors
    cdef tuple[str,str] tag_key,bucle_tag_key,predecessor_current_tag_key,current_successor_tag_key
    cdef bint predecessor_current_re_derive_in_epsilon,current_successor_re_derive_in_epsilon,pre_re_exists,curr_re_exists

    if not _is_normalized(automaton):
        _regex = _normalize(automaton)
    else:
        _regex = automaton

    tags,epsilons = _build_tags_for_regex_reduction(_regex)
    predecessors,successors = _get_predecessors_and_successors(_regex)

    for current_state in _regex._states_by_id.values():
        if not (current_state._is_accept or current_state._id == _regex._start_state._id):
            states.append(current_state._id)
        elif current_state._is_accept:
            final_id = current_state._id

    while states:
        current_id = states.pop()
        bucle_tag_key = (current_id,current_id)
        if bucle_tag_key in tags:
            if len(tags[bucle_tag_key]) == 1:
                bucle_re = f'{tags[bucle_tag_key]}*'
            elif len(tags[bucle_tag_key]) > 1:
                bucle_re = f'({tags[bucle_tag_key]})*'
            else:
                bucle_re = ''
        else:
            # RULE: ∅* = ε and ε* = ε
            bucle_re = ''
        
        for f_id in predecessors[current_id]:
            if f_id == current_id:
                continue
            predecessor_current_re_derive_in_epsilon = False # type:ignore
            pre_re_exists = False # type:ignore
            predecessor_current_tag_key = (f_id,current_id)
            # R_iq: current tag of the transition
            if predecessor_current_tag_key in tags or predecessor_current_tag_key in epsilons:
                if predecessor_current_tag_key in tags:
                    predecesor_current_re = tags[predecessor_current_tag_key]
                    pre_re_exists = True # type:ignore
                if predecessor_current_tag_key in epsilons:
                    predecessor_current_re_derive_in_epsilon = True # type:ignore
            else:
                # RULE: ∅ ∙ R = ∅
                # the current tag doesn't gets updated
                # R_ij = R_ij | (R_iq ∙ R_qq* ∙ R_qj)
                # R_iq = ∅ ---> (R_iq ∙ R_qq* ∙ R_qj) = (∅ ∙ R_qq* ∙ R_qj) = (∅ ∙ R_qj) = (∅) = ∅
                # So R_iq = ∅ ---> R_ij = R_ij | (R_iq ∙ R_qq* ∙ R_qj) = R_ij | ∅ = R_ij
                continue

            if not pre_re_exists:
                predecesor_current_re = ''

            if predecesor_current_re == '()':
                predecessor_current_re_derive_in_epsilon = True # type:ignore

            if predecessor_current_re_derive_in_epsilon and len(predecesor_current_re) > 0:
                   if len(predecesor_current_re) == 1:
                       predecesor_current_re = f'{predecesor_current_re}?'
                   else:
                       predecesor_current_re = f'({predecesor_current_re})?'

            for t_id in successors[current_id]:
                if t_id == current_id:
                    continue
                current_successor_re_derive_in_epsilon = False # type:ignore
                curr_re_exists = False # type:ignore
                current_successor_tag_key = (current_id,t_id)
                if current_successor_tag_key in tags or current_successor_tag_key in epsilons:
                    if current_successor_tag_key in tags:
                        current_successor_re = tags[current_successor_tag_key]
                        curr_re_exists = True # type:ignore
                    if current_successor_tag_key in epsilons:
                        current_successor_re_derive_in_epsilon = True # type:ignore
                else:
                    # RULE: R ∙ ∅ = ∅
                    # the current tag doesn't gets updated
                    # R_ij = R_ij | (R_iq ∙ R_qq* ∙ R_qj)
                    # R_qj = ∅ ---> (R_iq ∙ R_qq* ∙ R_qj) = (R_iq ∙ R_qq* ∙ ∅) = (R_iq ∙ ∅) = (∅) = ∅
                    # So R_qj = ∅ ---> R_ij = R_ij | (R_iq ∙ R_qq* ∙ R_qj) = R_ij | ∅ = R_ij
                    continue
                
                if not curr_re_exists:
                    current_successor_re = ''

                if current_successor_re == '()':
                    current_successor_re_derive_in_epsilon = True # type:ignore

                if current_successor_re_derive_in_epsilon and len(current_successor_re) > 0:
                    if len(current_successor_re) == 1:
                        current_successor_re = f'{current_successor_re}?'
                    else:
                        current_successor_re = f'({current_successor_re})?'
                
                tag_key = (f_id,t_id)
                if tag_key in tags:
                    tags[tag_key] = f'({tags[tag_key]}|{predecesor_current_re}{bucle_re}{current_successor_re})'
                else:
                    # RULE: ∅ | R = R
                    tags[tag_key] = f'{predecesor_current_re}{bucle_re}{current_successor_re}'
                
                if not f_id in successors:
                    successors[f_id] = set()
                successors[f_id].add(t_id)
                if not t_id in predecessors:
                    predecessors[t_id] = set()
                predecessors[t_id].add(f_id)
        
        for f_id in predecessors.get(current_id,set()):
            if f_id in successors:
                successors[f_id].discard(current_id)
        for t_id in successors.get(current_id,set()):
            if t_id in predecessors:
                predecessors[t_id].discard(current_id)
        
        if current_id in predecessors:
            del predecessors[current_id]
        if current_id in successors:
            del successors[current_id]
    
    for tag_key in tags:
        if tag_key in epsilons:
            if len(tags[tag_key]) == 1:
                tags[tag_key] = f'{tags[tag_key]}?'
            else:
                tags[tag_key] = f'({tags[tag_key]})?'

    tag_key = (_regex._start_state._id,final_id)
    if not tag_key in tags:
        if tag_key in epsilons:
            return ''
        raise ValueError('the given automaton is empty')
    return tags[tag_key]

cdef DFA _parse(str re):
    cdef Automaton aut
    cdef int line,column
    cdef Token end_token
    cdef BaseLexer _lexer = lexer
    cdef Parser _parser = parser
    cdef ASTWalker walker = regex_walker
    cdef RegexContext context = regex_context
    cdef list[RuntimeError] errors

    _lexer.load_text(re)
    while _lexer._move_next():
        _parser._try_parse(_lexer._current_token)
        line = _lexer._current_token._line
        column = _lexer._current_token._column
    end_token = Token('\x00',ReTokenType.SYMBOL,Symbol('\x00',True),line,column + 1) # type:ignore
    _parser._try_parse(end_token)
    if _parser._parsed:
        walker.walk(_parser._ast)
        errors = context.get_runtime_errors()
        if errors:
            _parser.reset()
            context.reset()
            raise RegexParsingException(errors)
        aut = (<RegexAST>_parser._ast)._get_automaton() # type:ignore
        _parser.reset()
        if isinstance(aut,NFA):
            aut = aut.to_deterministic()
        aut = aut.minimize() # type:ignore
        return aut # type:ignore
    _parser.reset()
    raise ValueError()