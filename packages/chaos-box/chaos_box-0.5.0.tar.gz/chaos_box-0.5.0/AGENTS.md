# AGENTS.md

## Setup commands

- Install deps: `uv sync`
- Run tests: `uv run pytest -v`
- Lint and format: `uv run ruff check --fix && uv run ruff format`

## General code style

- Follow established style guides and naming conventions.
- Keep functions/modules small, cohesive, and single-purpose.
- Use clear, consistent documentation for all public APIs.
- Validate inputs and handle errors explicitly with specific types.
- Prefer modular, reusable components; avoid unnecessary global state.
- Write automated tests and ensure reproducibility.
- Use version control with meaningful commit messages.
- Optimize for readability and maintainability over premature optimization.

## Python code style

- Use `argparse` with `argcomplete` for command-line arguments.
- Use `logging` (not `print`) for all output; avoid f-strings in logging calls.
- Follow PEP 8 for code style; use `typing` and type hint for all variables and function return types.
- Write Google-style docstrings for all public modules, classes, and functions.
- Handle errors with specific exceptions; avoid bare `except`.
- Use `main()` and `__main__` guard for CLI entry points.
- Prefer pathlib over os.path; use context managers for resource handling.
- Add unit tests (pytest) and type checks (mypy) to ensure correctness.
