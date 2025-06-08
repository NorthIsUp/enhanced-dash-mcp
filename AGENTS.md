# Project Agents Guide for OpenAI Codex

This repository is primarily Python code. The guidance below helps Codex work effectively with the project.

## Project Structure

- `enhanced_dash_server.py` – main server implementation
- `tests/` – pytest suite verifying behaviour
- `docs/` – documentation for using the server

## Coding Conventions

- Use Python 3.8+ syntax
- Keep functions small and well named
- Include inline comments for any non-obvious logic
- Follow the existing import order and code style

## Testing

Run the following commands before committing Python changes:

```bash
flake8 .
mypy .
pytest -q
```

## Pull Request Notes

Summarise changes clearly and update docs where relevant. Ensure new tests cover the behaviour of any new or changed code.
