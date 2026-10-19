# Module `visual`

## Main Submodule (`__init__.py`)

> ### Public Functions

 - `draw_automaton(automaton, **kwargs)`: creates an interactive graph in a html file.
    - Args:
        - `automaton (Automaton)`
        - `**kwargs`
            - `filename (str)`: name of the html file that will be generated.
            - `show (bool)`: if `True`, the generated file is opened in the browser.
            - `cache (bool)`: if `True`, the external links in the file are embeded.
            - `physics (bool)`: `pyvis` option (controls physics).
            - `select_menu (bool)`: `pyvis` option (enables the select menu).
            - `filter_menu (bool)`: `pyvis` option (enables the filter menu).
            - `nodes (bool)`: `pyvis` option (enables nodes options menu).
            - `edges (bool)`: `pyvis` option (enables edges options menu).
            - `as_tree (bool)`: `pyvis` option (sets a tree layout).

    - Raises: `ValueError` for each kwarg with incorrect type or if `cache=True` without `CACHE_FILE`.

 - `draw_lexer(lexer, **kwargs)`: delegates to `draw_automaton(lexer.dfa, ...)`, `**kwargs` argument is analogous to `draw_automaton`.

 - `draw_ast(ast, **kwargs)`: creates an interactive graph in a html file,`**kwargs` argument is analogous to `draw_automaton`.
    - Args:
        - `ast (AST)`
    
    - Raises: `ValueError` for each kwarg with incorrect type or if `cache=True` without `CACHE_FILE`.

 - `draw_parse_tree(tree, **kwargs)`: creates an interactive graph in a html file,`**kwargs` argument is analogous to `draw_automaton`.
    - Args:
        `tree (ParseTreeNode)`

    - Raises: `ValueError` for each kwarg with incorrect type or if `cache=True` without `CACHE_FILE`.

 - `show_propagation_edges_table(g, **kwargs)`: creates an interactive graph in a html file, with the info of the propagation edges for a LALR(1) parser building.
    - Args:
        - `g (Grammar)`
        - `**kwargs`:
            - `filename (str)`
            - `show (bool)`
            - `cache (bool)`
    
    - Raises: `ValueError` for each kwarg with incorrect type or if `cache=True` without `CACHE_FILE`.

 - `lr_inspect_grammar(g, type_=ParserType.LALR1, **kwargs)`: creates an interactive graph in a html file, exploring the grammar. Returns `True` if any conflict is found.
    - Args:
        - `g (Grammar)`
        - `**kwargs`:
            - `filename (str)`
            - `show (bool)`
            - `cache (bool)`
            - `report (bool)`: when `True`, generates a html file with the info.

    - Raises: `ValueError` for each kwarg with incorrect type or if `cache=True` without `CACHE_FILE`, or `show=True` and `report=False`.

 - `set_cache_file(filename)`: Sets the global cache file.
    - Args:
        - `filename (str)`

    - Raises: `ValueError` if `filename` is empty.

!!! warning
    if `filename` exists, it will be overwritten.

## Submodule `visual.table`

> ### HTML templates (compressed with **`LZMA`**) used to generate reports:

 - `propagation_edges_template`
 - `propagation_edges_row_template`
 - `state_details_template`
 - `goto_action_tables_template`

> ### Functions

 - `build_propagation_edges_table(g)`: builds the html table of lookahead propagation edges.
    - Args:
        - `g (Grammar)`

 - `build_action_goto_html_tables(g, type_)`: returns a tuple `(HTML content,flag)`. Delegates on `build_action_goto_lalr_tables`, `build_action_goto_slr_tables` and `build_action_goto_lr1_tables`, depending on `type_`.
    - Args:
        - `g (Grammar)`
        - `type_ (ParserType)`
    - Raises: `NotImplementedError` for unsupported types.