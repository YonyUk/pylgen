# Acknowledgments

PyLGEN is built on decades of work in formal language theory and compiler construction. This page credits the sources that shaped its design.

## Algorithms and theory

| Area | Source |
| :--- | :--- |
| Regular expressions and finite automata | Kleene, S. C. (1956). *Representation of events in nerve nets and finite automata.* |
| Thompson construction | Thompson, K. (1968). *Regular expression search algorithm.* |
| Subset construction (NFA → DFA) | Rabin, M. O., and Scott, D. (1959). *Finite automata and their decision problems.* |
| DFA minimization | Hopcroft, J. E. (1971). *An n log n algorithm for minimizing states in a finite automaton.* |
| LR parsing | Knuth, D. E. (1965). *On the translation of languages from left to right.* |
| LALR(1) | DeRemer, F. L. (1969). *Practical translators for LR(k) languages.* |
| LALR(1) lookahead propagation | DeRemer, F., and Pennello, T. (1982). *“Efficient Computation of LALR(1) Look-ahead Sets.”* ACM Transactions on Programming Languages and Systems, 4(4), 615–649.|
| Attributed grammars | Knuth, D. E. (1968). *Semantics of context-free languages.* |
| Syntax-directed translation | Aho, A. V., Lam, M. S., Sethi, R., and Ullman, J. D. *Compilers: Principles, Techniques, and Tools* (the “Dragon Book”). |

## Tools and libraries

 - **Cython** — for compiling PyLGEN’s core to native extensions.
 - **NumPy** — used in the VecLang example for vector operations.
 - **pyvis** and **networkx** — for the interactive HTML visualizations in the `visual` module.

## People

PyLGEN is created and maintained by [YonyUk](https://github.com/yonyuk). Contributions from the community are listed in the repository’s commit history and release notes.