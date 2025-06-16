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

