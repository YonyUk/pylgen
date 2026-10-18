# Module `grammar`

## Submodule `grammar.grammar`

> ### `SymbolNotPresentInGrammarException`

Exception raised when a symbol is not found in the current grammar (inherits from `Exception`).

 - `__init__(symbol: Symbol, *args)`

> ### `Production`

Class that represents a grammar production.

 - `__init__(head, production)`
    - Args:
        - `head (Symbol)`: left-hand side of the grammar production.
        - `production (List[Symbol])`: right-hand side of the grammar production.
    
    - Raises: `ValueError("head can't be a terminal symbol")` if `head.is_terminal` is `True`.

#### Properties

 - `id (str)`: the id of the production (`f'{head} -> {" ".join(prod)}'`).
 - `head (Symbol)`
 - `production (List[Symbol])`

#### Methods

 - `__str__`: returns `id`.
 - `__repr__`: returns `id`.
 - `__eq__`: equality by `head` and `production`.
 - `__hash__`: returns the precomputed hash.

> ### `ProductionsSet`

Class that contains the productions for an specific non-terminal.

 - `__init__()`

#### Properties

 - `productions (List[List[Symbol]])`: copy of each production.

#### Methods

 - `__iadd__(production)`: adds a production if not present using the operator `+=`.
    - Args:
        - `production (Tuple[Symbol,...])`

> ### `AttributedProductionsSet`

Version of `ProductionsSet` for attributed grammars. Inherits from `ProductionsSet` (`AttributedProductionsSet(ProductionsSet)`).

 - `__init__()`

#### Methods

 - `__iadd__(self, production_redutor_pair)`: adds an attributed production if not present using the operator `+=`.
    - Args:
        - `production_reductor_pair (Tuple[Tuple[Symbol, ...],Callable[[ASTListView],AST]])`: a pair `(production,reductor)`. `reductor` is the function that the parser will call when it reduces by this production.
    
    - Raises: `ValueError` if the `reductor`'s signature is not `(ASTListView) -> AST`.

> ### `Grammar`

Base class for a grammar.

 - `__init__(start_symbol, end_symbol = '\x00')`
    - Args:
        - `start_symbol (Symbol)`: the start symbol of the grammar.
        - `end_symbol (str)`: the `EOF` symbol for the parser, internally the grammar stores a terminal symbol with value `end_symbol`.
    
    - Raises: `ValueError("start_symbol can't be terminal")` if `start_symbol.is_terminal` is `True`.

#### Properties

 - `id (str)`: based in the current productions, terminals, non-terminals and any structural information of the grammar itself.
 - `productions (Set[Production])`: the current productions of the grammar.
 - `terminals (Set[Symbol])`: the current terminals of the grammar (including the `EOF` symbol created using `end_symbol`).
 - `non_terminals (Set[Symbol])`: the current non-terminals of the grammar.
 - `symbols (Set[Symbol])`: the current symbols present in the grammar (including the `EOF` symbol created using `end_symbol`).
 - `start_symbol (Symbol)`: the start symbol.
 - `end_symbol (Symbol)`: the `EOF` symbol.

#### Static Methods

 - `IsLeftRegular(g)`: returns `True` if the grammar is left-regular.
    - Args:
        `g (Grammar)`

 - `IsRightRegular(g)`: returns `True` if the grammar is right-regular.
    - Args:
        `g (Grammar)`

 - `IsRegular(g)`: returns `True` if the grammar is either left‑ or right‑regular.
    - Args:
        `g (Grammar)`

 - `AugmentGrammar(g)`: returns an augmented version of `g`.
    - Args:
        `g (Grammar)`

 - `Reverse(g)`: reverses the production bodies of every rule, yielding a grammar that recognizes the reversed language.
    - Args:
        `g (Grammar)`

#### Methods

 - `first(production)`: returns the `FIRST` set of the given sequence of symbols.
    - Args:
        `production (List[Symbol])`
    
    - Raises: `SymbolNotPresentInGrammarException` if any symbol is not present in the grammar.

 - `follow(symbol)`: returns the `FOLLOW` set of the given symbol.
    - Args:
        - `symbol (Symbol)`

    - Raises: `SymbolNotPresentInGrammarException` if any symbol is not present in the grammar.

 - `to_dict()`: returns a plain representation of the grammar in a dictionary.

 - `__getitem__(head)`: returns the `ProductionsSet` associated to the non-terminal `head`, via `[`...`]` syntax (eg., `G[nt]`).
    - Args:
        `head (Symbol)`

    - Raises: `ValueError("head can't be a terminal symbol")` if `head.is_terminal` is `True`.
 
 - `__setitem__(head, productions)`: sets the `ProductionsSet` for the non-terminal `head` via `[`...`]` syntax.
    - Args:
        - `head (Symbol)`
        - `productions (ProductionsSet)`
    
    - Raises:
        - `ValueError("head can't be a terminal symbol")` if `head.is_terminal` is `True`.
        - `ValueError('Only can exists one epsilon symbol')` if there is an epsilon symbol in productions different from the current present in the grammar (if exists).

!!! tip
    This method, in combination with `ProductionsSet.__iadd__`, is what allows to use the syntax `G[S] += A,a` to add productions to a grammar.

> ### `AttributedGrammar(Grammar)`

Version of `Grammar` for attributed grammars. Inherits from `Grammar` (`AttributedGrammar(Grammar)`).

 - `__init__(start_symbol, end_symbol='\x00')`: analogous to `Grammar.__init__`.

#### Methods

 - `get_reductor(production)`: gets the associated reductor the given production.
    - Args:
        - `production (Production)`
    
    - Raises: `KeyError` if there's no exists any reductor associated to the given production.

 - `__getitem__(head)`: returns the `AttributedProductionsSet` associated to the non-terminal `head`, via `[`...`]` syntax (eg., `G[nt]`).
    - Args:
        `head (Symbol)`

    - Raises: `ValueError("head can't be a terminal symbol")` if `head.is_terminal` is `True`.
 
 - `__setitem__(head, productions)`: sets the `AttributedProductionsSet` for the non-terminal `head` via `[`...`]` syntax.
    - Args:
        - `head (Symbol)`
        - `productions (ProductionsSet)`
    
    - Raises:
        - `ValueError("head can't be a terminal symbol")` if `head.is_terminal` is `True`.
        - `ValueError('Only can exists one epsilon symbol')` if there is an epsilon symbol in productions different from the current present in the grammar (if exists).

!!! tip
    This method, in combination with `AttributedProductionsSet.__iadd__`, is what allows to use the syntax `G[S] += (A,a),reductor` to add productions to a grammar.