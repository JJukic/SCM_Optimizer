# AGENTS Guidelines

This repository is designed for coding agents collaborating on a supply chain optimization codebase.

## Core Principles

- Keep the code modular and easy to extend.
- Use typed Python (Python 3.11+) everywhere.
- Prefer small, testable, mostly pure functions.
- Avoid hardcoded paths; always use `pathlib` and central config.
- Separate business assumptions from optimization logic.

## Coding Rules

- Add type hints to all public functions and class interfaces.
- Add concise docstrings for all public classes and functions.
- Keep modules focused: configuration, data I/O, validation, modeling, and reporting should remain separated.
- Use explicit imports instead of wildcard imports.
- Introduce complexity only when needed by a concrete use case.

## Modeling Rules

- Keep optimization model interfaces stable and explicit.
- Document assumptions in `docs/assumptions.md` before embedding them in model code.
- Keep placeholder and TODO blocks clearly marked when model behavior is not yet finalized.
- Avoid coupling model code directly to file I/O.

## Testing Rules

- Add or update tests for every non-trivial behavior change.
- Keep tests deterministic and small.
- Validate interfaces first (input contracts, output shape, error behavior).
- Prefer synthetic fixtures for fast local execution.

## Repository Conventions

- `src/scm_optimizer/` contains production code.
- `tests/` contains pytest tests mirroring package modules.
- `docs/` contains scope, assumptions, and roadmap documents.
- `data/raw` and `data/processed` are treated as generated/operational data locations.
- `data/sample` stores lightweight, versioned sample data for development.
