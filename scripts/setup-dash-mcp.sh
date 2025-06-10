#!/bin/bash
# Enhanced Dash MCP Server Setup Script
# Author: Josh (Fort Collins, CO)
# Optimized for Python/JavaScript/React development workflows

set -e

echo "🚀 Setting up Enhanced Dash MCP Server..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MCP_DIR="$HOME/Dropbox/programming/projects/mcp-servers/enhanced-dash-mcp"
SCRIPT_NAME="enhanced_dash_server.py"
REQUIREMENTS_FILE="requirements.txt"

# Create MCP servers directory
echo -e "${BLUE}📁 Creating MCP server directory...${NC}"
mkdir -p "$MCP_DIR"

# Check if Dash is installed and has docsets
DASH_DOCSETS_PATH="$HOME/Library/Application Support/Dash/DocSets"
if [ ! -d "$DASH_DOCSETS_PATH" ]; then
    echo -e "${YELLOW}⚠️  Warning: Dash docsets not found at expected location${NC}"
    echo -e "${YELLOW}   Expected: $DASH_DOCSETS_PATH${NC}"
    echo -e "${YELLOW}   Make sure Dash is installed and has downloaded docsets${NC}"
    echo -e "${YELLOW}   Continuing with setup anyway...${NC}"
else
    DOCSET_COUNT=$(find "$DASH_DOCSETS_PATH" -name "*.docset" | wc -l)
    echo -e "${GREEN}✅ Found $DOCSET_COUNT Dash docsets${NC}"
fi

# Copy files to MCP directory
echo -e "${BLUE}📋 Copying server files...${NC}"
cp "$SCRIPT_NAME" "$MCP_DIR/"
cp "$REQUIREMENTS_FILE" "$MCP_DIR/"

# Create Python virtual environment
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
cd "$MCP_DIR"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create startup script
echo -e "${BLUE}🔧 Creating startup script...${NC}"
cat > start-dash-mcp.sh << 'EOF'
#!/bin/bash
# Dash MCP Server Startup Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "🚀 Starting Enhanced Dash MCP Server..."
echo "📍 Server location: $SCRIPT_DIR"
echo "🔗 Connect Claude to: python3 $SCRIPT_DIR/enhanced_dash_server.py"
echo ""

python3 enhanced_dash_server.py
EOF

chmod +x start-dash-mcp.sh

# Create tmux startup script
echo -e "${BLUE}🖥️  Creating tmux integration script...${NC}"
cat > start-dash-mcp-tmux.sh << 'EOF'
#!/bin/bash
# Start Dash MCP Server in tmux session

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SESSION_NAME="dash-mcp"

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "📺 Tmux session '$SESSION_NAME' already exists"
    echo "🔗 Attach with: tmux attach -t $SESSION_NAME"
    echo "❌ Kill existing session with: tmux kill-session -t $SESSION_NAME"
    exit 1
fi

# Create new tmux session
echo "🚀 Starting Dash MCP Server in tmux session '$SESSION_NAME'..."
tmux new-session -d -s "$SESSION_NAME" -c "$SCRIPT_DIR" './start-dash-mcp.sh'

echo "✅ Dash MCP Server started in tmux session '$SESSION_NAME'"
echo "🔗 Attach with: tmux attach -t $SESSION_NAME"
echo "📋 List sessions: tmux list-sessions"
echo "❌ Stop server: tmux kill-session -t $SESSION_NAME"
EOF

chmod +x start-dash-mcp-tmux.sh

# Create Claude configuration template
echo -e "${BLUE}⚙️  Creating Claude configuration template...${NC}"
mkdir -p configs
cat > configs/claude-mcp-config.json << EOF
{
  "mcpServers": {
    "enhanced-dash-mcp": {
      "command": "python3",
      "args": ["$MCP_DIR/enhanced_dash_server.py"],
      "env": {},
      "description": "Enhanced Dash Documentation Server with project-aware search"
    }
  }
}
EOF

# Create shell aliases
echo -e "${BLUE}🔗 Creating shell aliases...${NC}"
cat > dash-mcp-aliases.sh << 'EOF'
# Dash MCP Server Aliases
# Add these to your ~/.zshrc or ~/.bashrc

