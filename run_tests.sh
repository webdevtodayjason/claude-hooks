#!/bin/bash
# Simple test runner for Claude Code hooks

echo "Running Claude Code Hooks Tests..."
echo "=================================="

# Test that hooks are executable
echo -n "Checking hook executability... "
all_executable=true
for hook in hooks/*.py; do
    if [[ ! -x "$hook" ]]; then
        echo "❌ $hook is not executable"
        all_executable=false
    fi
done

if $all_executable; then
    echo "✅ All hooks are executable"
fi

# Test basic functionality
echo ""
echo "Testing basic hook functionality..."

# Test validate-git-commit
echo -n "Testing validate-git-commit.py... "
result=$(echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"fix\""}}' | python3 hooks/validate-git-commit.py 2>&1)
if [[ $? -eq 2 ]] && [[ $result == *"too short"* ]]; then
    echo "✅ Correctly blocks short commits"
else
    echo "❌ Failed to block short commits"
fi

# Test no-mock-code
echo -n "Testing no-mock-code.py... "
# Just test it runs on a simple command
result=$(echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | python3 hooks/no-mock-code.py 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Runs without errors"
else
    echo "❌ Hook failed with error"
fi

# Test secret-scanner
echo -n "Testing secret-scanner.py... "
# Just test it runs on a simple command
result=$(echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | python3 hooks/secret-scanner.py 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Runs without errors"
else
    echo "❌ Hook failed with error"
fi

# Test that hooks don't break on normal operations
echo ""
echo "Testing hooks don't break normal operations..."

echo -n "Testing normal file write... "
result=$(echo '{"tool_name":"Write","tool_input":{"file_path":"normal.js","content":"const data = await db.query();"}}' | python3 hooks/no-mock-code.py 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Allows normal code"
else
    echo "❌ Blocked normal code"
fi

echo ""
echo "=================================="
echo "Tests complete!"