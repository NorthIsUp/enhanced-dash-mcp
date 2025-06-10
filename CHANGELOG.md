#  (2025-06-10)

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
