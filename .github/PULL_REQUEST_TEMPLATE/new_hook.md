---
name: New Hook
about: Template for submitting a new hook
title: '[HOOK] '
labels: 'new-hook'
---

## Hook Details

**Hook Name**: 
**Hook Type**: (pre-commit/commit-msg/pre-push/etc.)
**Description**: 

## Implementation Checklist

- [ ] Hook follows the naming convention (kebab-case)
- [ ] Hook is written in Python following project standards
- [ ] Hook returns appropriate exit codes (0 for success/warning, 2 for blocking)
- [ ] Hook includes descriptive error messages
- [ ] Hook handles edge cases gracefully

## Testing

- [ ] Added unit tests for the hook
- [ ] Tested with various file types/scenarios
- [ ] Tested failure cases
- [ ] Verified hook works with Claude

## Documentation

- [ ] Added hook to README.md hooks table
- [ ] Updated hooks count in README
- [ ] Added detailed description in hooks reference
- [ ] Included configuration options (if any)
- [ ] Added usage examples

## Example Usage

```bash
# Show how to use the hook
```

## Sample Output

```
# Show what the hook output looks like
```

## Related Issues

Closes #