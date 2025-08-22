# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Enhanced Dash MCP Server** - A Model Context Protocol (MCP) server that provides intelligent access to local Dash documentation for Claude Desktop. Built in Python 3.11+ with async support, fuzzy search, and multi-tier caching.

## Common Development Commands

### Setup & Installation

```bash
# Initial setup (interactive - prompts for install directory)
./scripts/setup-dash-mcp.sh

# Manual setup in custom directory
mkdir ~/enhanced-dash-mcp && cd ~/enhanced-dash-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Server

```bash
# Activate virtual environment first
source venv/bin/activate

# Test server configuration (validate setup)
python3 enhanced_dash_server.py --test

# Start server normally (for Claude integration)
./start-dash-mcp.sh

# Start in tmux session (background execution)
./start-dash-mcp-tmux.sh

# Using shell aliases (after setup)
dash-mcp-start    # Start server in tmux
dash-mcp-stop     # Stop tmux session
dash-mcp-restart  # Restart server
dash-mcp-status   # Check if running
dash-mcp-logs     # View server logs
dash-mcp-attach   # Attach to tmux session
```

### Development & Testing

```bash
# Run server in test mode (validates docset discovery)
python3 enhanced_dash_server.py --test

# Clear cache (force rediscovery of docsets)
rm -rf ~/.cache/dash-mcp/

# Check Python/Pydantic version compatibility
pip show pydantic  # Must be v2.0+

# Validate MCP configuration
cat ~/.claude/claude_desktop_config.json | jq '.mcpServers."enhanced-dash-mcp"'

# Run automated tests
./test-automation-environments.sh
./test-ci-automation.sh
./test-final-validation.sh
```

### Dependency Management

```bash
# Install/upgrade dependencies
pip install -r requirements.txt

# Install with pyproject.toml (for package builds)
pip install -e .

# Check for Pydantic v2 compatibility
pip install "pydantic>=2.0.0"

# Upgrade specific packages
pip install --upgrade mcp beautifulsoup4 rapidfuzz
```

## Code Architecture

### Core Components

**`enhanced_dash_server.py`** (2000+ lines)
- **`DashDocumentationServer`** class - Main MCP server implementation
  - Handles JSON-RPC protocol communication with Claude
  - Manages tool registration and request routing
  - Implements async/await patterns throughout

### Search & Ranking System

The server implements a sophisticated multi-stage search pipeline:

1. **Docset Discovery** - Recursively scans `~/Library/Application Support/Dash/` 
   - Finds 364+ docsets (vs 45 in flat directory scan)
   - Caches discovered docsets to disk for performance

2. **Fuzzy Matching** - Uses `rapidfuzz` and `fuzzywuzzy` libraries
   - Typo-tolerant search with Levenshtein distance
   - Smart ranking based on match quality and relevance

3. **Content Extraction** - BeautifulSoup4 for HTML/Markdown parsing
   - Cleans and normalizes documentation content
   - Preserves code blocks and formatting

### Caching Architecture

Multi-tier caching system for optimal performance:

- **Memory Cache** - In-process dictionary for hot data
  - Search results and frequently accessed content
  - Cleared on server restart

- **Disk Cache** - Persistent storage in `~/.cache/dash-mcp/`
  - Docset discovery results (364+ docsets)
  - Extracted content for faster retrieval
  - Clear with `rm -rf ~/.cache/dash-mcp/` when needed

### Project Context Awareness

The server analyzes project structure to provide relevant documentation:

- Detects `package.json` for JavaScript/Node.js projects
- Identifies frameworks (React, Vue, Next.js, Angular)
- Recognizes Python projects via `requirements.txt`/`pyproject.toml`
- Detects Django, Flask, FastAPI frameworks
- Analyzes tech stack to prioritize relevant docsets

### MCP Protocol Integration

Implements Model Context Protocol v1.9+:
- JSON-RPC 2.0 communication over stdin/stdout
- Tool registration for Claude integration
- Async request handling with proper error propagation
- Supports multiple concurrent tool calls

## File Organization

```
enhanced-dash-mcp/
├── enhanced_dash_server.py    # Main server implementation
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Package configuration
├── start-dash-mcp.sh          # Normal startup script
├── start-dash-mcp-tmux.sh     # tmux startup script
├── venv/                      # Python virtual environment
├── scripts/
│   ├── setup-dash-mcp.sh     # Automated setup
│   ├── setup-warp-dash-mcp.sh # Warp Terminal setup
│   └── warp-zshrc-additions.sh # Shell aliases
├── tests/                     # Test suite
│   ├── conftest.py           # pytest configuration
│   └── test_*.py             # Individual test files
├── docs/                      # Documentation
│   ├── help.md
│   ├── automation-detection.md
│   └── warp-dash-mcp-workflow.md
└── configs/
    └── warp-mcp-config.json   # Warp Terminal config
