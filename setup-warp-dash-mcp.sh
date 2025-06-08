#!/bin/bash
# Warp Terminal + Enhanced Dash MCP Integration Setup
# Author: Josh (Fort Collins, CO)
# Optimized for Warp Terminal, Neovim, tmux, Oh-My-Zsh workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Warp Terminal + Enhanced Dash MCP Integration...${NC}"

# Configuration
MCP_DIR="$HOME/Dropbox/programming/projects/mcp-servers/enhanced-dash-mcp"
WARP_CONFIG_DIR="$HOME/.warp"
WARP_MCP_CONFIG="$WARP_CONFIG_DIR/mcp-servers.json"
WARP_COMMANDS_DIR="$WARP_CONFIG_DIR/commands"
WARP_BLOCKS_DIR="$WARP_CONFIG_DIR/blocks"
WARP_WORKFLOWS_DIR="$WARP_CONFIG_DIR/workflows"

# Check if Warp is installed
if ! command -v warp-cli &> /dev/null && [[ ! -d "/Applications/Warp.app" ]]; then
    echo -e "${YELLOW}⚠️  Warp Terminal not found. Installing configuration anyway...${NC}"
    echo -e "${YELLOW}   Download Warp from: https://www.warp.dev${NC}"
fi

# Check if main MCP server is set up
if [[ ! -f "$MCP_DIR/enhanced_dash_server.py" ]]; then
    echo -e "${RED}❌ Enhanced Dash MCP Server not found at $MCP_DIR${NC}"
    echo -e "${RED}   Please run the main setup script first: ./setup-dash-mcp.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Enhanced Dash MCP Server${NC}"

# Create Warp configuration directories
echo -e "${BLUE}📁 Creating Warp configuration directories...${NC}"
mkdir -p "$WARP_CONFIG_DIR"
mkdir -p "$WARP_COMMANDS_DIR"
mkdir -p "$WARP_BLOCKS_DIR"
mkdir -p "$WARP_WORKFLOWS_DIR"

# Create Warp MCP server configuration
echo -e "${BLUE}⚙️  Creating Warp MCP server configuration...${NC}"
cat > "$WARP_MCP_CONFIG" << EOF
{
  "servers": {
    "enhanced-dash-mcp": {
      "config_file": "$MCP_DIR/warp-mcp-config.json",
      "enabled": true,
      "auto_start": true,
      "description": "Enhanced Dash Documentation Server with project-aware search"
    }
  },
  "global_settings": {
    "auto_start_servers": true,
    "timeout": 30,
    "retry_attempts": 3
  }
}
EOF

# Create Warp commands for MCP management
echo -e "${BLUE}🔧 Creating Warp commands...${NC}"
cat > "$WARP_COMMANDS_DIR/dash-mcp.yaml" << 'EOF'
commands:
  - name: "dash-mcp-search"
    description: "Search Dash documentation via MCP"
    command: "echo '💡 Ask Claude: Search for {query} in Dash docs'"
    parameters:
      - name: "query"
        description: "Documentation search query"
        required: true

  - name: "dash-mcp-start"
    description: "Start Dash MCP Server"
    command: "cd ~/mcp-servers/enhanced-dash-mcp && ./start-dash-mcp-tmux.sh"

  - name: "dash-mcp-status"
    description: "Check Dash MCP Server Status"
    command: "tmux has-session -t dash-mcp && echo '✅ Dash MCP: Running' || echo '❌ Dash MCP: Stopped'"

  - name: "dash-mcp-logs"
    description: "View Dash MCP Server Logs"
    command: "tmux capture-pane -t dash-mcp -p"

  - name: "dash-mcp-restart"
    description: "Restart Dash MCP Server"
    command: |
      tmux kill-session -t dash-mcp 2>/dev/null || true
      sleep 1
      cd ~/mcp-servers/enhanced-dash-mcp && ./start-dash-mcp-tmux.sh
      echo "🔄 Dash MCP Server restarted"

  - name: "dash-analyze-project"
    description: "Analyze current project for relevant documentation"
    command: |
      echo "📁 Current project: $(basename $(pwd))"
      echo "📍 Path: $(pwd)"
      echo "💡 Ask Claude: 'Analyze my current project and find relevant documentation'"

  - name: "dash-api-ref"
    description: "Get API reference with examples"
    command: "echo '💡 Ask Claude: Get latest API reference for {api_name} in {technology} with examples'"
    parameters:
      - name: "api_name"
        description: "API, method, or class name"
        required: true
      - name: "technology"
        description: "Technology/library name"
        required: true

  - name: "dash-best-practices"
    description: "Get implementation guidance for a feature"
    command: "echo '💡 Ask Claude: Get implementation guidance for {feature} in my current project'"
    parameters:
      - name: "feature"
        description: "Feature you want to implement"
        required: true
