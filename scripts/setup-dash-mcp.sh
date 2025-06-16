#!/bin/bash
# Enhanced Dash MCP Server Setup Script
# Author: Josh (Fort Collins, CO)
# Optimized for Python/JavaScript/React development workflows

set -e

# Signal handling for graceful cleanup
cleanup() {
    log_error "Setup interrupted by user or system"
    echo -e "${RED}\n❌ Setup interrupted!${NC}"
    echo -e "${YELLOW}Cleaning up partial installation...${NC}"
    if [ -n "$DASH_MCP_DIR" ] && [ -d "$DASH_MCP_DIR" ]; then
        echo "Partial installation directory: $DASH_MCP_DIR"
        echo "You may want to remove it and start over."
    fi
    exit 1
}

# Trap signals
trap cleanup INT TERM

# Add verbose logging function
log_step() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SETUP] $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2
}

log_step "🚀 Starting Enhanced Dash MCP Server setup..."
log_step "📍 Script location: $(pwd)"
log_step "🖥️  System: $(uname -s) $(uname -r)"

# Check for macOS (Dash requirement)
if [[ "$(uname -s)" != "Darwin" ]]; then
    log_step "⚠️  Warning: Non-macOS system detected"
    echo -e "${YELLOW}⚠️  Warning: This system is not macOS${NC}"
    echo -e "${YELLOW}   Dash documentation app is macOS-only${NC}"
    echo -e "${YELLOW}   The server will install but won't find local docsets${NC}"
    echo -e "${YELLOW}   Consider setting up on a macOS system for full functionality${NC}"
    echo -e "${YELLOW}   Continuing with setup for testing purposes...${NC}"
    echo ""
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
# Installation directory for the Dash MCP Server
# Dash is macOS-only, so use the home directory as the base.
DEFAULT_BASE="$HOME"
DEFAULT_DIR="${DASH_MCP_DIR:-${DEFAULT_BASE}/enhanced-dash-mcp}"

# Check if running in an automated environment (like Codex)
if [ -t 0 ]; then
    # Interactive terminal - prompt for directory
    log_step "💬 Prompting user for installation directory"
    read -r -p "Enter installation directory [${DEFAULT_DIR}]: " INPUT_DIR
    DASH_MCP_DIR="${INPUT_DIR:-$DEFAULT_DIR}"
else
    # Non-interactive environment - use default
    log_step "🤖 Non-interactive environment detected, using default directory"
    DASH_MCP_DIR="$DEFAULT_DIR"
fi

log_step "📁 Installation directory set to: $DASH_MCP_DIR"
SCRIPT_NAME="enhanced_dash_server.py"
REQUIREMENTS_FILE="requirements.txt"

# Create MCP servers directory
log_step "📁 Creating MCP server directory: $DASH_MCP_DIR"
echo -e "${BLUE}📁 Creating MCP server directory...${NC}"
mkdir -p "$DASH_MCP_DIR"
log_step "✅ Directory created successfully"

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
log_step "📋 Starting file copy operations"
echo -e "${BLUE}📋 Copying server files...${NC}"
if [ ! -f "$SCRIPT_NAME" ]; then
    log_error "Script file $SCRIPT_NAME not found in current directory"
    echo -e "${RED}❌ Error: $SCRIPT_NAME not found${NC}"
    exit 1
fi
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_error "Requirements file $REQUIREMENTS_FILE not found in current directory"
    echo -e "${RED}❌ Error: $REQUIREMENTS_FILE not found${NC}"
    exit 1
fi
cp "$SCRIPT_NAME" "$DASH_MCP_DIR/"
cp "$REQUIREMENTS_FILE" "$DASH_MCP_DIR/"
log_step "✅ Files copied successfully"

# Create Python virtual environment
log_step "🐍 Starting Python virtual environment creation"
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
cd "$DASH_MCP_DIR"
log_step "📍 Changed to directory: $(pwd)"
log_step "🐍 Running: python3 -m venv venv"
if ! python3 -m venv venv; then
    log_error "Failed to create virtual environment"
    echo -e "${RED}❌ Error: Failed to create virtual environment${NC}"
    echo -e "${YELLOW}Try: python3 --version to check Python installation${NC}"
    exit 1
fi
log_step "✅ Virtual environment created successfully"

log_step "🔄 Activating virtual environment"
source venv/bin/activate
if [ -z "$VIRTUAL_ENV" ]; then
    log_error "Virtual environment activation failed"
    echo -e "${RED}❌ Error: Virtual environment not activated${NC}"
    exit 1
fi
log_step "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install dependencies
log_step "📦 Starting dependency installation"
echo -e "${BLUE}📦 Installing dependencies (this may take a few minutes)...${NC}"

# Function to run pip with timeout and better error handling
run_pip_with_timeout() {
    local timeout_seconds=$1
    shift
    local cmd="$@"
    
    log_step "⏱️  Running: pip $cmd (timeout: ${timeout_seconds}s)"
    
    # Use timeout command to prevent hanging
    if command -v timeout >/dev/null 2>&1; then
        if timeout "$timeout_seconds" pip $cmd; then
            return 0
        else
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                log_error "Command timed out after ${timeout_seconds} seconds"
                echo -e "${RED}❌ Installation timed out. This might indicate network issues.${NC}"
            else
                log_error "Command failed with exit code: $exit_code"
            fi
            return $exit_code
        fi
    else
        # Fallback without timeout (macOS doesn't have timeout by default)
        log_step "⚠️  Running without timeout (timeout command not available)"
        pip $cmd
        return $?
    fi
}

