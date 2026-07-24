# Step 3: Bringing Meaning to the Tree (Semantic Analysis)

With our AST ready and our parser validated, we've reached the stage where we move beyond structure and into **meaning**. Lexical and syntactic analysis tell us ***how*** the code is written; semantic analysis tells us ***what*** it means and ***whether*** it makes sense.

In a typical compiler pipeline, semantic analysis handles tasks like:

 - **`Type checking`**: ensuring operations are performed on compatible types.
 - **`Scope resolution`**: verifying that variables are declared before use.
 - **`Error detection`**: cacthing nonsensical operations like division by zero at compile time (when possible).

For our REPL, we'll also combine **semantic analysis** with **evaluation**, after all, we're building an **interpreter**. But before we compute values, we must ensure that the computation is valid.