EOF

# Create Warp blocks for reusable workflows
echo -e "${BLUE}🧱 Creating Warp blocks...${NC}"
cat > "$WARP_BLOCKS_DIR/enhanced-dash-mcp.yaml" << 'EOF'
blocks:
  - name: "project-docs-analysis"
    description: "Analyze current project and get relevant documentation"
    template: |
      # 📊 Project Documentation Analysis
      echo "📁 Project: $(basename $(pwd))"
      echo "📍 Location: $(pwd)"
      echo "🔍 Detecting technology stack..."

      # Check for common project files
      [[ -f package.json ]] && echo "📦 Found: package.json (JavaScript/Node.js)"
      [[ -f requirements.txt ]] && echo "🐍 Found: requirements.txt (Python)"
      [[ -f pyproject.toml ]] && echo "🐍 Found: pyproject.toml (Python)"
      [[ -f Cargo.toml ]] && echo "🦀 Found: Cargo.toml (Rust)"
      [[ -f go.mod ]] && echo "🐹 Found: go.mod (Go)"

      echo ""
      echo "💡 Ask Claude: 'Analyze my current project and suggest relevant documentation'"

  - name: "api-quick-lookup"
    description: "Quick API reference lookup"
    template: |
      # 🔍 API Reference Lookup
      echo "Looking up: {api_name} ${tech:+in }{tech}"
      echo "💡 Ask Claude: 'Get latest API reference for {api_name} in {tech} with examples'"
    parameters:
      - name: "api_name"
        description: "API, method, or class name"
      - name: "tech"
        description: "Technology/library name"

  - name: "migration-helper"
    description: "Get migration documentation between versions"
    template: |
      # 🚀 Migration Documentation Helper
      echo "Migration: {tech} {from_version} → {to_version}"
      echo "💡 Ask Claude: 'Get migration docs for {tech} from {from_version} to {to_version}'"
    parameters:
      - name: "tech"
        description: "Technology name"
      - name: "from_version"
        description: "Current version"
      - name: "to_version"
        description: "Target version"

  - name: "debug-with-docs"
    description: "Debug issue with documentation assistance"
    template: |
      # 🐛 Debug with Documentation
      echo "Issue: {issue}"
      echo "Context: $(pwd)"
      echo "💡 Ask Claude: 'Help debug {issue} and find relevant documentation'"
    parameters:
      - name: "issue"
        description: "Description of the issue you're facing"
EOF

# Create Warp workflows for common development scenarios
echo -e "${BLUE}🔄 Creating Warp workflows...${NC}"

# React development workflow
cat > "$WARP_WORKFLOWS_DIR/react-dev-dash.yaml" << 'EOF'
name: "React Development with Dash Docs"
description: "Streamlined React development workflow with documentation access"
steps:
  - name: "setup"
    description: "Setup development environment"
    commands:
      - "dash-mcp-status"
      - "dash-mcp-start"

  - name: "project-analysis"
    description: "Analyze React project"
    commands:
      - "dash-analyze-project"

  - name: "common-queries"
    description: "Common React documentation queries"
    suggestions:
      - "Ask Claude: 'React hooks best practices for my current project'"
      - "Ask Claude: 'Latest React 18 features and migration guide'"
      - "Ask Claude: 'Next.js routing patterns and examples'"
      - "Ask Claude: 'React state management patterns'"
