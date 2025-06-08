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
