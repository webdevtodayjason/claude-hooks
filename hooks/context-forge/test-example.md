# Testing Context Forge Hooks

## Quick Test Setup

1. **Create a minimal Context Forge project**:
```bash
mkdir test-project && cd test-project

# Create CLAUDE.md
cat > CLAUDE.md << 'EOF'
# Test Project - Claude Code Context

## Project Overview
A test project for Context Forge hooks

## Core Rules
1. Always follow KISS principle
2. Functions under 50 lines
3. Test everything

## Tech Stack
- Frontend: React
- Backend: FastAPI
- Database: PostgreSQL
EOF

# Create Docs structure
mkdir -p Docs PRPs .context-forge

# Create Implementation.md
cat > Docs/Implementation.md << 'EOF'
# Implementation Plan

## Stage 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Configure development environment
- [ ] Create base components
- [x] Install Context Forge hooks

## Stage 2: Core Features (Week 2)
- [ ] User authentication
- [ ] Database schema
- [ ] API endpoints

## Stage 3: Advanced Features (Week 3)
- [ ] Real-time updates
- [ ] Data visualization
- [ ] Export functionality
EOF

# Create a PRP
cat > PRPs/base.md << 'EOF'
# Base Implementation PRP

This is the core implementation guide.

## Key Principles
1. Start with Stage 1 tasks
2. Complete each stage before moving on
3. Test as you go
EOF

# Create config
cat > .context-forge/config.json << 'EOF'
{
  "projectName": "Test Project",
  "techStack": {
    "frontend": "react",
    "backend": "fastapi",
    "database": "postgresql"
  }
}
EOF
```

2. **Test the hooks manually**:
```bash
# Test Context Forge detection
python3 ~/.claude/hooks/context-forge/context-forge-utils.py

# Expected output:
# ✓ This is a Context Forge project
# {detailed project analysis}
```

3. **Simulate PreCompact hook**:
```bash
# Create test input
echo '{"session_id": "test123", "transcript_path": "/tmp/test.jsonl", "trigger": "manual", "custom_instructions": ""}' | \
python3 ~/.claude/hooks/context-forge/precompact-context-refresh.py

# Expected: JSON response with refresh instructions
```

## Testing in Claude Code

1. **Start Claude Code** in the test project
2. **Work on some tasks** until you have significant context
3. **Trigger compaction** with `/compact`
4. **Observe** the refresh instructions
5. **Verify** Claude re-reads the context files

## What to Expect

### Before Compaction
Claude works normally, aware of your project structure and rules.

### During Compaction (PreCompact Hook)
- Hook detects Context Forge project
- Creates marker for Stop hook
- Prepares refresh instructions

### After Compaction (Stop Hook)
Claude will be prompted to:
```
Context refresh required after compaction.
1. Re-read CLAUDE.md to restore project rules and conventions
2. Check Docs/Implementation.md - you are currently working on Stage 1
3. Review PRPs/base.md for implementation guidelines
After reading these files, continue with the task at hand.
```

## Debugging

Watch the log file during testing:
```bash
tail -f ~/.claude/context-forge-hook.log
```

Sample log output:
```
[2024-01-10T10:30:45] PreCompact hook triggered: trigger=manual, session=test123
[2024-01-10T10:30:45] Context Forge detection in /path/to/test-project:
[2024-01-10T10:30:45]   CLAUDE.md: True
[2024-01-10T10:30:45]   Docs/Implementation.md: True
[2024-01-10T10:30:45]   PRPs/: True
[2024-01-10T10:30:45]   .context-forge/config.json: True
[2024-01-10T10:30:45] Context Forge project detected!
[2024-01-10T10:30:45] Created compaction marker for Stop hook
[2024-01-10T10:30:45] Found reference to Stage 1
[2024-01-10T10:30:45] Sent refresh instructions for post-compaction
```