EOF

# Python development workflow
cat > "$WARP_WORKFLOWS_DIR/python-dev-dash.yaml" << 'EOF'
name: "Python Development with Dash Docs"
description: "Python development workflow with documentation access"
steps:
  - name: "setup"
    description: "Setup development environment"
    commands:
      - "dash-mcp-status"
      - "dash-mcp-start"

  - name: "project-analysis"
    description: "Analyze Python project"
    commands:
      - "dash-analyze-project"

  - name: "common-queries"
    description: "Common Python documentation queries"
    suggestions:
      - "Ask Claude: 'Django best practices for my current project'"
      - "Ask Claude: 'Flask routing and middleware patterns'"
      - "Ask Claude: 'FastAPI async patterns and examples'"
      - "Ask Claude: 'Pandas DataFrame operations with examples'"
EOF

# Create enhanced .zshrc additions for Warp
echo -e "${BLUE}🐚 Creating enhanced shell configuration...${NC}"
cat > "$MCP_DIR/warp-zshrc-additions.sh" << 'EOF'
# Enhanced Dash MCP Integration for Warp Terminal
# Add these lines to your ~/.zshrc

# Warp Terminal Detection
export WARP_TERMINAL_DETECTED=false
if [[ "$TERM_PROGRAM" == "WarpTerminal" ]]; then
    export WARP_TERMINAL_DETECTED=true
fi

# Enhanced Dash MCP aliases for Warp Terminal
export MCP_DASH_DIR="$HOME/mcp-servers/enhanced-dash-mcp"

# Warp-optimized aliases with rich output
alias dash-mcp-start='echo "🚀 Starting Dash MCP Server..." && cd $MCP_DASH_DIR && ./start-dash-mcp-tmux.sh'
alias dash-mcp-stop='echo "🛑 Stopping Dash MCP Server..." && tmux kill-session -t dash-mcp 2>/dev/null || echo "Already stopped"'
alias dash-mcp-restart='echo "🔄 Restarting Dash MCP Server..." && dash-mcp-stop && sleep 1 && dash-mcp-start'
alias dash-mcp-status='tmux has-session -t dash-mcp 2>/dev/null && echo "✅ Dash MCP Server: Running" || echo "❌ Dash MCP Server: Stopped"'
alias dash-mcp-logs='echo "📋 Dash MCP Server Logs:" && tmux capture-pane -t dash-mcp -p'
alias dash-mcp-attach='echo "🔗 Attaching to Dash MCP Server..." && tmux attach -t dash-mcp'

# Project-aware documentation shortcuts
function enhanced-dash-mcp-for-project() {
    local project_path=${1:-$(pwd)}
    echo "📁 Analyzing project at: $project_path"
    echo "🔍 Technology stack detection..."

    # Detect project type
    if [[ -f "$project_path/package.json" ]]; then
        echo "📦 JavaScript/Node.js project detected"
        if grep -q "react" "$project_path/package.json" 2>/dev/null; then
            echo "⚛️  React framework detected"
        fi
        if grep -q "next" "$project_path/package.json" 2>/dev/null; then
            echo "🔺 Next.js framework detected"
        fi
    elif [[ -f "$project_path/requirements.txt" ]] || [[ -f "$project_path/pyproject.toml" ]]; then
        echo "🐍 Python project detected"
        if [[ -f "$project_path/manage.py" ]]; then
            echo "🎸 Django framework detected"
        fi
    fi

    echo ""
    echo "💡 Ask Claude: 'Analyze project at $project_path and suggest relevant documentation'"
}

