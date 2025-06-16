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

