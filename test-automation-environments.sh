#!/bin/bash
# Comprehensive test script for Enhanced Dash MCP in automated environments
# Tests interactive terminal, CI simulation, and env -i scenarios
# Ensures no prompts or hangs in automated setups

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Test configuration
TEST_BASE_DIR="/tmp/dash-mcp-automation-tests-$$"
TEST_TIMEOUT=300  # 5 minutes max per test
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# Logging functions
log_test() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [TEST] $1"
}

log_success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1${NC}"
}

log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1${NC}"
}

log_info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1${NC}"
}

# Cleanup function
cleanup() {
    log_info "🧹 Cleaning up test directories..."
    if [ -n "$TEST_BASE_DIR" ] && [ -d "$TEST_BASE_DIR" ]; then
        rm -rf "$TEST_BASE_DIR"
    fi
    
    # Kill any tmux sessions we might have created
    for session in $(tmux list-sessions -F '#{session_name}' 2>/dev/null | grep -E '^dash-mcp-test-'); do
        log_info "Killing test tmux session: $session"
        tmux kill-session -t "$session" 2>/dev/null || true
    done
}

# Signal handling
trap cleanup EXIT INT TERM

# Test timeout wrapper
run_with_timeout() {
    local timeout_seconds=$1
    local description="$2"
    shift 2
    local cmd="$@"
    
    log_test "⏱️  Running: $description (timeout: ${timeout_seconds}s)"
    
    if command -v timeout >/dev/null 2>&1; then
        if timeout "$timeout_seconds" bash -c "$cmd"; then
            log_success "✅ $description completed successfully"
            return 0
        else
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                log_error "❌ $description timed out after ${timeout_seconds} seconds"
            else
                log_error "❌ $description failed with exit code: $exit_code"
            fi
            return $exit_code
        fi
    else
        log_warning "⚠️  timeout command not available, running without timeout"
        if bash -c "$cmd"; then
            log_success "✅ $description completed successfully"
            return 0
        else
            local exit_code=$?
            log_error "❌ $description failed with exit code: $exit_code"
            return $exit_code
        fi
    fi
}