function dash-api-lookup() {
    local api_name=$1
    local tech=${2:-""}
    if [[ -z "$api_name" ]]; then
        echo "❌ Usage: dash-api-lookup <api_name> [technology]"
        echo "📖 Example: dash-api-lookup useState react"
        return 1
    fi
    echo "🔍 Looking up: $api_name ${tech:+in $tech}"
    echo "💡 Ask Claude: 'Get latest API reference for $api_name ${tech:+in $tech} with examples'"
}

function dash-best-practices() {
    local feature=$1
    local project_path=${2:-$(pwd)}
    if [[ -z "$feature" ]]; then
        echo "❌ Usage: dash-best-practices <feature_description> [project_path]"
        echo "📖 Example: dash-best-practices 'user authentication'"
        return 1
    fi
    echo "📚 Getting best practices for: $feature"
    echo "📁 Project context: $project_path"
    echo "💡 Ask Claude: 'Get implementation guidance for $feature in project at $project_path'"
}

function dash-migration-help() {
    local tech=$1
    local from_version=$2
    local to_version=$3
    if [[ -z "$tech" ]] || [[ -z "$from_version" ]] || [[ -z "$to_version" ]]; then
        echo "❌ Usage: dash-migration-help <technology> <from_version> <to_version>"
        echo "📖 Example: dash-migration-help react 17 18"
        return 1
    fi
    echo "🚀 Migration help: $tech $from_version → $to_version"
    echo "💡 Ask Claude: 'Get migration docs for $tech from $from_version to $to_version'"
}

function dash-debug-help() {
    local issue=$1
    if [[ -z "$issue" ]]; then
        echo "❌ Usage: dash-debug-help <issue_description>"
        echo "📖 Example: dash-debug-help 'React component not re-rendering'"
        return 1
    fi
    echo "🐛 Debug assistance for: $issue"
    echo "📁 Project context: $(pwd)"
    echo "💡 Ask Claude: 'Help debug this issue and find relevant documentation: $issue'"
}

# Warp-specific enhancements
if [[ "$WARP_TERMINAL_DETECTED" == "true" ]]; then
    echo "🚀 Warp Terminal detected - Enhanced MCP integration active"

    # Auto-start MCP server when opening Warp (optional - uncomment if desired)
    # if command -v tmux >/dev/null && ! tmux has-session -t dash-mcp 2>/dev/null; then
    #     echo "🚀 Auto-starting Dash MCP Server for Warp session..."
    #     (cd $MCP_DASH_DIR && ./start-dash-mcp-tmux.sh) &
    # fi

    # Warp AI integration helpers
    function warp-ask-with-context() {
        local query=$1
        local project_context=$(pwd)
        echo "🤖 Warp AI Query with project context:"
        echo "📁 Project: $project_context"
        echo "❓ Query: $query"
        echo ""
        echo "💡 Enhanced with Dash MCP: Access to local documentation"
    }

    # Quick Claude prompts for common tasks
    alias claude-react-help='echo "💡 Ask Claude: Help with React development in my current project"'
    alias claude-python-help='echo "💡 Ask Claude: Help with Python development in my current project"'
    alias claude-debug='echo "💡 Ask Claude: Help debug issues in my current project with relevant documentation"'
    alias claude-best-practices='echo "💡 Ask Claude: What are the best practices for my current project?"'
fi

