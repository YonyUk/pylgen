from typing import List,Tuple,Set
from hashlib import sha256
from common.types cimport Symbol

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
        self._non_terminals = set()
        self._terminals = set()
    
    @property
    def productions(self) -> List[List[Symbol]]:
        cdef list[list[Symbol]] result = []
        cdef list[Symbol] production

        for production in self._productions.values():
            result.append(production.copy())
        
        return result
    
    def __iadd__(self,production:Tuple[Symbol,...]) -> ProductionsSet:
        cdef Symbol symbol
        cdef list[str] p_ids = []
        cdef str p_id

        for symbol in production:
            if symbol._is_terminal and not symbol in self._terminals:
                self._terminals.add(symbol)
            elif not symbol._is_terminal and not symbol in self._non_terminals:
                self._non_terminals.add(symbol)
            p_ids.append(symbol._symbol)
        
        p_id = ','.join(p_ids)

        if not p_id in self._productions:
            self._productions[p_id] = list(production)
        
        return self

cdef class Grammar:

    def __init__(self,Symbol start_symbol):
        '''
        Args:
            start_symbol (Symbol): initial symbol of this grammar
        
        Raises:
            ValueError("start_symbol can't be terminal")
        '''
        self._start_symbol = start_symbol
        self._non_terminals = {self._start_symbol}
        self._terminals = set()
        self._firsts = {}
        self._follows = {}
        self._productions = {}
        self._initialized = False # type:ignore
    
    @property
    def id(self) -> str:
        '''
        Returns:
            str: the id of this grammar
        '''
        cdef Symbol head
        cdef ProductionsSet productions
        cdef list[Symbol] production
        cdef list[str] productions_ids = []
        cdef list[str] terminals_ids = []
        cdef list[str] non_terminals_ids = []

        for head,productions in self._productions.items():
            for production in productions._productions.values():
                productions_ids.append(Production(head,production).id)
        
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
        cdef Symbol head
        cdef ProductionsSet productions
        cdef list[Symbol] production

        for head,productions in self._productions.items():
            for production in productions._productions.values():
                result.add(Production(head,production))
        
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
        
        for symbol in p._terminals:
            if not symbol in self._terminals:
                self._terminals.add(symbol)
        
        self._productions[h] = productions