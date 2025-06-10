# Changelog

## [1.2.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.11) - 2025-06-10
- feat: recursively search for `.docset` directories to support nested docsets

## [1.2.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.10) - 2025-06-10
- docs: clarify symlink placement instructions in README

## [1.2.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.9) - 2025-06-08
- fix: preserve full history when generating changelog via GitHub Actions

## [1.2.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.8) - 2025-06-08
- fix: handle symlinked DocSets paths more robustly
- test: add coverage for symlinked DocSets environment variable

## [1.2.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.7) - 2025-06-08
- feat: automatically adjust docset path when DASH_DOCSETS_PATH points to Dash directory or symlink

## [1.2.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.6) - 2025-06-08
- feat: log docset directory on startup and resolve symlinks

## [1.2.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.5) - 2025-06-08
- feat: docset directory can be configured via `DASH_DOCSETS_PATH`

## [1.2.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.4) - 2025-06-08
- fix: cast limit argument to int to prevent slice index errors

## [1.2.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.3) - 2025-06-08
- fix: generate initialization options correctly to avoid AttributeError during startup

## [1.2.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.2) - 2025-06-08
- startup and shutdown log messages
- error logging for unexpected exceptions

## [1.2.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.1) - 2025-06-08
- startup log message to confirm server launch

## [1.2.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.0) - 2025-06-08
- configurable structured logging with file rotation

## [1.1.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.11) - 2025-06-08
- cancel helper suppresses `KeyboardInterrupt` so shutdown completes cleanly

## [1.1.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.10) - 2025-06-08
- ensure `main` returns after task cancellation so startup never hangs

## [1.1.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.9) - 2025-06-08
- suppress KeyboardInterrupt traceback to prevent hanging

## [1.1.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.8) - 2025-06-08
- extracted cancellation logic into a helper to avoid duplication

## [1.1.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.7) - 2025-06-08
- re-raise KeyboardInterrupt after cleanup for proper exit status

## [1.1.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.6) - 2025-06-08
- cancel server task on Ctrl+C so startup no longer hangs

## [1.1.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.5) - 2025-06-08
- graceful shutdown on Ctrl+C without stack trace

## [1.1.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.4) - 2025-06-08
- added `.flake8` and `mypy.ini` to resolve linter and type checker errors

## [1.1.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.3) - 2025-06-08
- documented `stdio_server` usage in help docs and bumped version constant

## [1.1.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.2) - 2025-06-08
- use `stdio_server` from MCP library instead of removed `StdioClient`

## [1.1.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.1) - 2025-06-08
- run server using `StdioClient` and update documentation

## [1.1.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.0) - 2025-06-08
- Automatic changelog generation via GitHub Actions
- Version constant in `enhanced_dash_server.py`
- Help documentation for CI and changelog

## [1.0.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.0.0) - 2025-06-07
- Initial release
