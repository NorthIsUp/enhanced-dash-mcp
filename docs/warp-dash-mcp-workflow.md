# Warp Terminal + Enhanced Dash MCP Integration

## Overview

This guide sets up the Enhanced Dash MCP Server to work seamlessly with Warp Terminal, leveraging your existing Fort Collins development workflow with Neovim, tmux, and Oh-My-Zsh.

## Warp-Specific Configuration

### 1. Warp MCP Server Registration

Add the MCP server to Warp's configuration:

```json
// ~/.warp/mcp-servers.json or via Warp Settings > MCP Servers
{
  "enhanced-dash-mcp": {
    "config_file": "~/mcp-servers/enhanced-dash-mcp/warp-mcp-config.json",
    "enabled": true,
    "auto_start": true
  }
}
```

### 2. Warp Command Palette Integration

Create custom Warp commands for quick MCP server management:

```yaml
# ~/.warp/commands/dash-mcp.yaml
commands:
  - name: "dash-mcp-search"
    description: "Search Dash documentation via MCP"
    command: "echo 'Ask Claude: Search for {query} in Dash docs'"
    parameters:
      - name: "query"
        description: "Documentation search query"
        required: true

  - name: "dash-mcp-start"
    description: "Start Dash MCP Server"
    command: "cd ~/mcp-servers/enhanced-dash-mcp && ./start-dash-mcp-tmux.sh"

  - name: "dash-mcp-status"
    description: "Check Dash MCP Server Status"
    command: "tmux has-session -t dash-mcp && echo '✅ Running' || echo '❌ Stopped'"

  - name: "dash-mcp-logs"
    description: "View Dash MCP Server Logs"
    command: "tmux capture-pane -t dash-mcp -p"

  - name: "dash-mcp-restart"
    description: "Restart Dash MCP Server"
    command: |
      tmux kill-session -t dash-mcp 2>/dev/null || true
      cd ~/mcp-servers/enhanced-dash-mcp && ./start-dash-mcp-tmux.sh
      echo "🔄 Dash MCP Server restarted"
```

### 3. Warp Blocks Integration

Create reusable Warp blocks for common documentation workflows:

```yaml
# ~/.warp/blocks/enhanced-dash-mcp.yaml
blocks:
  - name: "project-docs-analysis"
    description: "Analyze current project and get relevant documentation"
    template: |
      # Project Documentation Analysis
      echo "📁 Current project: $(basename $(pwd))"
      echo "🔍 Analyzing project context..."

      # This would be executed via Claude + MCP
      echo "Ask Claude: 'Analyze my current project and find relevant documentation'"
      echo "Current directory: $(pwd)"

  - name: "api-quick-lookup"
    description: "Quick API reference lookup"
    template: |
      # API Reference Lookup
      echo "🔍 Looking up API documentation..."
      echo "Ask Claude: 'Get latest API reference for {api_name} in {technology}'"
    parameters:
      - name: "api_name"
        description: "API, method, or class name"
      - name: "technology"
        description: "Technology/library name"

  - name: "migration-helper"
    description: "Get migration documentation between versions"
    template: |
      # Migration Documentation Helper
      echo "🚀 Finding migration documentation..."
      echo "Ask Claude: 'Get migration docs for {tech} from {from_version} to {to_version}'"
    parameters:
      - name: "tech"
        description: "Technology name"
      - name: "from_version"
        description: "Current version"
      - name: "to_version"
        description: "Target version"
```

## Warp Terminal Workflow Integration

### Enhanced .zshrc for Warp + MCP

Add these to your `~/.zshrc` for seamless Warp integration:

