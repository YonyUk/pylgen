# Pause & Reflect - Visualizing Our Progress

We've reached a solid milestone. With the lexer, grammar, and reductors in place, our pipeline is now capable of transforming raw source code into a structured Abstract Syntax Tree (AST). It's the perfect moment to take a step back, appreciate what we've built, and, most importantly, verify that everything is working as expected.

Before diving into semantic analysis and execution, let's explore a few visualization options. Being able to ***see*** the tree your parser produces is not only satisfying, but it's also an invaluable **debugging** aid. You can catch structural issues early, long before you start executing code.

## Putting It All Together

With the lexer, grammar, reductors, and AST nodes fully defined, we've reached the moment where everything converges into a single, coherent pipeline. The script below, our `main.py`, loads a sample expression, runs it through the entire lexer-parser chain, and produces visual representations of both the parse tree and the abstract syntax tree.

File: `main.py`
```python
from arithmetic_interpreter.grammar import parser
from arithmetic_interpreter.lexer import lexer
from pylgen.visual import draw_ast,draw_parse_tree_from_parser


text = '(1 + 3)*9 - 5%3'

# Feed the source code into the lexer
lexer.load_text(text)

# Instruct the parser to retain parse tree information during analysis
parser.set_draw_parse_tree_flag(True)

# Parse the token stream and obtain the final AST
ast = parser.parse(lexer.tokens)

# Generate an interactive HTML visualization of the AST
draw_ast(ast,show=True)

# Generate an interactive HTML visualization of the full parse tree
draw_parse_tree_from_parser(parser,show=True)
```

> ### What's happening under the hood?

 - `lexer.load_text(text)`: feeds the raw source string into the lexer, ready for tokenization.
 - `parser.set_draw_parse_tree_flag(True)`: activates a flag that instructs the parser to record every step of the syntactic derivation. This is essential for building the complete parse tree later.
 - `parser.parse(lexer.tokens)`: consumes the token stream, applies the grammar rules and reductors, and returns the root node of the AST.
 - `draw_ast` and `draw_parse_tree_from_parser`: these are the star of the show from the `pylgen.visual` submodule.

> ### Spotlight on [`pylgen.visual`](../api/visual/visual.md) - Native Visualization Made Simple

One of PyLGEN's most convenient built-in utilities is its **visualization submodule**. Instead of requiring you to install external graphing libraries or manually export data, `pylgen.visual` provides ready-to-use functions that generate **standalone, interactive HTML documents** directly from your parser and AST.

 - `draw_ast(ast,show=True)`: takes the root of your AST and generates a fully interactive, zoomable tree visualization. The `show=True` flag automatically opens it in your default web browser, perfect for quick inspections.
 - `draw_parse_tree_from_parser(parser,show=True)`: does the same for the entire parse tree, including every terminal and non-terminal symbol involved in the derivation. This gives you an x-ray view of exactly how your grammar consumed the input, rule by rule.

The best part? These HTML files are self-contained, You can save them, share them, or embed them directly into documentation, just like we've done, below. No external servers, no complicated setup. Just clean, visual representation of your language's internal structure.

!!! important
    The generated HTML files are **single, portable documents** that you can **save, share, or embed**. However, by default, `draw_ast` and `draw_parse_tree_from_parser` reference external resources, the **vis.js library** and its associated CSS styles, loaded from online CDNs via `<script>` and `<link>` tags.

    This means that unless you use the embedding option, an internet connection is required when opening the generated HTML to download these resources. The visualization will not render properly in offline environments without that initial fetch (or an existing browser cache).

!!! info
    PyLGEN's visual submodule does offer a mechanism to embed these resources directly into the HTML output, inlining all JavaScript and CSS, to produce truly offline‑capable files. In this tutorial, we have used that embedding option when generating the visualizations. Consequently, the interactive trees you see in the iframes below are fully self-contained; they include everything they need internally and will render flawlessly without any external network requests.

## Visualizing the results

For the sample expression `(1 + 3)*9 - 5%3`, the functions generate the following interactive views:

> ### Parse Tree (Full Derivation)
> Every rule application is captured, showing exactly how the grammar broke down the input.

<iframe src="../../images/section-1/parse tree.html" width="100%" height="400" style="border:none;"></iframe>

> ### Abstract Syntax Tree (Simplified Structure)
> Parentheses and intermediate non-terminals are stripped away, leaving only the core operational structure.

<iframe src="../../images/section-1/ast.html" width="100%" height="400" style="border:none;"></iframe>

Notice how the AST is leaner and more direct than the parse tree, it omits details like parentheses and single‑step reductions, focusing purely on the semantic essence of the expression. The parse tree, on the other hand, is a faithful record of the syntactic derivation, invaluable for debugging grammar ambiguities or precedence issues.

!!! tip "Visual Debugging"
    When hovering over any node in the AST visualization, a tooltip appears displaying the **node’s public**, **JSON‑serializable** properties such as its symbol, line/column, and any additional data like the variable name or operator. This allows you to inspect the node’s internal state instantly without referring back to the source code or reading the AST class definitions.

## What this Confirms?

By visually inspecting both trees, you can immediately verify:

 - The lexer classified every token correctly.
 - The grammar applied the expected rules with the correct precedence (e.g., multiplication before subtraction).
 - The reductors assembled the intended AST nodes in the right order.


## What's Next?

With our pipeline fully validated and visualized, we have a rock‑solid foundation. The next phase is **Semantic Analysis**, where we'll check that variables are defined before, followed by Execution, where we'll finally evaluate expressions, manage a symbol table, and bring our REPL to life.

Take a moment to experiment: change the text variable in `main.py` and re-run the script. Watch how both trees adapt to new expressions. It's a fantastic way to internalize how your language design translates into actual data structures, and the `pylgen.visual` module makes that exploration effortless. Ready to move forward? Let's go!