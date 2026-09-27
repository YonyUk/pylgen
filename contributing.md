# Contributing to PyLGEN

First off, thank you for considering a contribution. PyLGEN is a pedagogical project, and every issue, pull request, or suggestion helps it grow.

This document explains how to report bugs, propose features, set up your development environment, and submit changes. It is meant to be practical, not bureaucratic. If something here is unclear, open an issue and we will fix it.

## Table of Contents

 - [Code of Conduct](#code-of-conduct)
 - [Reporting Bugs](#reporting-bugs)
 - [Suggesting Features](#suggesting-features)
 - [Development Setup](#development-setup)
 - [Project Structure](#project-structure)
 - [Running the Tests](#running-the-tests)
 - [Coverage](#coverage)
 - [Building the Documentation](#building-the-documentation)
 - [Style Guidelines](#style-guidelines)
 - [Commit Conventions](#commit-conventions)
 - [Branching Strategy](#branching-strategy)
 - [Pull Request Process](#pull-request-process)
 - [Release Process](#release-process)

## Code of Conduct

Be kind, be patient, be constructive. This project is maintained by a small team, and contributions come from people with different levels of experience. Harassment, dismissiveness, or gatekeeping will not be tolerated.

If you witness or experience unacceptable behavior, contact the maintainer at `yonatanjoseguerraperez@gmail.com`. All reports will be handled with discretion.

## Reporting Bugs

Before opening an issue, please:

 - `1`. Search the [existing issues](https://github.com/yonyuk/pylgen/issues) to
   avoid duplicates.
 
 - `2`. Verify that the bug still occurs on the latest `main` branch.
 
 - `3`. Reduce the problem to a minimal reproducible example, if possible.

When opening an issue, include:

 - **What you did**: the exact commands or code that triggered the bug.
 
 - **What you expected**: the behavior you anticipated.
 
 - **What happened**: the actual behavior, with the full traceback if applicable.
 
 - **Environment**: Python version, PyLGEN version, OS, and whether you are
  running pure Python or compiled Cython.

If the bug is in the Cython-compiled code and not reproducible in pure Python, say so explicitly. It saves a lot of debugging time.

## Suggesting Features

Feature suggestions are welcome, but they should fit the scope of the project. PyLGEN is a framework for building interpreters, not a general-purpose compiler toolchain. Before proposing a feature, ask yourself:

 - Does it belong in the core pipeline, or in a downstream tool?

 - Does it fit the pedagogical philosophy of exposing every stage?
 
 - Does it require breaking changes to existing APIs?

For large features, open an issue first to discuss the design before writing code. A short conversation can save a long pull request.

## Development Setup

PyLGEN is written in Cython and requires a C compiler to build the extensions.

### Prerequisites

- Python 3.12 or later
- A C compiler (`gcc`, `clang`, or `MSVC`)
- Git

### Installation

 - `1`. Create a new virtual environment:

```bash
python -m venv <target-directory>

cd <target-directory>

source ./bin/activate   # On Windows: .\Scripts\activate
```
 - `2`. Download the source code to `<target-directory>` and install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

 - `3`. Build the source code

```bash
python setup.py build_ext --inplace
```

### Rebuilding after changing `.pyx` files

If you modify a `.pyx` or `.pxd` file, you must rebuild:

```bash
python setup.py build_ext --inplace --force
```

Forgetting this step is the most common source of confusion. If your changes seem to have no effect, rebuild before assuming the bug is elsewhere.

## Project Structure

```text
pylgen/
├── common/        # Core types: Symbol, AST, Token, ASTListView, Error hierarchy
├── automaton/     # Finite automata, determinization, Hopcroft minimization
├── regex/         # Regular expression engine
├── lexer/         # Lexical analysis
├── grammar/       # Context-free and attributed grammars
├── parser/        # Parser generation and runtime
├── analysis/      # Visitor pattern, traversal strategies, context management
└── visual/        # Interactive HTML visualization
```

Each module (except `visual`) follows the same layout:

 - `.pyx`: Cython implementation

 - `.pxd`: Cython declarations for other modules

 - `.pyi`: Python type stubs for IDEs and type checkers

When adding or modifying a module, keep all three files in sync.

## Running the Tests

The test suite uses `pytest`:

```bash
pytest tests/
```

Tests are organized by module under `tests/`. When adding a feature, add tests in the corresponding directory. When fixing a bug, add a regression test that would have caught it.

## Coverage

PyLGEN measures coverage through a **dedicated branch** (`dev-coverage`) and a **dedicated GitHub Actions workflow** (`coverage.yml`). Coverage is not part of the standard test run, because compiling the extensions with `linetrace` enabled adds significant overhead and is only needed when you want to inspect coverage numbers.

### How it works

The `dev-coverage` branch contains a modified `setup.py` that activates `linetrace` and `profile` in the Cython compilation directives, along with the required `CYTHON_TRACE` and `CYTHON_USE_SYS_MONITORING=0` macros. The `.github/workflows/coverage.yml` workflow checks out that branch, builds the extensions with instrumentation, runs the test suite through `pytest-cov`, and uploads the report to Codecov.

The `visual` module **is measured**, but it contains a number of `# pragma: no cover` markers on lines that only configure `networkx` and `pyvis` rather than implement framework logic. Those exclusions are intentional and documented in the source.

### Running coverage locally

If you want to reproduce the coverage run locally, check out the `dev-coverage` branch and follow the same steps the workflow uses:

```bash
python setup.py build_ext --inplace --force
pytest --cov=pylgen --cov-report=term-missing
```

> [!important]
Do not submit pull requests that lower the coverage below the configured threshold. If a section of code genuinely cannot be tested (platform-specific branches, defensive error handling), mark it with `# pragma: no cover` and explain why in the pull request.

## Building the Documentation

The documentation uses MkDocs with the Material theme. To preview it locally:

```bash
pip install mkdocs mkdocs-material mkdocs-toc-md
mkdocs serve
```

Then open `http://127.0.0.1:8000` in your browser. Changes to the `.md` files are reflected live.

When adding or modifying documentation:

 - Keep the tone consistent with the existing sections.

 - Cross-reference other modules with relative links.

 - If you add a new page, register it in the `nav` section of `mkdocs.yml`.

 - If you add code examples, verify that they run.


### Translations

The guidelines above apply to the **English documentation**, which is the source of truth for the project. If you are contributing to a translation:

 - Work on a dedicated branch off the corresponding translation branch (for example, `dev-docs-es` for Spanish).

 - Do not modify the English source files unless you are also fixing an error in them; keep translation changes isolated.

 - Preserve the structure of the original (headings, admonitions, code blocks) so the translated page mirrors the English one.

 - When the English documentation changes, open a follow-up issue to keep the translation in sync. Translations that lag behind the source are worse than no translation at all.

## Style Guidelines

### Python and Cython

 - Follow [PEP 8](https://peps.python.org/pep-0008) for Python code.

 - Use type annotations where they improve clarity.

 - Prefer `cdef class` and `cdef` attributes with concrete types in Cython classes. This is
critical for performance in the parsing and evaluation hot paths.

 - In Cython code, use `_get(idx)` and `_size()` over `__getitem__(idx)` and
`__len__()` when iterating over `ASTListView`.

 - Document public classes and methods with docstrings. Keep them concise.

### Documentation

 - Write in English.

 - Use American spelling consistently (`minimization`, not `minimisation`).

 - Prefer short paragraphs and bulleted lists over long prose.

 - Use admonitions (`!!! note`, `!!! tip`, `!!! warning`) sparingly and only
when they add value.

 - When including code, use the Python/Cython tabbed format used throughout the
documentation.

### Commits

 - One logical change per commit.

 - Write commit messages in the imperative mood: `Fix off-by-one in lexer`,
not `Fixed off-by-one in lexer`.

 - Reference issues when applicable: `Fix off-by-one in lexer (#42)`.

## Commit Conventions

PyLGEN follows a lightweight version of [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

## Branching Strategy

PyLGEN does not use a single development branch. Instead, it uses **dedicated branches for each area of the codebase**, so that work stays isolated and reviews are focused. Before starting a contribution, create your branch from the branch that matches the area you are working on. If you are unsure which branch to use, open an issue and ask. Creating a branch from `master` when the change belongs to `dev-parser` will require rebasing later, so it is worth checking first.

Branch names should be descriptive and prefixed by the type of change:

```text
fix/lexer-column-tracking
feat/parser-unary-minus
docs/api-automaton-example
```

## Pull Request Process

- **Fork the repository** and create a branch from the branch that corresponds to your area (see Branching Strategy above). Do not branch from `master` unless you are coordinating with a maintainer.

 - **Make your changes** with tests and documentation.

 - **Run the test suite** locally and verify that coverage does not decrease.

 - **Update the changelog** if your change is user-facing. The changelog lives in the `readme.md` file, under the `Changelog` section. Add an entry under `[Unreleased]` in `CHANGELOG.md`, in the appropriate category (`Added`, `Changed`, `Fixed`, `Removed`).

 - **Open a pull request** against the **same branch you branched from**. In the description, explain:

     - What the change does.

     - Why it is needed.

     - How it was tested.

     - Any breaking changes.

 - **Respond to review comments**. Small iterations are normal; do not take them personally.

A maintainer will review the pull request and either merge it, request changes, or explain why it is out of scope. Do not be discouraged by a rejection; the project has a specific philosophy, and not every contribution fits it.

## Release Process

This section is for maintainers.

Releases are built and validated by the main CI workflow (`.github/workflows/ci.yml`). The workflow runs the test suite, builds the wheels, and verifies that the resulting artifacts are installable and functional. **The wheels produced by that workflow are the ones used for deployment**; do not build new ones locally, because the CI is the source of truth for what ships.

The release steps are:

 - `1`. Ensure the target branch (`master`) is up to date with all the changes to be released.
 
 - `2`. Update the version in `pyproject.toml`.
 
 - `3`. Move the contents of `[Unreleased]` in the `readme.md` changelog section to a new version section with today's date.

 - `4`. Commit: `chore: release vX.Y.Z`.

 - `5`. Tag the commit: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.

 - `6`. Push the commit and the tag: `git push && git push --tags`.

 - `7`. Wait for the CI workflow to complete successfully. It will build the wheels and run the tests against them.

 - `8`. Download the wheels and the source distribution from the CI artifacts.

 - `9`. Upload to TestPyPI first:

```bash
python -m twine upload --repository testpypi <path-to-artifacts>/*
```

 - `10`. Verify the installation from TestPyPI in a clean environment.

 - `11`. Upload to PyPI:

```bash
python -m twine upload <path-to-artifacts>/*
```

 - `12`. Create a GitHub release from the tag, and mark it as the latest release.

 - `13`. ReadTheDocs will automatically build the documentation for the new tag and update the `stable` version.

## Thank You

PyLGEN exists because people like you take the time to read, use, and improve it. Whether you fix a typo, report a bug, or implement a feature, your contribution matters. Thank you.