```

## Critical Requirements

### System Dependencies
- **macOS only** - Dash app is macOS-exclusive
- **Python 3.8+** required, **3.11+ recommended**
- **Pydantic v2.0+** - Required for MCP compatibility
- **Dash app** installed with docsets downloaded
- **tmux** recommended for background execution

### Important Paths
- **Docsets**: `~/Library/Application Support/Dash/`
- **Cache**: `~/.cache/dash-mcp/`
- **Default Install**: `~/enhanced-dash-mcp/`
- **Claude Config**: `~/.claude/claude_desktop_config.json`

## Troubleshooting

### Server Won't Start
```bash
# Check virtual environment
which python3  # Should show venv/bin/python3

# Verify Pydantic version
pip show pydantic  # Must be 2.0+

# Test server directly
python3 enhanced_dash_server.py --test
```

### Docsets Not Found
```bash
# Clear cache to force rediscovery
rm -rf ~/.cache/dash-mcp/

# Verify Dash installation
ls -la ~/Library/Application\ Support/Dash/

# Count available docsets
find ~/Library/Application\ Support/Dash -name "*.docset" | wc -l
```

### Claude Integration Issues
```bash
# Validate Claude config
cat ~/.claude/claude_desktop_config.json

# Check server is in config
jq '.mcpServers."enhanced-dash-mcp"' ~/.claude/claude_desktop_config.json

# Restart Claude Desktop after config changes
```

## Development Workflow

### Making Changes

1. **Activate environment**: `source venv/bin/activate`
2. **Edit code**: Main logic in `enhanced_dash_server.py`
3. **Test locally**: `python3 enhanced_dash_server.py --test`
4. **Clear cache if needed**: `rm -rf ~/.cache/dash-mcp/`
5. **Restart server**: `dash-mcp-restart` or manually
6. **Test with Claude**: Ask for documentation searches

### Testing Search Functionality

```bash
# Test server discovers all docsets (should find 364+)
python3 enhanced_dash_server.py --test 2>&1 | grep "docsets"

# Verify cache creation
ls -la ~/.cache/dash-mcp/

# Check server logs in tmux
tmux capture-pane -t dash-mcp -p
```

### Performance Optimization

- Cache is automatically managed (memory + disk)
- Clear cache only when docset structure changes
- Server pre-loads docset list on startup
- Fuzzy search is optimized with rapidfuzz C extensions

## Integration Notes

### Warp Terminal Enhancements
- Custom aliases defined in `scripts/warp-zshrc-additions.sh`
- Project detection functions for context-aware help
- Integration with Warp AI for enhanced queries

### Claude Desktop Configuration
The server must be registered in `~/.claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "enhanced-dash-mcp": {
      "command": "$DASH_MCP_DIR/venv/bin/python3",
      "args": ["$DASH_MCP_DIR/enhanced_dash_server.py"],
      "env": {}
    }
  }
}
```

Replace `$DASH_MCP_DIR` with actual installation path.

## Known Issues & Edge Cases

1. **Pydantic Version Conflicts**: Other Python projects may require Pydantic v1.x. Use virtual environments to isolate.

2. **Cache Staleness**: After Dash updates or new docset downloads, clear cache with `rm -rf ~/.cache/dash-mcp/`

3. **tmux Session Conflicts**: If `dash-mcp` session exists, stop it before restarting: `tmux kill-session -t dash-mcp`

4. **Docset Discovery**: First run after cache clear takes longer (scanning 364+ docsets). Subsequent runs use cache.

5. **Non-Interactive Setup**: The setup script detects CI/non-TTY environments and uses defaults automatically.
