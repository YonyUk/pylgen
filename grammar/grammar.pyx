from typing import List,Tuple,Set
from hashlib import sha256
from common.types cimport Symbol

cdef class SymbolNotPresentInGrammarException(Exception):
    
    def __init__(self, Symbol symbol,*args: object) -> None:
        super().__init__(*args)
        self._msg = f'Symbol {symbol} not present in grammar'

cdef class Production:

    def __init__(self,Symbol head,list[Symbol] production):
        '''
        Args:
            head (Symbol): symbol that produces the given list of symbols
            production (List[Symbol])
        
        Raises:
            ValueError("head can't be a terminal symbol")
        '''
        cdef Symbol symbol
        cdef list[str] prod = [symbol._symbol for symbol in production]
        if head._is_terminal:
            raise ValueError("head can't be a terminal symbol")
        self._head = head
        self._production = production
        self._id = f'{head} -> {" ".join(prod)}'
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def head(self) -> Symbol:
        return self._head
    
    @property
    def production(self) -> List[Symbol]:
        return self._production
    
    def __str__(self) -> str:
        return self._id
    
    def __repr__(self) -> str:
        return self._id
    
    def __eq__(self, o) -> bool:
        cdef Production other
        if not isinstance(o,Production):
            return False
        other = o
        if other._head != self._head:
            return False
        return self._production == other._production
    
    def __hash__(self) -> int:
        cdef bytes digest = sha256(self._id.encode()).digest()
        cdef long long h = 0 # type:ignore
        cdef int i
        for i in range(8):
            h = (h << 8) | digest[i]
        return h # type:ignore

cdef class ProductionsSet:

    def __init__(self):
        self._productions = {}
        self._last_production_added = []
    
    @property
    def productions(self) -> List[List[Symbol]]:
        cdef list[list[Symbol]] result = []
        cdef list[Symbol] production

        for production in self._productions.values():
            result.append(production.copy())
        
        return result
    
    def __iadd__(self,production:Tuple[Symbol,...]) -> ProductionsSet:
        cdef Symbol symbol
        cdef list[str] p_ids = [symbol._symbol for symbol in production]
        cdef str p_id
        
        p_id = ','.join(p_ids)

        if not p_id in self._productions:
            self._productions[p_id] = list(production)

        self._last_production_added = self._productions[p_id]
        return self