# Enhanced project detection for better context
function detect-project-tech() {
    local project_path=${1:-$(pwd)}
    echo "🔍 Technology Detection Report for: $(basename $project_path)"
    echo "📍 Path: $project_path"
    echo ""

    # Check for various project indicators
    local tech_detected=false

    if [[ -f "$project_path/package.json" ]]; then
        echo "📦 JavaScript/Node.js Project"
        local frameworks=$(grep -E '"(react|vue|angular|next|express|gatsby)"' "$project_path/package.json" 2>/dev/null | sed 's/.*"\([^"]*\)".*/\1/')
        if [[ -n "$frameworks" ]]; then
            echo "🚀 Frameworks: $frameworks"
        fi
        tech_detected=true
    fi

    if [[ -f "$project_path/requirements.txt" ]] || [[ -f "$project_path/pyproject.toml" ]]; then
        echo "🐍 Python Project"
        if [[ -f "$project_path/manage.py" ]]; then
            echo "🎸 Django Framework"
        elif grep -q "flask" "$project_path/requirements.txt" 2>/dev/null; then
            echo "🌶️  Flask Framework"
        elif grep -q "fastapi" "$project_path/requirements.txt" 2>/dev/null; then
            echo "⚡ FastAPI Framework"
        fi
        tech_detected=true
    fi

    if [[ -f "$project_path/Cargo.toml" ]]; then
        echo "🦀 Rust Project"
        tech_detected=true
    fi

    if [[ -f "$project_path/go.mod" ]]; then
        echo "🐹 Go Project"
        tech_detected=true
    fi

    if [[ -f "$project_path/pubspec.yaml" ]]; then
        echo "🎯 Dart/Flutter Project"
        tech_detected=true
    fi

    if [[ "$tech_detected" == "false" ]]; then
        echo "❓ Unknown or mixed technology project"
    fi

    echo ""
    echo "💡 Use: enhanced-dash-mcp-for-project to get relevant documentation"
}

# Git integration for better project context
function dash-git-context() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "📂 Git Repository Information:"
        echo "🌿 Branch: $(git branch --show-current 2>/dev/null || echo 'detached')"
        echo "📝 Recent commits:"
        git log --oneline -3 2>/dev/null || echo "No commits found"
        echo ""
        echo "💡 Ask Claude: 'Analyze my git repository and suggest relevant documentation based on recent changes'"
    else
        echo "❌ Not in a git repository"
    fi
}

# Quick help function
function dash-help() {
    echo "🚀 Enhanced Dash MCP Commands for Warp Terminal"
    echo ""
    echo "📋 Server Management:"
    echo "  dash-mcp-start          - Start the MCP server"
    echo "  dash-mcp-stop           - Stop the MCP server"
    echo "  dash-mcp-restart        - Restart the MCP server"
    echo "  dash-mcp-status         - Check server status"
    echo "  dash-mcp-logs           - View server logs"
    echo "  dash-mcp-attach         - Attach to server session"
    echo ""
    echo "🔍 Documentation Helpers:"
    echo "  enhanced-dash-mcp-for-project [path]       - Analyze project for relevant docs"
    echo "  dash-api-lookup <api> [tech]       - Quick API reference lookup"
    echo "  dash-best-practices <feature>      - Get implementation guidance"
    echo "  dash-migration-help <tech> <v1> <v2> - Migration documentation"
    echo "  dash-debug-help <issue>            - Debug assistance with docs"
    echo ""
    echo "🛠️  Project Analysis:"
    echo "  detect-project-tech [path]         - Detect project technology stack"
    echo "  dash-git-context                   - Git repository context"
    echo ""
    echo "💡 All functions work with Claude + MCP for intelligent documentation access"
}

# Export functions for use in Warp
export -f enhanced-dash-mcp-for-project dash-api-lookup dash-best-practices dash-migration-help dash-debug-help detect-project-tech dash-git-context dash-help
if [[ "$WARP_TERMINAL_DETECTED" == "true" ]]; then
    export -f warp-ask-with-context
fi
EOF

# Copy Warp configuration files to MCP directory
echo -e "${BLUE}📋 Copying Warp configuration files...${NC}"
cp warp-mcp-config.json "$MCP_DIR/"

# Create Powerlevel10k integration (if p10k is detected)
if command -v p10k >/dev/null 2>&1; then
    echo -e "${BLUE}⚡ Creating Powerlevel10k integration...${NC}"
    cat > "$MCP_DIR/p10k-dash-mcp.zsh" << 'EOF'
# Powerlevel10k integration for Dash MCP Server
# Add this to your ~/.p10k.zsh file