# Verify required files exist
verify_setup() {
    log_test "🔍 Verifying setup files exist..."
    
    local required_files=(
        "scripts/setup-dash-mcp.sh"
        "scripts/setup-warp-dash-mcp.sh"
        "scripts/test-pip-install.sh"
        "start-dash-mcp.sh"
        "enhanced_dash_server.py"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$file" ]; then
            log_error "Required file not found: $file"
            return 1
        fi
    done
    
    log_success "✅ All required files found"
    return 0
}

# Test 1: Interactive terminal test
test_interactive_terminal() {
    log_test "🖥️  Test 1: Interactive Terminal Environment"
    
    local test_dir="$TEST_BASE_DIR/interactive"
    mkdir -p "$test_dir"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Set environment to simulate interactive terminal with timeout
    export DASH_MCP_DIR="$test_dir/enhanced-dash-mcp-interactive"
    
    # Use expect to simulate user input or timeout
    local setup_cmd="
        cd '$test_dir' && 
        echo '' | timeout 30 bash setup-dash-mcp.sh 2>&1 | 
        head -100  # Limit output to prevent hanging
    "
    
    if run_with_timeout $TEST_TIMEOUT "Interactive terminal setup" "$setup_cmd"; then
        # Verify installation
        if [ -d "$DASH_MCP_DIR" ] && [ -f "$DASH_MCP_DIR/enhanced_dash_server.py" ]; then
            log_success "✅ Interactive terminal test passed"
            return 0
        else
            log_error "❌ Interactive terminal test failed - installation incomplete"
            return 1
        fi
    else
        log_error "❌ Interactive terminal test failed"
        return 1
    fi
}

# Test 2: CI environment simulation
test_ci_environment() {
    log_test "🤖 Test 2: CI Environment Simulation"
    
    local test_dir="$TEST_BASE_DIR/ci"
    mkdir -p "$test_dir"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Set CI environment variables
    export CI=true
    export CONTINUOUS_INTEGRATION=true
    export DASH_MCP_DIR="$test_dir/enhanced-dash-mcp-ci"
    export TERM=dumb
    
    local setup_cmd="
        cd '$test_dir' && 
        CI=true CONTINUOUS_INTEGRATION=true TERM=dumb \
        bash setup-dash-mcp.sh 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "CI environment setup" "$setup_cmd"; then
        # Verify installation
        if [ -d "$DASH_MCP_DIR" ] && [ -f "$DASH_MCP_DIR/enhanced_dash_server.py" ]; then
            log_success "✅ CI environment test passed"
            unset CI CONTINUOUS_INTEGRATION
            return 0
        else
            log_error "❌ CI environment test failed - installation incomplete"
            unset CI CONTINUOUS_INTEGRATION
            return 1
        fi
    else
        log_error "❌ CI environment test failed"
        unset CI CONTINUOUS_INTEGRATION
        return 1
    fi
}

# Test 3: env -i (clean environment) test
test_clean_environment() {
    log_test "🔒 Test 3: Clean Environment (env -i) Test"
    
    local test_dir="$TEST_BASE_DIR/clean"
    mkdir -p "$test_dir"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Use env -i to run in clean environment
    local setup_cmd="
        cd '$test_dir' && 
        env -i \
            PATH=/usr/local/bin:/usr/bin:/bin \
            HOME='$HOME' \
            USER='$USER' \
            SHELL='$SHELL' \
            DASH_MCP_DIR='$test_dir/enhanced-dash-mcp-clean' \
            CI=true \
            BATCH_MODE=true \
            TERM=dumb \
        bash setup-dash-mcp.sh 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "Clean environment setup" "$setup_cmd"; then
        # Verify installation
        local clean_dir="$test_dir/enhanced-dash-mcp-clean"
        if [ -d "$clean_dir" ] && [ -f "$clean_dir/enhanced_dash_server.py" ]; then
            log_success "✅ Clean environment test passed"
            return 0
        else
            log_error "❌ Clean environment test failed - installation incomplete"
            return 1
        fi
    else
        log_error "❌ Clean environment test failed"
        return 1
    fi
}

# Test 4: Non-interactive stdin test
test_noninteractive_stdin() {
    log_test "🔇 Test 4: Non-interactive stdin test"
    
    local test_dir="$TEST_BASE_DIR/noninteractive"
    mkdir -p "$test_dir"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Redirect stdin from /dev/null to simulate non-interactive
    local setup_cmd="
        cd '$test_dir' && 
        DASH_MCP_DIR='$test_dir/enhanced-dash-mcp-noninteractive' \
        bash setup-dash-mcp.sh < /dev/null 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "Non-interactive stdin setup" "$setup_cmd"; then
        # Verify installation
        local nonint_dir="$test_dir/enhanced-dash-mcp-noninteractive"
        if [ -d "$nonint_dir" ] && [ -f "$nonint_dir/enhanced_dash_server.py" ]; then
            log_success "✅ Non-interactive stdin test passed"
            return 0
        else
            log_error "❌ Non-interactive stdin test failed - installation incomplete"
            return 1
        fi
    else
        log_error "❌ Non-interactive stdin test failed"
        return 1
    fi
}

# Test 5: Test pip installation script separately
test_pip_installation() {
    log_test "📦 Test 5: Isolated pip installation test"
    
    local test_dir="$TEST_BASE_DIR/pip"
    mkdir -p "$test_dir"
    
    # Copy pip test script
    cp "$SCRIPT_DIR/scripts/test-pip-install.sh" "$test_dir/"
    
    cd "$test_dir"
    
    local pip_cmd="
        cd '$test_dir' && 
        bash test-pip-install.sh 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "Pip installation test" "$pip_cmd"; then
        log_success "✅ Pip installation test passed"
        return 0
    else
        log_error "❌ Pip installation test failed"
        return 1
    fi
}

# Test 6: Server startup test
test_server_startup() {
    log_test "🚀 Test 6: Server startup test (automated)"
    
    # Use one of the successful installations from previous tests
    local install_dir="$TEST_BASE_DIR/ci/enhanced-dash-mcp-ci"
    
    if [ ! -d "$install_dir" ]; then
        log_warning "⚠️  No installation found for server test, skipping"
        return 0
    fi
    
    cd "$install_dir"
    
    # Test server validation mode
    local test_cmd="
        cd '$install_dir' && 
        source venv/bin/activate && 
        python3 enhanced_dash_server.py --test 2>&1
    "
    
    if run_with_timeout 60 "Server validation test" "$test_cmd"; then
        log_success "✅ Server startup test passed"
        return 0
    else
        log_error "❌ Server startup test failed"
        return 1
    fi
}

# Test 7: Warp setup script test
test_warp_setup() {
    log_test "🌊 Test 7: Warp setup script test"
    
    # Use existing installation as base
    local base_install="$TEST_BASE_DIR/ci/enhanced-dash-mcp-ci"
    
    if [ ! -d "$base_install" ]; then
        log_warning "⚠️  No base installation found for Warp test, skipping"
        return 0
    fi
    
    local test_dir="$TEST_BASE_DIR/warp"
    mkdir -p "$test_dir"
    
    # Copy Warp setup script
    cp "$SCRIPT_DIR/scripts/setup-warp-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Set environment for Warp setup
    local warp_cmd="
        cd '$test_dir' && 
        DASH_MCP_DIR='$base_install' \
        bash setup-warp-dash-mcp.sh 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "Warp setup test" "$warp_cmd"; then
        log_success "✅ Warp setup test passed"
        return 0
    else
        log_error "❌ Warp setup test failed"
        return 1
    fi
}

# Test 8: Batch mode test
test_batch_mode() {
    log_test "📦 Test 8: Batch mode test"
    
    local test_dir="$TEST_BASE_DIR/batch"
    mkdir -p "$test_dir"
    
    # Copy required files
    cp "$SCRIPT_DIR/enhanced_dash_server.py" "$test_dir/"
    cp "$SCRIPT_DIR/requirements.txt" "$test_dir/"
    cp "$SCRIPT_DIR/scripts/setup-dash-mcp.sh" "$test_dir/"
    
    cd "$test_dir"
    
    # Set batch mode environment
    local batch_cmd="
        cd '$test_dir' && 
        BATCH_MODE=true \
        DASH_MCP_DIR='$test_dir/enhanced-dash-mcp-batch' \
        bash setup-dash-mcp.sh 2>&1
    "
    
    if run_with_timeout $TEST_TIMEOUT "Batch mode setup" "$batch_cmd"; then
        # Verify installation
        local batch_dir="$test_dir/enhanced-dash-mcp-batch"
        if [ -d "$batch_dir" ] && [ -f "$batch_dir/enhanced_dash_server.py" ]; then
            log_success "✅ Batch mode test passed"
            return 0
        else
            log_error "❌ Batch mode test failed - installation incomplete"
            return 1
        fi
    else
        log_error "❌ Batch mode test failed"
        return 1
    fi
}

# Main test runner
main() {
    echo -e "${PURPLE}🧪 Enhanced Dash MCP Automation Environment Tests${NC}"
    echo -e "${BLUE}📍 Script location: $SCRIPT_DIR${NC}"
    echo -e "${BLUE}🗂️  Test directory: $TEST_BASE_DIR${NC}"
    echo -e "${BLUE}⏱️  Test timeout: ${TEST_TIMEOUT}s per test${NC}"
    echo ""
    
    # Create test base directory
    mkdir -p "$TEST_BASE_DIR"
    
    # Verify setup
    if ! verify_setup; then
        log_error "❌ Setup verification failed"
        exit 1
    fi
    
    local tests_passed=0
    local tests_failed=0
    local tests_skipped=0
    
    # Run tests
    echo -e "${BLUE}🚀 Starting automation tests...${NC}"
    echo ""
    
    local test_functions=(
        "test_pip_installation"         # Test pip first as it's fastest
        "test_noninteractive_stdin"     # Test non-interactive scenarios
        "test_batch_mode"               # Test batch mode
        "test_clean_environment"        # Test env -i scenario
        "test_ci_environment"           # Test CI simulation
        "test_interactive_terminal"     # Test interactive (with timeout)
        "test_server_startup"           # Test server validation
        "test_warp_setup"               # Test Warp integration
    )
    
    for test_func in "${test_functions[@]}"; do
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        if $test_func; then
            ((tests_passed++))
        else
            # Check if it was skipped
            if [[ $? -eq 77 ]]; then  # Common skip exit code
                ((tests_skipped++))
            else
                ((tests_failed++))
            fi
        fi
        
        echo ""
    done
    
    # Summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}📊 Test Results Summary${NC}"
    echo -e "${GREEN}✅ Tests passed: $tests_passed${NC}"
    echo -e "${RED}❌ Tests failed: $tests_failed${NC}"
    echo -e "${YELLOW}⏭️  Tests skipped: $tests_skipped${NC}"
    echo ""
    
    if [ $tests_failed -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Scripts are ready for automated environments.${NC}"
        echo -e "${GREEN}✅ No prompts or hangs detected in automation scenarios.${NC}"
        return 0
    else
        echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
        echo -e "${YELLOW}💡 Check for prompts, hangs, or missing automation handling.${NC}"
        return 1
    fi
}

# Run main function
main "$@"

