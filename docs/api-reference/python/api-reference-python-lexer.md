# Module `lexer`

## Submodule `lexer.base_lexer`

> ### `LexerNotInitializedException`

Exception raised when an attemp is made to obtain the internal `DFA` without initializing the lexer first. Inherits from `Exception` (`LexerNotInitializedException(Exception)`).

> ### `LexerNotTokensProvidedException`

Exception raised when an attemp is made to initialize the lexer without any token automata provided. Inherits from `Exception` (`LexerNotTokensProvidedException(Exception)`).

> ### `BaseLexer`

Base class for a lexer.

 - `__init__(get_symbol_function, ignore_pattern)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: mapping function that maps a tuple `(Any,str)` to a `Symbol`. The mapping function must be annotated with the specific signature `Callable[[Any, str], Symbol]`, where the first argument annotation must be a subclass of `TokenType`.
        - `ignore_pattern (DFA)`: the `DFA` used to skip text patterns.
    
    - Raises: `ValueError` if the signature of `get_symbol_function` is invalid.

!!! warning
    This class is not meant to be used directly.

#### Properties

 - `dfa (DFA)`: returns the internal `DFA` used for tokenization.
    - Raises: `LexerNotInitializedException` if not initialized.

 - `tokens (Iterable[Token])`: initializes (if needed) and iterates over all tokens skipping ignored tokens.

#### Methods

 - `initialize()`: initializes the lexer.
    - Raises: `LexerNotTokensProvidedException` if there are no automata provided for tokens.

 - `load_text(text)`: prepares the lexer for tokenization.

## Submodule `lexer.lexer`

> ### `Lexer`

Subclass of `BaseLexer`.

 - `__init__(get_symbol_function, ignore_pattern)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: analogous to `BaseLexer.__init__`.
        - `ignore_pattern (str)`: regex of the tokens to skip in the tokenization.

#### Properties

 - `errors (Set[LexicalError])`: a copy of the lexical errors detected during the tokenization.
 
 - `tokens (Iterable[Token])`: analogous to `BaseLexer.tokens`, besides normal tokens, emits the EOF token (if provided) at the end.

#### Methods

 - `clear_errors()`: clears all the lexical errors detected.

 - `set_eof_token(symbol, type_)`: sets the `EOF` token to be emmited at the end of the tokenization.
    - Args:
        - `symbol (str)`: the text of the symbol for the `EOF` token. The symbol of `EOF` token is always a terminal.
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
    
    - Raises: `ValueError` if `type_` does not belong to the enum of the annotation for the first argument of `get_symbol_function`.

 - `add_token_regex(priority, type_, re)`: compiles `re`, assigns `type_` to accepting states of the compilation result of `re` and registers the token.
    - Args:
        - `priority (int)`
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
        - `re (str)`: the regex for the token.

 - `add_rule(type_, rule)`: adds a `LexicalRule` to the set associated with `type_`.
    - Args:
        - `type_ (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
        - `rule (LexicalRule)`: the rule to be applied during tokenization.

> ### `IdentedLexer`

Subclass of `Lexer` specialized on languages with identation.

 - `__init__(get_symbol_function, ignore_pattern)`
    - Args:
        - `get_symbol_function (Callable[[Any, str], Symbol])`: analogous to `BaseLexer.__init__`.
        - `ignore_pattern (str)`: regex of the tokens to skip in the tokenization.

#### Methods

- `set_ident(ident_type)`: sets the set of tokens associated to identation (`'    ', '\t'`, etc.) 
    - Args:
        - `ident_type (Any)`: must be a member of the enum type declared in the annotation for the first argument of `get_symbol_function`.
    
    - Raises: `ValueError` if not in the enum.

 - `set_indent_symbol(symbol)`: sets the symbol for the `INDENT` token.
    - Args:
        - `symbol (Symbol)`

 - `set_dedent_symbol(symbol)`: sets the symbol for the `DEDENT` token.
    - Args:
        - `symbol (Symbol)`

 - `set_text_sanitize_function(sanitaze_function)`: stores the sanitization function, if provided, is automatically called during `IdentedLexer.load_text(text)`.
    - Args:
        - `sanitaze_function (Callable[[str],str])`.