# Custom segment for MCP server status
function prompt_dash_mcp_status() {
  if tmux has-session -t dash-mcp 2>/dev/null; then
    p10k segment -f 2 -i '📚' -t "MCP"  # Green with book emoji when running
  else
    p10k segment -f 1 -i '📕' -t "MCP"  # Red with closed book when stopped
  fi
}

# Add to your prompt elements (example - adjust to your preferences)
# typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
#   # ... your existing elements ...
#   dash_mcp_status
#   # ... other elements ...
# )
EOF
fi

# Create installation summary
echo -e "${BLUE}📊 Creating installation summary...${NC}"
cat > "$MCP_DIR/warp-installation-summary.md" << EOF
# Warp Terminal + Enhanced Dash MCP Installation Summary

## ✅ Installation Complete

### Files Created:
- **Warp MCP Config**: \`$WARP_MCP_CONFIG\`
- **Warp Commands**: \`$WARP_COMMANDS_DIR/dash-mcp.yaml\`
- **Warp Blocks**: \`$WARP_BLOCKS_DIR/enhanced-dash-mcp.yaml\`
- **Warp Workflows**: \`$WARP_WORKFLOWS_DIR/react-dev-dash.yaml\`, \`python-dev-dash.yaml\`
- **Shell Enhancements**: \`$MCP_DIR/warp-zshrc-additions.sh\`
$(command -v p10k >/dev/null && echo "- **P10k Integration**: \`$MCP_DIR/p10k-dash-mcp.zsh\`")

### Next Steps:

1. **Add shell enhancements to your .zshrc:**
   \`\`\`bash
   echo "source $MCP_DIR/warp-zshrc-additions.sh" >> ~/.zshrc
   source ~/.zshrc
   \`\`\`

2. **Start the MCP server:**
   \`\`\`bash
   dash-mcp-start
   \`\`\`

3. **Configure Claude with MCP** (if not done already):
   - Add the configuration from \`$MCP_DIR/warp-mcp-config.json\`

$(command -v p10k >/dev/null && echo "4. **Optional - Add P10k integration:**
   - Add the segment from \`$MCP_DIR/p10k-dash-mcp.zsh\` to your \`~/.p10k.zsh\`")

### Quick Test:
\`\`\`bash
# Check server status
dash-mcp-status

# Analyze current project
enhanced-dash-mcp-for-project

# Get help
dash-help
\`\`\`

### Warp Command Palette:
- Press \`⌘K\` in Warp and type:
  - \`dash-mcp-start\`
  - \`dash-mcp-status\`
  - \`dash-analyze-project\`

### Claude Integration Examples:
- "Analyze my current React project and find relevant documentation"
- "Get implementation guidance for user authentication in my current project"
- "Search for Python pandas DataFrame methods with examples"

**Your Fort Collins development workflow is now supercharged with intelligent documentation access! 🚀**
EOF

echo ""
echo -e "${GREEN}🎉 Warp Terminal + Enhanced Dash MCP Integration setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "1. ${YELLOW}Add shell enhancements:${NC} ${BLUE}echo \"source $MCP_DIR/warp-zshrc-additions.sh\" >> ~/.zshrc && source ~/.zshrc${NC}"
echo -e "2. ${YELLOW}Start MCP server:${NC} ${BLUE}dash-mcp-start${NC}"
echo -e "3. ${YELLOW}Test in Warp:${NC} Press ${BLUE}⌘K${NC} and type ${BLUE}dash-mcp-status${NC}"
echo -e "4. ${YELLOW}Try with Claude:${NC} ${BLUE}'Analyze my current project and find relevant documentation'${NC}"
echo ""
echo -e "${GREEN}📍 Installation summary: $MCP_DIR/warp-installation-summary.md${NC}"
echo -e "${GREEN}📚 Full documentation: $MCP_DIR/warp-dash-mcp-workflow.md${NC}"
echo ""
echo -e "${PURPLE}🚀 Your Warp Terminal is now documentation-aware! Happy coding!${NC}"
