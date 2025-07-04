#!/bin/bash
# Test runner for Claude Hooks Manager

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running Claude Hooks Manager Tests..."
echo "=================================="

# Test that hooks are executable
echo -n "Checking hook executability... "
all_executable=true
for hook in ../hooks/*.py; do
    if [[ ! -x "$hook" ]]; then
        echo "❌ $hook is not executable"
        all_executable=false
    fi
done

if $all_executable; then
    echo "✅ All hooks are executable"
fi

echo ""
echo "Running comprehensive test suite..."

# Run the comprehensive test
python3 test_all_hooks.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ All tests passed!"
else
    echo ""
    echo "=================================="
    echo "❌ Some tests failed!"
    exit 1
fi