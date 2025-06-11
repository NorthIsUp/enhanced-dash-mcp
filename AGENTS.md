# Project Agents.md Guide for OpenAI Codex

This Agents.md file provides guidance for OpenAI Codex and other AI agents working with this codebase.

## Project Structure for OpenAI Codex Navigation

- `/enhanced_dash_server.py` – main server implementation
- `/scripts` – shell scripts for setup and integration
- `/configs` – configuration templates for external tools
- `/docs` – user documentation and guides
- `/AI_Docs` – AI-specific docs and agent guidelines
- `/Specs` – product requirements and plans
- `/tests` – pytest suite verifying behaviour

## Coding Conventions for OpenAI Codex

### General Conventions for Agents.md Implementation

- Use Python 3.8+ syntax
- Keep functions small with meaningful names
- Include comments for complex logic
- Follow existing import order and code style

### React Components Guidelines for OpenAI Codex

This project doesn't use React, so ignore these guidelines.

### CSS/Styling Standards for OpenAI Codex

Not applicable.

## Testing Requirements for OpenAI Codex

Run the following commands before committing Python changes:

```bash
flake8 .
mypy .
pytest -q
```

## Pull Request Guidelines for OpenAI Codex

When creating a PR, ensure it:

1. Includes a clear description of the changes
2. References any related issues
3. Ensures all tests pass
4. Includes screenshots for UI changes
5. Keeps PRs focused on a single concern

## Programmatic Checks for OpenAI Codex

Before submitting changes, run:

```bash
flake8 .
mypy .
pytest -q
```