log_step "🔄 Upgrading pip"
echo "Upgrading pip (timeout: 5 minutes)..."
if ! run_pip_with_timeout 300 "install --upgrade pip --no-cache-dir --progress-bar on"; then
    log_error "Failed to upgrade pip"
    echo -e "${RED}❌ Error: pip upgrade failed${NC}"
    echo -e "${YELLOW}Trying alternative pip upgrade method...${NC}"
    if ! python3 -m pip install --upgrade pip --no-cache-dir; then
        log_error "Alternative pip upgrade also failed"
        echo -e "${RED}❌ Error: Could not upgrade pip${NC}"
        exit 1
    fi
fi
log_step "✅ pip upgraded successfully"

log_step "📦 Installing requirements from $REQUIREMENTS_FILE"
echo "Installing Python packages (timeout: 10 minutes)..."
echo "Dependencies to install:"
cat requirements.txt
echo ""
echo "Starting installation - this may take several minutes..."
if ! run_pip_with_timeout 600 "install -r requirements.txt --no-cache-dir --progress-bar on"; then
    log_error "Failed to install dependencies"
    echo -e "${RED}❌ Error: Dependency installation failed${NC}"
    echo -e "${YELLOW}Possible causes:${NC}"
    echo -e "  - Network connectivity issues"
    echo -e "  - PyPI server problems"
    echo -e "  - Package version conflicts"
    echo -e "${YELLOW}Try running the script again or check your internet connection${NC}"
    exit 1
fi
log_step "✅ All dependencies installed successfully"

# Create startup script
echo -e "${BLUE}🔧 Creating startup script...${NC}"
cat > start-dash-mcp.sh << 'EOF'
#!/bin/bash
# Dash MCP Server Startup Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Test the server first (for validation and debugging)
echo "🧪 Testing server configuration..."
python3 enhanced_dash_server.py --test

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Enhanced Dash MCP Server..."
    echo "📍 Server location: $SCRIPT_DIR"
    echo "🔗 Connect Claude to: python3 $SCRIPT_DIR/enhanced_dash_server.py"
    echo "ℹ️  Note: Server will wait for JSON-RPC input from MCP client (Claude)"
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    python3 enhanced_dash_server.py
else
    echo "❌ Server test failed. Please check the configuration and try again."
    exit 1
fi
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

# Test server configuration first
echo "🧪 Testing server configuration..."
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 enhanced_dash_server.py --test

if [ $? -eq 0 ]; then
    # Create new tmux session
    echo ""
    echo "🚀 Starting Dash MCP Server in tmux session '$SESSION_NAME'..."
    tmux new-session -d -s "$SESSION_NAME" -c "$SCRIPT_DIR" './start-dash-mcp.sh'
    
    echo "✅ Dash MCP Server started in tmux session '$SESSION_NAME'"
    echo "🔗 Attach with: tmux attach -t $SESSION_NAME"
    echo "📋 List sessions: tmux list-sessions"
    echo "❌ Stop server: tmux kill-session -t $SESSION_NAME"
    echo "ℹ️  Note: Server is running in background and waiting for MCP client connection"
else
    echo "❌ Server test failed. Please check the configuration before starting tmux session."
    exit 1
fi
EOF

chmod +x start-dash-mcp-tmux.sh

# Create Claude configuration template
echo -e "${BLUE}⚙️  Creating Claude configuration template...${NC}"
mkdir -p configs
cat > configs/claude-mcp-config.json << EOF
{
  "mcpServers": {
    "enhanced-dash-mcp": {
      "command": "$DASH_MCP_DIR/venv/bin/python3",
      "args": ["$DASH_MCP_DIR/enhanced_dash_server.py"],
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
alias dash-mcp-start="cd '$DASH_MCP_DIR' && ./start-dash-mcp-tmux.sh"

# Attach to running server
alias dash-mcp-attach="tmux attach -t dash-mcp"

# View server logs
alias dash-mcp-logs="tmux capture-pane -t dash-mcp -p"

# Stop server
alias dash-mcp-stop="tmux kill-session -t dash-mcp"

# Check server status
alias dash-mcp-status="tmux has-session -t dash-mcp && echo 'Running' || echo 'Stopped'"

# Open MCP directory
alias dash-mcp-dir="cd '$DASH_MCP_DIR'"
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

# Final validation test
log_step "🧪 Running final validation test"
echo -e "${BLUE}🧪 Testing server installation...${NC}"
if python3 enhanced_dash_server.py --test; then
    log_step "✅ Server validation test passed"
    echo -e "${GREEN}✅ Server test passed!${NC}"
else
    log_error "Server validation test failed"
    echo -e "${RED}❌ Server test failed - check installation${NC}"
    echo -e "${YELLOW}Check logs above for errors${NC}"
    exit 1
fi

log_step "🎉 Setup completed successfully"
echo ""
echo -e "${GREEN}🎉 Enhanced Dash MCP Server setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "1. ${YELLOW}Configure Claude:${NC} Add the config from ${BLUE}$DASH_MCP_DIR/configs/claude-mcp-config.json${NC}"
echo -e "2. ${YELLOW}Add aliases:${NC} Source ${BLUE}$DASH_MCP_DIR/dash-mcp-aliases.sh${NC} in your ~/.zshrc"
echo -e "3. ${YELLOW}Start server:${NC} Run ${BLUE}cd $DASH_MCP_DIR && ./start-dash-mcp-tmux.sh${NC}"
echo -e "4. ${YELLOW}Test with Claude:${NC} Try 'Search for React useState documentation'"
echo ""
echo -e "${GREEN}📍 Server location: $DASH_MCP_DIR${NC}"
echo -e "${GREEN}📚 Documentation: $DASH_MCP_DIR/README.md${NC}"
echo ""
log_step "🏁 Setup script completed at $(date)"
echo -e "${BLUE}Happy coding! 🚀${NC}"
