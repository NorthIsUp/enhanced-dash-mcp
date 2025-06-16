#!/bin/bash
# Simplified CI test script for Enhanced Dash MCP
# Tests specific CI automation scenarios quickly

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
TEST_DIR="/tmp/dash-mcp-ci-test-$$"
TEST_TIMEOUT=180  # 3 minutes

# Logging
log() {
    echo "$(date '+%H:%M:%S') [CI-TEST] $1"
}

log_success() {
    echo -e "${GREEN}$(date '+%H:%M:%S') [SUCCESS] $1${NC}"
}

log_error() {
    echo -e "${RED}$(date '+%H:%M:%S') [ERROR] $1${NC}" >&2
}

# Cleanup
cleanup() {
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
}
trap cleanup EXIT

# Main CI test
test_ci_setup() {
    log "🤖 Testing CI environment setup"
    
    # Create test directory
    mkdir -p "$TEST_DIR"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$TEST_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$TEST_DIR/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$TEST_DIR/"
    
    cd "$TEST_DIR"
    
    # Set CI environment variables
    export CI=true
    export CONTINUOUS_INTEGRATION=true
    export TERM=dumb
    export DASH_MCP_DIR="$TEST_DIR/enhanced-dash-mcp"
    
    log "📦 Running setup script in CI mode..."
    
    # Run setup with timeout
    if timeout $TEST_TIMEOUT bash setup-dash-mcp.sh 2>&1; then
        log_success "✅ Setup completed successfully"
        
        # Verify installation
        if [ -d "$DASH_MCP_DIR" ] && [ -f "$DASH_MCP_DIR/enhanced_dash_server.py" ]; then
            log_success "✅ Installation verified"
            
            # Test server validation
            cd "$DASH_MCP_DIR"
            source venv/bin/activate
            
            if python3 enhanced_dash_server.py --test; then
                log_success "✅ Server validation passed"
                return 0
            else
                log_error "❌ Server validation failed"
                return 1
            fi
        else
            log_error "❌ Installation verification failed"
            return 1
        fi
    else
        log_error "❌ Setup script failed or timed out"
        return 1
    fi
}

# Test env -i scenario
test_clean_env() {
    log "🔒 Testing clean environment (env -i)"
    
    local clean_dir="$TEST_DIR-clean"
    mkdir -p "$clean_dir"
    
    # Copy files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$clean_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$clean_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$clean_dir/"
    
    cd "$clean_dir"
    
    # Run in clean environment
    if env -i \
        PATH=/usr/local/bin:/usr/bin:/bin \
        HOME="$HOME" \
        USER="$USER" \
        SHELL="$SHELL" \
        DASH_MCP_DIR="$clean_dir/enhanced-dash-mcp" \
        CI=true \
        BATCH_MODE=true \
        TERM=dumb \
        timeout $TEST_TIMEOUT bash setup-dash-mcp.sh 2>&1; then
        
        log_success "✅ Clean environment test passed"
        
        # Quick validation
        if [ -d "$clean_dir/enhanced-dash-mcp" ]; then
            log_success "✅ Clean environment installation verified"
            return 0
        else
            log_error "❌ Clean environment installation failed"
            return 1
        fi
    else
        log_error "❌ Clean environment test failed"
        return 1
    fi
}

# Test non-interactive stdin
test_noninteractive() {
    log "🔇 Testing non-interactive stdin"
    
    local nonint_dir="$TEST_DIR-nonint"
    mkdir -p "$nonint_dir"
    
    # Copy files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$nonint_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$nonint_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$nonint_dir/"
    
    cd "$nonint_dir"
    
    # Run with stdin from /dev/null
    if DASH_MCP_DIR="$nonint_dir/enhanced-dash-mcp" \
       timeout $TEST_TIMEOUT bash setup-dash-mcp.sh < /dev/null 2>&1; then
        
        log_success "✅ Non-interactive test passed"
        
        # Quick validation
        if [ -d "$nonint_dir/enhanced-dash-mcp" ]; then
            log_success "✅ Non-interactive installation verified"
            return 0
        else
            log_error "❌ Non-interactive installation failed"
            return 1
        fi
    else
        log_error "❌ Non-interactive test failed"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Enhanced Dash MCP CI Automation Tests${NC}"
    echo -e "${BLUE}📍 Script: $SCRIPT_DIR${NC}"
    echo -e "${BLUE}🗂️  Test: $TEST_DIR${NC}"
    echo -e "${BLUE}⏱️  Timeout: ${TEST_TIMEOUT}s${NC}"
    echo ""
    
    local passed=0
    local failed=0
    
    # Run tests
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if test_ci_setup; then
        ((passed++))
    else
        ((failed++))
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if test_clean_env; then
        ((passed++))
    else
        ((failed++))
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if test_noninteractive; then
        ((passed++))
    else
        ((failed++))
    fi
    
    # Summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 CI Test Results${NC}"
    echo -e "${GREEN}✅ Passed: $passed${NC}"
    echo -e "${RED}❌ Failed: $failed${NC}"
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}🎉 All CI tests passed!${NC}"
        echo -e "${GREEN}✅ Scripts are automation-ready${NC}"
        return 0
    else
        echo -e "${RED}❌ Some CI tests failed${NC}"
        return 1
    fi
}

main "$@"