# Start Dash MCP server
alias dash-mcp-start="cd '$MCP_DIR' && ./start-dash-mcp-tmux.sh"

# Attach to running server
alias dash-mcp-attach="tmux attach -t dash-mcp"

# View server logs
alias dash-mcp-logs="tmux capture-pane -t dash-mcp -p"

# Stop server
alias dash-mcp-stop="tmux kill-session -t dash-mcp"

# Check server status
alias dash-mcp-status="tmux has-session -t dash-mcp && echo 'Running' || echo 'Stopped'"

# Open MCP directory
alias dash-mcp-dir="cd '$MCP_DIR'"
EOF

# Create documentation
echo -e "${BLUE}📚 Creating usage documentation...${NC}"
cat > README.md << 'EOF'
# Enhanced Dash MCP Server

An intelligent Model Context Protocol server that provides Claude with seamless access to your local Dash documentation.

## Features

- **Intelligent Caching**: Fast search with memory + disk caching
- **Content Extraction**: Clean text from HTML/Markdown documentation
- **Fuzzy Search**: Typo-tolerant search with intelligent ranking
- **Project Awareness**: Context-aware documentation based on your project
- **Implementation Guidance**: Best practices and patterns for features
- **Migration Support**: Version upgrade documentation
- **Latest API Reference**: Current API docs with examples

## Quick Start

1. **Start the server:**
   ```bash
   ./start-dash-mcp-tmux.sh
   ```

2. **Configure Claude:**
   Add the configuration from `configs/claude-mcp-config.json` to Claude's MCP settings

3. **Use with Claude:**
   ```
   "Search for React useState hook documentation"
   "Get implementation guidance for user authentication in my React project"
   "Find migration docs for upgrading from React 17 to 18"
   ```

## Available Tools

- `search_dash_docs` - Basic documentation search
- `list_docsets` - List available documentation sets
- `get_doc_content` - Get full content for specific documentation
- `analyze_project_context` - Analyze project tech stack
- `get_project_relevant_docs` - Context-aware documentation search
- `get_implementation_guidance` - Best practices for features
- `get_migration_docs` - Version upgrade documentation
- `get_latest_api_reference` - Current API reference with examples

## Shell Aliases

Add these to your shell configuration:

```bash
source dash-mcp-aliases.sh
```

Then use:
- `dash-mcp-start` - Start server
- `dash-mcp-attach` - Attach to running server
- `dash-mcp-logs` - View server logs
- `dash-mcp-stop` - Stop server
- `dash-mcp-status` - Check if running

## Troubleshooting

1. **No docsets found**: Ensure Dash is installed with downloaded docsets
2. **Permission errors**: Check file permissions and Python environment
3. **Import errors**: Verify all dependencies are installed in the virtual environment
4. **Connection issues**: Ensure Claude is configured with the correct server path

## Project Integration

The server automatically detects:
- JavaScript/Node.js projects (package.json)
- Python projects (requirements.txt, pyproject.toml)
- Frameworks (React, Vue, Django, Flask, etc.)
- Dependencies and provides relevant documentation

Perfect for your Fort Collins development workflow!
EOF

echo ""
echo -e "${GREEN}🎉 Enhanced Dash MCP Server setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "1. ${YELLOW}Configure Claude:${NC} Add the config from ${BLUE}$MCP_DIR/claude-mcp-config.json${NC}"
echo -e "2. ${YELLOW}Add aliases:${NC} Source ${BLUE}$MCP_DIR/dash-mcp-aliases.sh${NC} in your ~/.zshrc"
echo -e "3. ${YELLOW}Start server:${NC} Run ${BLUE}cd $MCP_DIR && ./start-dash-mcp-tmux.sh${NC}"
echo -e "4. ${YELLOW}Test with Claude:${NC} Try 'Search for React useState documentation'"
echo ""
echo -e "${GREEN}📍 Server location: $MCP_DIR${NC}"
echo -e "${GREEN}📚 Documentation: $MCP_DIR/README.md${NC}"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"
