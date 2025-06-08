# Changelog
## [1.1.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.8) - 2025-06-08
### Fixed
- extracted cancellation logic into a helper to avoid duplication
## [1.1.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.7) - 2025-06-08
### Fixed
- re-raise KeyboardInterrupt after cleanup for proper exit status

## [1.1.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.6) - 2025-06-08
### Fixed
- cancel server task on Ctrl+C so startup no longer hangs

## [1.1.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.5) - 2025-06-08
### Fixed
- graceful shutdown on Ctrl+C without stack trace


## [1.1.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.4) - 2025-06-08
### Fixed
- added `.flake8` and `mypy.ini` to resolve linter and type checker errors

## [1.1.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.3) - 2025-06-08
### Changed
- documented `stdio_server` usage in help docs and bumped version constant

## [1.1.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.2) - 2025-06-08
### Fixed
- use `stdio_server` from MCP library instead of removed `StdioClient`
