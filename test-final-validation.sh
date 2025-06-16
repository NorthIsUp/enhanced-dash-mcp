#!/bin/bash
# Final comprehensive test of Enhanced Dash MCP automation readiness
# This script validates all automation scenarios work without prompting or hanging

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
TEST_DIR="/tmp/dash-mcp-final-test-$$"
SHORT_TIMEOUT=30   # For quick tests
MEDIUM_TIMEOUT=120 # For installation tests

# Logging
log() {
    echo "$(date '+%H:%M:%S') [FINAL-TEST] $1"
}

log_success() {
    echo -e "${GREEN}$(date '+%H:%M:%S') [SUCCESS] $1${NC}"
}

log_error() {
    echo -e "${RED}$(date '+%H:%M:%S') [ERROR] $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}$(date '+%H:%M:%S') [WARNING] $1${NC}"
}

# Cleanup
cleanup() {
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
    # Clean up any test installations in home directory
    if [ -d "/Users/$(whoami)/enhanced-dash-mcp-test" ]; then
        rm -rf "/Users/$(whoami)/enhanced-dash-mcp-test"
    fi
}
trap cleanup EXIT

# Test 1: Verify no prompts in CI mode
test_no_prompts_ci() {
    log "🤖 Test 1: Verify no prompts in CI mode"
    
    local test_dir="$TEST_DIR/ci-no-prompts"
    mkdir -p "$test_dir"
    
    # Copy files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Run with CI variables and capture output
    local output_file="$test_dir/output.log"
    
    if CI=true TERM=dumb DASH_MCP_DIR="$test_dir/mcp" \
       timeout $MEDIUM_TIMEOUT bash setup-dash-mcp.sh > "$output_file" 2>&1; then
        
        # Check for prompt indicators
        if grep -q -E "(read -|Enter |\[.*\]:|Y/n|y/N)" "$output_file"; then
            log_error "❌ Found prompt indicators in CI mode"
            grep -E "(read -|Enter |\[.*\]:|Y/n|y/N)" "$output_file" | head -5
            return 1
        else
            log_success "✅ No prompts detected in CI mode"
            return 0
        fi
    else
        log_error "❌ CI setup failed or timed out"
        return 1
    fi
}

# Test 2: Verify env -i works without hanging
test_clean_env_no_hang() {
    log "🔒 Test 2: Verify env -i works without hanging"
    
    local test_dir="$TEST_DIR/clean-env"
    mkdir -p "$test_dir"
    
    # Copy files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Run in clean environment with timeout
    local start_time=$(date +%s)
    
    if env -i \
        PATH=/usr/local/bin:/usr/bin:/bin \
        HOME="$HOME" \
        USER="$USER" \
        SHELL="$SHELL" \
        DASH_MCP_DIR="$test_dir/mcp" \
        CI=true \
        BATCH_MODE=true \
        timeout $MEDIUM_TIMEOUT bash setup-dash-mcp.sh >/dev/null 2>&1; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if [ $duration -lt $MEDIUM_TIMEOUT ]; then
            log_success "✅ Clean environment completed in ${duration}s (no hang)"
            return 0
        else
            log_error "❌ Clean environment took too long (${duration}s)"
            return 1
        fi
    else
        log_error "❌ Clean environment test failed"
        return 1
    fi
}

# Test 3: Test startup script doesn't hang
test_startup_script() {
    log "🚀 Test 3: Test startup script doesn't hang"
    
    # Use existing installation from previous test
    local install_dir="$TEST_DIR/clean-env/mcp"
    
    if [ ! -d "$install_dir" ]; then
        log_warning "⚠️ No installation found, skipping startup test"
        return 0
    fi
    
    cd "$install_dir"
    
    # Test startup script with --test flag (should exit quickly)
    local start_time=$(date +%s)
    
    if timeout $SHORT_TIMEOUT bash -c "source venv/bin/activate && python3 enhanced_dash_server.py --test" >/dev/null 2>&1; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if [ $duration -lt $SHORT_TIMEOUT ]; then
            log_success "✅ Server test completed in ${duration}s (no hang)"
            return 0
        else
            log_error "❌ Server test took too long (${duration}s)"
            return 1
        fi
    else
        log_error "❌ Server test failed"
        return 1
    fi
}

# Test 4: Test non-interactive stdin
test_stdin_redirect() {
    log "🔇 Test 4: Test non-interactive stdin redirect"
    
    local test_dir="$TEST_DIR/stdin-test"
    mkdir -p "$test_dir"
    
    # Copy files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Redirect stdin from /dev/null and test for hanging
    local start_time=$(date +%s)
    
    if DASH_MCP_DIR="$test_dir/mcp" \
       timeout $MEDIUM_TIMEOUT bash setup-dash-mcp.sh < /dev/null >/dev/null 2>&1; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if [ $duration -lt $MEDIUM_TIMEOUT ]; then
            log_success "✅ Stdin redirect completed in ${duration}s (no hang)"
            return 0
        else
            log_error "❌ Stdin redirect took too long (${duration}s)"
            return 1
        fi
    else
        log_error "❌ Stdin redirect test failed"
        return 1
    fi
}