cdef class Grammar:

    def __init__(self,Symbol start_symbol,str end_symbol = '\x00'):
        '''
        Args:
            start_symbol (Symbol): initial symbol of this grammar
        
        Raises:
            ValueError("start_symbol can't be terminal")
        '''
        self._start_symbol = start_symbol
        self._productions_by_symbol = {}
        self._end_symbol = Symbol(end_symbol,True) # type:ignore
        if self._start_symbol._is_terminal:
            raise ValueError("start_symbol can't be terminal")
        self._non_terminals = { self._start_symbol }
        self._terminals = { self._end_symbol }
        self._firsts = { self._start_symbol: set() }
        self._follows = { self._start_symbol: set() }
        self._productions = {}
        self._initialized = False # type:ignore
    
    @property
    def id(self) -> str:
        '''
        Returns:
            str: the id of this grammar
        '''
        cdef Symbol head
        cdef set[Production] productions
        cdef Production production
        cdef list[str] productions_ids = []
        cdef list[str] terminals_ids = []
        cdef list[str] non_terminals_ids = []

        for productions in self._productions_by_symbol.values():
            for production in productions:
                productions_ids.append(production._id)

        for head in self._terminals:
            if head._is_epsilon:
                terminals_ids.append(f'EPSILON-SYMBOL-{head._symbol}')
            else:
                terminals_ids.append(head._symbol)
        
        for head in self._non_terminals:
            non_terminals_ids.append(head._symbol)
        
        productions_ids.sort()
        terminals_ids.sort()
        non_terminals_ids.sort()

        return sha256(f"START-SYMBOL: {self._start_symbol} PRODUCTIONS: {'-'.join(productions_ids)} TERMINALS: {'-'.join(terminals_ids)} NON-TERMINALS: {'-'.join(non_terminals_ids)}".encode()).hexdigest()

    @property
    def productions(self) -> Set[Production]:
        '''
        Returns:
            Set[Production]: all the productions inside this grammar
        '''
        cdef set[Production] result = set()
        cdef set[Production] productions

        for productions in self._productions_by_symbol.values():
            result.update(productions)
        
        return result
    
    @property
    def terminals(self) -> Set[Symbol]:
        return set(self._terminals)
    
    @property
    def non_terminals(self) -> Set[Symbol]:
        return set(self._non_terminals)
    
    @property
    def start_symbol(self) -> Symbol:
        return self._start_symbol
    
    cdef bint _derives_in_epsilon(self,Symbol symbol):
        cdef Symbol sym

        for sym in self._firsts[symbol]:
            if sym._is_epsilon:
                return True # type:ignore
        return False # type:ignore

    cdef void _make_firsts(self):
        cdef bint change = True # type:ignore
        cdef Symbol non_terminal,terminal
        cdef list[Symbol] production
        cdef Symbol symbol,inner_symbol
        cdef ProductionsSet productions
        cdef int idx
        cdef bint epsilon = False # type:ignore

        while change:
            change = False # type:ignore
            # for non terminal
            for non_terminal in self._non_terminals:
                productions = self._productions[non_terminal]
                # for production
                for production in productions._productions.values():
                    symbol = production[0]
                    # check if symbol derive in epsilon
                    epsilon = self._derives_in_epsilon(symbol)
                    # if symbol is a terminal and is not epsilon symbol and it is not already in
                    # the set first of the current non terminal
                    if symbol._is_terminal and not symbol._is_epsilon and not symbol in self._firsts[non_terminal]:
                        # add it to the set first of the current non terminal and set change to true
                        self._firsts[non_terminal].add(symbol)
                        change = True # type:ignore
                    # if symbol is not a terminal
                    elif not symbol._is_terminal:
                        # adds every symbol in its set first, except the epsilon symbol
                        for inner_symbol in self._firsts[symbol]:
                            if not inner_symbol in self._firsts[non_terminal] and not inner_symbol._is_epsilon:
                                self._firsts[non_terminal].add(inner_symbol)
                                change = True # type:ignore
                    # starts for the second symbol in the production
                    idx = 1
                    # while the the current symbol derive in epsilon
                    while epsilon and idx < len(production):
                        # add every symbol in set first of the current symbol
                        for symbol in self._firsts[production[idx]]:
                            if not symbol._is_epsilon and not symbol in self._firsts[non_terminal]:
                                self._firsts[non_terminal].add(symbol)
                                change = True # type:ignore
                        # check if the current symbol derives in expsilon
                        epsilon = self._derives_in_epsilon(production[idx])
                        idx += 1
                    
                    if idx == len(production) and epsilon and not self._epsilon in self._firsts[non_terminal]:
                        self._firsts[non_terminal].add(self._epsilon)
                        change = True # type:ignore
        self._initialized = True # type:ignore

    # cdef void _make_follows(self,str end_symbol):
    #     cdef bint change = True # type:ignore
    #     cdef Production production
    #     cdef set[Production] productions
    #     self._follows[self._start_symbol] = {Symbol(end_symbol,True)} # type:ignore
        
    #     while change:
    #         change = False # type:ignore
    #         for production in self.
    
    cpdef set[Symbol] first(self,list[Symbol] production):
        cdef set[Symbol] result = set()
        cdef bint derives_in_epsilon = True # type:ignore
        cdef int idx = 0
        cdef Symbol symbol

        if not self._initialized:
            self._make_firsts()

        while derives_in_epsilon and idx < len(production):
            if not production[idx] in self._terminals and not production[idx] in self._non_terminals:
                raise SymbolNotPresentInGrammarException(production[idx])
            for symbol in self._firsts[production[idx]]:
                if not symbol._is_epsilon and not symbol in result:
                    result.add(symbol)
            derives_in_epsilon = self._derives_in_epsilon(production[idx])
            idx += 1
        
        if derives_in_epsilon and idx == len(production):
            result.add(self._epsilon)
        
        return result

    def __getitem__(self,head:Symbol) -> ProductionsSet:
        cdef Symbol h = head
        if h._is_terminal:
            raise ValueError("head can't be a terminal symbol")
        if h in self._productions:
            return self._productions[h]
        
        return ProductionsSet()
    
    def __setitem__(self,head:Symbol,productions:ProductionsSet) -> None:
        cdef Symbol symbol
        cdef ProductionsSet p = productions
        cdef Symbol h = head

        if h._is_terminal:
            raise ValueError("head can't be a terminal symbol")

        if not h in self._non_terminals:
            self._non_terminals.add(h)
            self._firsts[h] = set()
            self._follows[h] = set()
        
        for symbol in p._last_production_added:
            if symbol._is_terminal:
                if not symbol in self._terminals:
                    self._terminals.add(symbol)
                    self._firsts[symbol] = { symbol }
                    if symbol._is_epsilon:
                        if not self._epsilon:
                            self._epsilon = symbol
                        elif self._epsilon != symbol:
                            raise ValueError('Only can exists one epsilon symbol')
            else:
                if not symbol in self._non_terminals:
                    self._non_terminals.add(symbol)
                    self._firsts[symbol] = set()
                    self._follows[symbol] = set()

        self._productions[h] = productions

        if not h in self._productions_by_symbol:
            self._productions_by_symbol[h] = set()
        
        self._productions_by_symbol[h].add(Production(h,p._last_production_added))
        self._initialized = False # type:ignore