```bash
# Enhanced Dash MCP aliases for Warp Terminal
export MCP_DASH_DIR="$HOME/mcp-servers/enhanced-dash-mcp/"

# Warp-specific aliases with better output formatting
alias dash-mcp-start='echo "🚀 Starting Dash MCP Server..." && cd $MCP_DASH_DIR && ./start-dash-mcp-tmux.sh'
alias dash-mcp-stop='echo "🛑 Stopping Dash MCP Server..." && tmux kill-session -t dash-mcp'
alias dash-mcp-restart='dash-mcp-stop; sleep 1; dash-mcp-start'
alias dash-mcp-status='tmux has-session -t dash-mcp 2>/dev/null && echo "✅ Dash MCP Server: Running" || echo "❌ Dash MCP Server: Stopped"'
alias dash-mcp-logs='echo "📋 Dash MCP Server Logs:" && tmux capture-pane -t dash-mcp -p'
alias dash-mcp-attach='echo "🔗 Attaching to Dash MCP Server..." && tmux attach -t dash-mcp'

# Project-aware documentation shortcuts
function enhanced-dash-mcp-for-project() {
    local project_path=${1:-$(pwd)}
    echo "📁 Analyzing project at: $project_path"
    echo "💡 Ask Claude: 'Analyze project at $project_path and suggest relevant documentation'"
}

function dash-api-lookup() {
    local api_name=$1
    local tech=${2:-""}
    if [[ -z "$api_name" ]]; then
        echo "Usage: dash-api-lookup <api_name> [technology]"
        return 1
    fi
    echo "🔍 Looking up: $api_name ${tech:+in $tech}"
    echo "💡 Ask Claude: 'Get latest API reference for $api_name ${tech:+in $tech} with examples'"
}

function dash-best-practices() {
    local feature=$1
    local project_path=${2:-$(pwd)}
    if [[ -z "$feature" ]]; then
        echo "Usage: dash-best-practices <feature_description> [project_path]"
        return 1
    fi
    echo "📚 Getting best practices for: $feature"
    echo "💡 Ask Claude: 'Get implementation guidance for $feature in project at $project_path'"
}

# Auto-start MCP server when opening Warp (optional)
if [[ "$TERM_PROGRAM" == "WarpTerminal" ]] && command -v tmux >/dev/null; then
    if ! tmux has-session -t dash-mcp 2>/dev/null; then
        echo "🚀 Auto-starting Dash MCP Server for Warp session..."
        (cd $MCP_DASH_DIR && ./start-dash-mcp-tmux.sh) &
    fi
fi

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
```

### Warp Workflows Configuration

Create workflow files for common development scenarios:

```yaml
# ~/.warp/workflows/enhanced-dash-mcp-react.yaml
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
      - "enhanced-dash-mcp-for-project"

  - name: "common-queries"
    description: "Common React documentation queries"
    suggestions:
      - "Ask Claude: 'React hooks best practices for my current project'"
      - "Ask Claude: 'Latest React 18 features and migration guide'"
      - "Ask Claude: 'Next.js routing patterns and examples'"
```

### Powerlevel10k Integration

Add MCP server status to your Powerlevel10k prompt:

```bash
# Add to ~/.p10k.zsh

# Custom segment for MCP server status
function prompt_dash_mcp_status() {
  if tmux has-session -t dash-mcp 2>/dev/null; then
    p10k segment -f 2 -t "📚"  # Green book emoji when running
  else
    p10k segment -f 1 -t "📕"  # Red book emoji when stopped
  fi
}

# Add to your prompt elements
typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
  # ... your existing elements ...
  dash_mcp_status
  # ... other elements ...
)
```

## Usage in Warp Terminal

### Quick Commands

```bash
# Start server
⌘K → "dash-mcp-start"

# Check status
⌘K → "dash-mcp-status"

# Project analysis
⌘K → "enhanced-dash-mcp-for-project"

# API lookup
⌘K → "dash-api-lookup useState react"

# Best practices
⌘K → "dash-best-practices authentication"
```

### Claude Integration Examples

Once the MCP server is running, use these patterns with Claude in Warp:

```
💬 "Analyze my current React project and find relevant documentation"
💬 "Get implementation guidance for WebSocket integration in my current project"
💬 "Search for Python pandas DataFrame methods with examples"
💬 "Find migration documentation for upgrading from Next.js 12 to 13"
💬 "What are the best practices for error handling in my Django project?"
```

## Performance Optimizations for Warp

### 1. Background Server Management

```bash
# Auto-start server in background when Warp opens
if [[ "$TERM_PROGRAM" == "WarpTerminal" ]]; then
    (dash-mcp-start &) 2>/dev/null
fi
```

### 2. Intelligent Caching

The server automatically caches frequently accessed documentation for faster responses in Warp's fast terminal environment.

### 3. Tmux Integration

Server runs in a dedicated tmux session, keeping it available across Warp terminal sessions.