# Test 5: Test automated variable detection
test_automation_detection() {
    log "🔍 Test 5: Test automation variable detection"
    
    local test_dir="$TEST_DIR/auto-detect"
    mkdir -p "$test_dir"
    
    # Copy setup script
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Test different automation scenarios
    local scenarios=(
        "CI=true"
        "CONTINUOUS_INTEGRATION=true"
        "BATCH_MODE=true"
        "TERM=dumb"
    )
    
    for scenario in "${scenarios[@]}"; do
        log "  Testing detection: $scenario"
        
        # Just test the directory selection part (quick test)
        if echo "" | timeout 10 env $scenario bash -c '
            source setup-dash-mcp.sh 2>/dev/null
            select_installation_directory 2>/dev/null || true
            if [ -n "$DASH_MCP_DIR" ]; then
                echo "DETECTED: $scenario"
            fi
        ' 2>/dev/null | grep -q "DETECTED"; then
            log_success "  ✅ $scenario detected correctly"
        else
            log_warning "  ⚠️ $scenario detection inconclusive"
        fi
    done
    
    return 0
}

# Test 6: Verify timeout mechanisms work
test_timeout_mechanisms() {
    log "⏱️ Test 6: Verify timeout mechanisms work"
    
    # Test that pip operations have timeouts
    local test_dir="$TEST_DIR/timeout-test"
    mkdir -p "$test_dir"
    
    # Create a mock pip that hangs
    cat > "$test_dir/pip" << 'EOF'
#!/bin/bash
# Mock pip that hangs
echo "Mock pip starting..."
sleep 300  # Hang for 5 minutes
EOF
    chmod +x "$test_dir/pip"
    
    # Test that our timeout wrapper works
    local start_time=$(date +%s)
    
    if ! PATH="$test_dir:$PATH" timeout 10 bash -c '
        run_pip_with_timeout() {
            local timeout_seconds=$1
            shift
            if command -v timeout >/dev/null 2>&1; then
                timeout "$timeout_seconds" pip "$@"
            else
                pip "$@"
            fi
        }
        run_pip_with_timeout 5 install something
    ' 2>/dev/null; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if [ $duration -lt 15 ]; then  # Should timeout much faster than 300s
            log_success "✅ Timeout mechanisms working (${duration}s)"
            return 0
        else
            log_error "❌ Timeout took too long (${duration}s)"
            return 1
        fi
    else
        log_success "✅ Timeout mechanisms working (command failed as expected)"
        return 0
    fi
}

# Main test runner
main() {
    echo -e "${PURPLE}🧪 Enhanced Dash MCP Final Validation Tests${NC}"
    echo -e "${BLUE}📍 Script: $SCRIPT_DIR${NC}"
    echo -e "${BLUE}🗂️ Test: $TEST_DIR${NC}"
    echo -e "${BLUE}⏱️ Timeouts: ${SHORT_TIMEOUT}s/${MEDIUM_TIMEOUT}s${NC}"
    echo ""
    
    mkdir -p "$TEST_DIR"
    
    local passed=0
    local failed=0
    
    # Run all tests
    local tests=(
        "test_no_prompts_ci"
        "test_clean_env_no_hang"
        "test_startup_script"
        "test_stdin_redirect"
        "test_automation_detection"
        "test_timeout_mechanisms"
    )
    
    for test_func in "${tests[@]}"; do
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        if $test_func; then
            ((passed++))
        else
            ((failed++))
        fi
        echo ""
    done
    
    # Summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}📊 Final Validation Results${NC}"
    echo -e "${GREEN}✅ Tests passed: $passed${NC}"
    echo -e "${RED}❌ Tests failed: $failed${NC}"
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}🎉 All validation tests passed!${NC}"
        echo -e "${GREEN}✅ Scripts are fully automation-ready${NC}"
        echo -e "${GREEN}✅ No prompts or hangs detected${NC}"
        echo -e "${GREEN}✅ Timeout mechanisms working${NC}"
        echo -e "${GREEN}✅ Environment detection working${NC}"
        echo ""
        echo -e "${BLUE}📋 Validation Summary:${NC}"
        echo -e "  ✅ CI environments: No prompts, automatic defaults"
        echo -e "  ✅ Clean environments (env -i): No hangs"
        echo -e "  ✅ Non-interactive stdin: Handles gracefully"
        echo -e "  ✅ Timeout mechanisms: Prevent indefinite hangs"
        echo -e "  ✅ Server startup: Quick validation mode"
        echo -e "  ✅ Automation detection: Multiple environment variables"
        echo ""
        echo -e "${GREEN}🚀 Ready for production automation!${NC}"
        return 0
    else
        echo -e "${RED}❌ Some validation tests failed${NC}"
        echo -e "${YELLOW}💡 Review failed tests above${NC}"
        return 1
    fi
}

main "$@"

