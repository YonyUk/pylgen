# Module `grammar`

## Submodule `grammar.grammar`

> ### `SymbolNotPresentInGrammarException`

Exception raised when a symbol is not found in the current grammar (inherits from `Exception`).

 - `__init__(symbol: Symbol, *args)`

#### Properties

 - `_msg (cdef str)`: message of the exception.

> ### `Production`

Class that represents a grammar production.

 - `__init__(head, production)`
    - Args:
        - `head (Symbol)`: left-hand side of the grammar production.
        - `production (List[Symbol])`: right-hand side of the grammar production.
    
    - Raises: `ValueError("head can't be a terminal symbol")` if `head._is_terminal` is `True`.

#### Properties

 - `_id (cdef str)`: the id of the production (`f'{head} -> {" ".join(prod)}'`).
 - `_head (cdef Symbol)`
 - `_production (cdef list[Symbol])`
 - `_hash (cdef int)`: precomputed hash.

> ### `ProductionsSet`

Class that contains the productions for an specific non-terminal.

 - `__init__()`

#### Properties

 - `_productions (cdef dict[str,list[Symbol]])`: mapping of productions.
 - `_last_production_added (cdef list[Symbol])`: the last production added (used internally by `Grammar`).

#### Methods

 - `cdef void _add_production(production)`: adds a new production if not present.
    - Args:
        - `production (list[Symbol])`

> ### `AttributedProductionsSet`

Version of `ProductionsSet` for attributed grammars. Inherits from `ProductionsSet` (`AttributedProductionsSet(ProductionsSet)`).

 - `__init__()`

#### Properties

 - `_last_reductor_added (cdef object)`: the reductor associated to `_last_production_added` (used internally by `AttributedGrammar`).

#### Methods

 - `cdef void _add_attributed_production(self,list[Symbol] production,object reductor)`:adds an attributed production if not present.
    - Args:
        - `production (list[Symbol])`
        - `reductor (object)`: the function that the parser will call when it reduces by this production.

> ### `Grammar`

Base class for a grammar.

 - `__init__(start_symbol, end_symbol = '\x00')`
    - Args:
        - `start_symbol (Symbol)`: the start symbol of the grammar.
        - `end_symbol (str)`: the `EOF` symbol for the parser, internally the grammar stores a terminal symbol with value `end_symbol`.
    
    - Raises: `ValueError("start_symbol can't be terminal")` if `start_symbol._is_terminal` is `True`.

#### Properties

 - `_start_symbol (cdef Symbol)`: start symbol of the grammar.
 - `_end_symbol (cdef Symbol)`: `EOF` symbol of the grammar (used by the parser).
 - `_terminals (cdef set[Symbol])`: the current terminals of the grammar (including the `EOF` symbol created using `end_symbol`).
 - `_non_terminals (cdef set[Symbol])`:the current non-terminals of the grammar.
 - `_follows (cdef dict[Symbol,set[Symbol]])`: used for cache in the `FOLLOW` set computation.
 - `_firsts (cdef dict[Symbol,set[Symbol]])`: used for cache in the `FIRST` set computation.
 - `_productions (cdef dict[Symbol,ProductionsSet])`: mapping of the productions set of each symbol.
 - `_productions_by_symbol (cdef dict[Symbol,set[Production]])`: mapping of the productions of each symbol for direct access.
 - `_firsts_computed (cdef bint)`: flag to invalidate cache for `FIRST` sets already computed.
 - `_follows_computed (cdef bint)`: flag to invalidate cache for `FOLLOW` sets already computed.
 - `_epsilon (cdef Symbol)`: the epsilon symbol of the grammar (if exists).
 - `_symbols (cdef set[Symbol])`: symbols of the grammar.

#### Methods

 - `cdef bint _derives_in_epsilon(symbol)`: returns `True` if `symbol` can produce the epsilon symbol following the productions rules of the grammar.
    - Args:
        - `symbol (Symbol)`

 - `cdef void _make_firsts()`: initializes the cache for the `FIRST` sets computation.

 - `cdef void _make_follows()`: initializes the cache for the `FOLLOW` sets computation.

 - `cdef void _add_production(head,production)`: adds a production if not present in grammar.
    - Args:
        - `head (Symbol)`
        - `productions (ProductionsSet)`
    
    - Raises:
        - `ValueError("head can't be a terminal symbol")` if `head._is_terminal` is `True`.
        - `ValueError('Only can exists one epsilon symbol')` if there is an epsilon symbol in productions different from the current present in the grammar (if exists).
 
 - `cdef str _id()`: computes the id of the grammar based in the current productions, terminals, non-terminals and any structural information of the grammar itself.

 - `cpdef set[Symbol] first(production)`: returns the `FIRST` set of the given sequence of symbols.
    - Args:
        `production (list[Symbol])`
    
    - Raises: `SymbolNotPresentInGrammarException` if any symbol is not present in the grammar.

 - `cpdef set[Symbol] follow(symbol)`: returns the `FOLLOW` set of the given symbol.
    - Args:
        - `symbol (Symbol)`

    - Raises: `SymbolNotPresentInGrammarException` if any symbol is not present in the grammar.

 - `cpdef dict to_dict()`: returns a plain representation of the grammar in a dictionary.

> ### `AttributedGrammar(Grammar)`

Version of `Grammar` for attributed grammars. Inherits from `Grammar` (`AttributedGrammar(Grammar)`).

 - `__init__(start_symbol, end_symbol='\x00')`: analogous to `Grammar.__init__`.

#### Properties

 - `_reductors_by_production (cdef dict[Production,object])`: mapping of the reductors by the productions that triggers it.

#### Methods

 - `cpdef object get_reductor(production)`: gets the associated reductor the given production.
    - Args:
        - `production (Production)`
    
    - Raises: `KeyError` if there's no exists any reductor associated to the given production.

 - `cdef void _add_attributed_production(head,production,reductor)`: adds a production with its reductor if not present in grammar.
    - Args:
        - `head (Symbol)`
        - `productions (ProductionsSet)`
        - `reductor (object)`
    
    - Raises:
        - `ValueError("head can't be a terminal symbol")` if `head._is_terminal` is `True`.
        - `ValueError('Only can exists one epsilon symbol')` if there is an epsilon symbol in productions different from the current present in the grammar (if exists).

> ### Module functions

 - `cdef bint _is_left_regular(g)`: returns `True` if the grammar is left-regular.
    - Args:
        `g (Grammar)`

 - `cdef bint _is_right_regular(g)`: returns `True` if the grammar is right-regular.
    - Args:
        `g (Grammar)`

 - `cdef Grammar _augment_grammar(g)`: returns an augmented version of `g`.
    - Args:
        `g (Grammar)`

 - `cdef Grammar _reverse_grammar(g)`: reverses the production bodies of every rule, yielding a grammar that recognizes the reversed language.
    - Args:
        `g (Grammar)`