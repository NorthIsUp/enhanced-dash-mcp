# Changelog

All notable changes to the Enhanced Dash MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.9] - 2025-06-08

### Fixed
- Fixed Dash docset directory structure handling to correctly locate docsets
- Added support for both Core Data and searchIndex database schemas
- Improved docset discovery to handle nested directory structure (DocSets/Name/Name.docset/)
- Enhanced error handling for different database schema types
- Added fallback queries for Core Data schema compatibility

### Changed
- Updated docset scanning logic to properly handle Dash's actual directory structure
- Improved database schema detection and handling
- Enhanced logging for better troubleshooting of docset access issues

### Technical Details
- Modified `get_available_docsets()` to scan subdirectories for .docset files
- Added Core Data schema support in `search_docset()` method
- Improved error handling and fallback mechanisms for database queries
- Added debug script for testing docset accessibility

## [1.2.8] - Previous Release
- Enhanced error logging
- Improved stdio_server usage documentation
