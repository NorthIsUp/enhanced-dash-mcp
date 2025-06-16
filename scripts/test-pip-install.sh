#!/bin/bash
# Minimal test script to debug pip installation issues
# Run this first to test if pip installation hangs

set -e

log_step() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [TEST] $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2
}

log_step "🧪 Starting pip installation test"
log_step "📍 Current directory: $(pwd)"
log_step "🐍 Python version: $(python3 --version)"
log_step "📦 pip version: $(python3 -m pip --version)"

# Create temporary test directory
TEST_DIR="/tmp/dash-mcp-pip-test-$$"
log_step "📁 Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create minimal requirements file
log_step "📝 Creating minimal requirements.txt"
cat > requirements.txt << EOF
mcp>=1.0.0
pydantic>=2.0.0
EOF

log_step "📋 Requirements to test:"
cat requirements.txt

# Create virtual environment
log_step "🐍 Creating test virtual environment"
if ! python3 -m venv test-venv; then
    log_error "Failed to create virtual environment"
    exit 1
fi

log_step "🔄 Activating virtual environment"
source test-venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    log_error "Virtual environment not activated"
    exit 1
fi

log_step "✅ Virtual environment activated: $VIRTUAL_ENV"

# Test pip upgrade with timeout
log_step "⏱️  Testing pip upgrade (timeout: 2 minutes)"
echo "This will timeout after 2 minutes if hanging..."

if command -v timeout >/dev/null 2>&1; then
    log_step "Using timeout command"
    if timeout 120 pip install --upgrade pip --no-cache-dir --verbose; then
        log_step "✅ pip upgrade successful"
    else
        exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_error "pip upgrade timed out after 2 minutes"
        else
            log_error "pip upgrade failed with exit code: $exit_code"
        fi
        exit $exit_code
    fi
else
    log_step "⚠️  timeout command not available, using plain pip"
    if pip install --upgrade pip --no-cache-dir --verbose; then
        log_step "✅ pip upgrade successful"
    else
        log_error "pip upgrade failed"
        exit 1
    fi
fi

# Test minimal package installation
log_step "⏱️  Testing minimal package installation (timeout: 3 minutes)"
echo "Installing just 2 packages to test..."

if command -v timeout >/dev/null 2>&1; then
    if timeout 180 pip install -r requirements.txt --no-cache-dir --verbose; then
        log_step "✅ Package installation successful"
    else
        exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_error "Package installation timed out after 3 minutes"
        else
            log_error "Package installation failed with exit code: $exit_code"
        fi
        exit $exit_code
    fi
else
    if pip install -r requirements.txt --no-cache-dir --verbose; then
        log_step "✅ Package installation successful"
    else
        log_error "Package installation failed"
        exit 1
    fi
fi

# Cleanup
log_step "🧹 Cleaning up test directory"
cd /
rm -rf "$TEST_DIR"

log_step "🎉 Pip installation test completed successfully!"
echo "✅ The pip installation works fine - the issue might be elsewhere in the setup script."
echo "📝 You can now run the full setup script with confidence."

