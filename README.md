# Enhanced Dash MCP Server

![Version](https://img.shields.io/badge/version-1.2.11-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
See [CHANGELOG.md](CHANGELOG.md) for version history.

An intelligent Model Context Protocol (MCP) server that transforms your local Dash documentation into a powerful, context-aware assistant for Claude. Built for developers who want seamless access to documentation while coding.

## 🚀 Features

### **Core Capabilities**

- **🔍 Intelligent Search** - Fuzzy matching with typo tolerance and smart ranking
- **📚 Content Extraction** - Clean text extraction from HTML, Markdown, and text docs
- **⚡ Multi-Tier Caching** - Memory + disk caching for lightning-fast repeated searches
- **🎯 Project Awareness** - Automatically detects your tech stack and prioritizes relevant docs
- **🛠️ Implementation Guidance** - Best practices and patterns for specific features
- **📈 Migration Support** - Version upgrade documentation and breaking changes
- **🔄 Latest API Reference** - Current API docs with practical examples

### **Developer Workflow Integration**

- **Warp Terminal** - Native command palette and workflow integration
- **tmux** - Background server execution across terminal sessions
- **Neovim** - Documentation access while coding via Claude
- **Oh-My-Zsh** - Enhanced aliases and productivity shortcuts
- **Git Integration** - Repository-aware documentation suggestions

### **Supported Technologies**

JavaScript/TypeScript, React, Next.js, Vue.js, Angular, Node.js, Python, Django, Flask, FastAPI, pandas, NumPy, and many more through Dash docsets.

## 📋 Prerequisites

- **macOS** with Dash app installed
- **Python 3.8+** (Python 3.11+ recommended)
- **Dash docsets** downloaded (JavaScript, Python, React, etc.)
- **Claude** with MCP support
- **tmux** (recommended for background execution)

### ⚠️ Important Dependency Requirements

This server requires **Pydantic v2.0+** for MCP compatibility. If you have existing projects with Pydantic v1.x, you may need to:

1. Use a virtual environment (recommended)
2. Check for compatibility with other tools (like `pieces-os-client`)
3. Consider using separate Python environments for different projects

```bash
# Check your current Pydantic version
pip show pydantic

# If you have v1.x, you'll need to upgrade
pip install "pydantic>=2.0.0"
```

### 📦 Dependencies

The setup script automatically installs all required dependencies, including:

- `mcp>=1.9.0` - Model Context Protocol framework
- `pydantic>=2.0.0` - Data validation (required for MCP compatibility)
- `beautifulsoup4>=4.12.0` - HTML content extraction
- `fuzzywuzzy>=0.18.0` - Fuzzy string matching
- `python-levenshtein>=0.27.0` - Fast string similarity
- `aiofiles>=24.0.0` - Async file operations
- `aiohttp>=3.11.0` - Async HTTP client
- `rapidfuzz>=3.0.0` - Enhanced fuzzy matching
- `typing-extensions>=4.12.0` - Extended type hints

## ⚡ Quick Start

See [docs/help.md](docs/help.md) for a brief overview of how to run the server.

### 1. **Clone & Setup**

```bash
# Clone or download the project files
mkdir ~/enhanced-dash-mcp && cd ~/enhanced-dash-mcp

# Make setup script executable
chmod +x scripts/setup-dash-mcp.sh

# Run automated setup
./scripts/setup-dash-mcp.sh
```

### 2. **Configure Claude**

Add this to Claude's MCP settings:

```json
{
  "mcpServers": {
    "enhanced-dash-mcp": {
      "command": "python3",
      "args": [
        "/Users/your-username/mcp-servers/enhanced-dash-mcp/enhanced_dash_server.py"
      ],
      "env": {}
    }
  }
}
```

### 3. **Start & Test**

```bash
# Add shell enhancements
echo "source ~/mcp-servers/enhanced-dash-mcp/dash-mcp-aliases.sh" >> ~/.zshrc
source ~/.zshrc

# Start the server
dash-mcp-start

# Test with Claude
# "Search for React useState hook documentation"
```

## 🎮 Usage

### **Basic Documentation Search**

```bash
# Ask Claude:
"Search for Python pandas DataFrame methods"
"Find React hooks best practices"
"Get FastAPI routing documentation with examples"
```

### **Project-Aware Intelligence**

```bash
# Navigate to your project directory, then ask Claude:
"Analyze my current project and find relevant documentation"
"Get implementation guidance for user authentication in my React app"
"What are the best practices for my current Django project?"
```

### **Migration & Upgrade Help**

```bash
# Ask Claude:
"Get migration docs for upgrading from React 17 to 18"
"Find Django 4.2 upgrade guide and breaking changes"
"Show me Next.js 13 to 14 migration documentation"
```

### **API Reference with Examples**

```bash
# Ask Claude:
"Get latest pandas DataFrame.merge API reference with examples"
"Show me React useEffect hook documentation and patterns"
"Find Express.js middleware documentation with use cases"
```

## 🛠️ Advanced Setup

### **Warp Terminal Integration**

For enhanced Warp Terminal support:

```bash
# Run Warp-specific setup
chmod +x scripts/setup-warp-dash-mcp.sh
./scripts/setup-warp-dash-mcp.sh

# Use Command Palette (⌘K):
dash-mcp-start
dash-analyze-project
dash-api-ref useState react
```

### **Shell Aliases & Functions**

After setup, you'll have these convenient commands:

```bash
dash-mcp-start              # Start server in tmux
dash-mcp-status             # Check if running
dash-mcp-logs               # View server output
enhanced-dash-mcp-for-project       # Analyze current project
dash-api-lookup <api> <tech> # Quick API reference
dash-best-practices <feature> # Implementation guidance
dash-help                   # Show all commands
```

### **Powerlevel10k Integration**

Add MCP server status to your prompt:

```bash
# Add to ~/.p10k.zsh (see p10k-dash-mcp.zsh for details)
# Shows 📚 when running, 📕 when stopped
```

## 🔧 Configuration

### **Cache Settings**

```python
# Default cache TTL: 1 hour
# Cache location: ~/.cache/dash-mcp/
# Memory + disk caching for optimal performance
```

### **Fuzzy Search Tuning**

```python
# Default threshold: 60% match
# Adjustable in server configuration
# Typo tolerance with intelligent ranking
```

### **Content Extraction Limits**

```python
# Default: 5000 characters per document
# Configurable for performance vs. detail trade-off
```

## 🏗️ Architecture

### **Core Components**

- **DashMCPServer** - Main server orchestrating all components
- **CacheManager** - Multi-tier caching (memory + disk)
- **ContentExtractor** - Clean text extraction from various formats
- **FuzzySearchEngine** - Intelligent search with ranking algorithms
- **ProjectAwareDocumentationServer** - Context-aware documentation selection

### **Data Flow**

1. **Query received** from Claude via MCP
2. **Project context** analyzed (language, framework, dependencies)
3. **Relevant docsets** identified and prioritized
4. **Fuzzy search** performed with intelligent ranking
5. **Content extracted** and cached for future requests
6. **Results returned** with project-specific scoring

### **Caching Strategy**

- **Memory Cache** - Instant access for recently searched items
- **Disk Cache** - Persistent storage surviving server restarts
- **Smart Expiration** - 1-hour TTL with automatic cleanup
- **Cache Keys** - Generated from search parameters for optimal hit rates

## 📊 Performance

### **Benchmarks**

- **First search**: ~500ms (includes docset scanning)
- **Cached searches**: ~50ms (memory cache hits)
- **Content extraction**: +200-300ms (when requested)
- **Fuzzy matching**: Minimal overhead with significant quality improvement

### **Optimization Tips**

- Keep server running in tmux for best performance
- Initial searches per docset are slower (cache building)
- Content extraction adds latency but provides much richer context
- Memory cache provides fastest repeated access

## 🔍 Available Tools

### **Core Search Tools**

| Tool               | Description                                    | Use Case                         |
| ------------------ | ---------------------------------------------- | -------------------------------- |
| `search_dash_docs` | Basic documentation search with fuzzy matching | General API/concept lookup       |
| `list_docsets`     | Show all available documentation sets          | Discover available documentation |
| `get_doc_content`  | Get full content for specific documentation    | Deep dive into specific topics   |

### **Project-Aware Tools**

| Tool                          | Description                                | Use Case                           |
| ----------------------------- | ------------------------------------------ | ---------------------------------- |
| `analyze_project_context`     | Detect project tech stack and dependencies | Understand current project         |
| `get_project_relevant_docs`   | Context-aware documentation search         | Find docs relevant to your project |
| `get_implementation_guidance` | Best practices for specific features       | Implementation planning            |

### **Specialized Tools**

| Tool                       | Description                    | Use Case                         |
| -------------------------- | ------------------------------ | -------------------------------- |
| `get_migration_docs`       | Version upgrade documentation  | Planning upgrades and migrations |
| `get_latest_api_reference` | Current API docs with examples | Quick reference while coding     |

## 🚨 Troubleshooting

### **Common Issues**

**❌ "No docsets found"**

```bash
# Ensure Dash is installed with docsets
ls ~/Library/Application\ Support/Dash/DocSets/
# Should show *.docset directories
# Optionally set DASH_DOCSETS_PATH if your docsets live elsewhere
# (symlinks to the default location are supported)
# When creating a symlink, point it at `~/Library/Application Support/Dash`.
# A symlink directly to the `DocSets` folder will produce a search path
# ending in `DocSets/DocSets` and no docsets will be discovered.
# The server now resolves such symlinks automatically and also corrects
# `DASH_DOCSETS_PATH` values that point at the parent `Dash` directory.
```

**❌ "Permission errors"**

```bash
# Check Python environment
which python3
source ~/mcp-servers/enhanced-dash-mcp/venv/bin/activate
```

**❌ "Import errors"**

```bash
# Reinstall dependencies
cd ~/mcp-servers/enhanced-dash-mcp
source venv/bin/activate
pip install -r requirements.txt
```

**❌ "Server won't start"**

```bash
# Check if port is in use
tmux kill-session -t dash-mcp
dash-mcp-start
```

**❌ "Slow searches"**

```bash
# First searches build cache - subsequent searches are much faster
# Check cache directory
ls ~/.cache/dash-mcp/
```

### **Debug Mode**

```bash
# View detailed server logs
dash-mcp-logs

# Attach to server session for real-time debugging
dash-mcp-attach
```

## 🤝 Contributing

### **Development Setup**

```bash
# Clone repository
git clone <repository-url>
cd enhanced-dash-mcp

# Create development environment
python3 -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### **Running Tests**

```bash
# Unit tests
pytest tests/

# Linting and type checks
black .
flake8 .  # uses settings from .flake8
mypy .    # uses settings from mypy.ini
```

### **Adding New Features**

1. **Docset Support** - Add new file format extractors in `ContentExtractor`
2. **Search Algorithms** - Enhance ranking in `FuzzySearchEngine`
3. **Project Detection** - Extend framework detection in `ProjectAwareDocumentationServer`
4. **Caching Strategies** - Optimize cache management in `CacheManager`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dash** by Kapeli for providing excellent local documentation
- **Anthropic** for Claude and the MCP framework
- **Warp Terminal** for innovative terminal experience
- **Fort Collins Tech Community** for inspiration and feedback

## 📞 Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the `/docs` directory for detailed guides

## 🗺️ Roadmap

### **v1.1 - Enhanced Intelligence**

- [ ] ML-powered documentation relevance scoring
- [ ] Automatic dependency documentation downloads
- [ ] Cross-reference linking between related docs

### **v1.2 - Extended Platform Support**

- [ ] Linux support with Zeal integration
- [ ] Windows support with alternative doc browsers
- [ ] VS Code extension for direct editor integration

### **v1.3 - Advanced Features**

- [ ] Documentation usage analytics and recommendations
- [ ] Team collaboration features for shared documentation
- [ ] Integration with popular documentation hosting platforms

---

**Built with ❤️ in Fort Collins, CO for developers who value efficient, intelligent documentation access.**

_Transform your development workflow with context-aware documentation that understands your project and coding patterns._

## 📚 Further Reading

- [Changelog and CI](docs/changelog_and_ci.md)
- [Server Usage](docs/server_usage.md)
- [AI Agent Guide](AGENTS.md)
