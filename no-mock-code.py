#!/usr/bin/env python3
"""
No Mock Code Hook.
Prevents pseudo/mock/placeholder code from being committed.
Ensures only real, functional implementations make it to production.
"""
import json
import os
import re
import sys
from pathlib import Path


# Common placeholder patterns
PLACEHOLDER_PATTERNS = {
    'names': [
        r'\b(?:John|Jane)\s+(?:Doe|Smith)\b',
        r'\bTest\s+User\b',
        r'\bDemo\s+(?:User|Account|Company)\b',
        r'\bExample\s+(?:User|Name|Company)\b',
        r'\bSample\s+\w+\b',
        r'\bACME\s+(?:Corp|Inc|Company)\b',
    ],
    'emails': [
        r'\b[\w.]+@(?:test|example|demo|sample|temp|fake)\.(?:com|org|net)\b',
        r'\btest[\w]*@[\w]+\.[\w]+\b',
        r'\b(?:user|admin|demo)@(?:localhost|127\.0\.0\.1)\b',
    ],
    'phones': [
        r'\b(?:123-?456-?7890|555-?(?:0[1-9]|[1-9])\d{2}-?\d{4})\b',
        r'\b\(555\)\s*\d{3}-?\d{4}\b',
        r'\b1234567890\b',
    ],
    'addresses': [
        r'\b123\s+(?:Main|Test|Demo|Sample)\s+(?:St|Street|Ave|Avenue)\b',
        r'\b(?:Test|Demo|Sample)\s+(?:Address|Location)\b',
        r'\b1234\s+\w+\s+(?:St|Street|Ave|Avenue)\b',
    ],
    'lorem': [
        r'\blorem\s+ipsum\b',
        r'\bdolor\s+sit\s+amet\b',
        r'\bconsectetur\s+adipiscing\b',
    ],
    'urls': [
        r'https?://(?:example|test|demo|sample)\.(?:com|org|net)',
        r'https?://localhost(?::\d+)?',
        r'https?://127\.0\.0\.1(?::\d+)?',
    ],
    'ids': [
        r'\b(?:12345|00000|11111|99999)\b',
        r'\b[0-9a-f]{8}-0000-0000-0000-[0-9a-f]{12}\b',  # UUID with zeros
        r'\btest[-_]?id[-_]?\d*\b',
    ],
    'dates': [
        r'\b2024-01-01\b',
        r'\b2020-12-31\b',
        r'\b1970-01-01\b',
        r'\b2000-01-01\b',
    ]
}


def check_static_return_values(content, file_path):
    """Check for functions that always return static values."""
    issues = []
    
    # Skip test files
    if any(pattern in file_path for pattern in ['test.', 'spec.', '__tests__', 'mock', '.stories.']):
        return issues
    
    # Pattern for function with static return
    patterns = [
        # JS/TS functions returning literals
        r'(?:function\s+\w+|const\s+\w+\s*=.*?)\s*\([^)]*\)\s*(?:=>|\{)[^{}]*?return\s+[\'"]\w+[\'"]',
        r'(?:function\s+\w+|const\s+\w+\s*=.*?)\s*\([^)]*\)\s*(?:=>|\{)[^{}]*?return\s+\d+',
        r'(?:function\s+\w+|const\s+\w+\s*=.*?)\s*\([^)]*\)\s*(?:=>|\{)[^{}]*?return\s+(?:true|false|null)',
        # Functions returning static arrays/objects
        r'return\s+\[\s*{[^}]+}\s*(?:,\s*{[^}]+}\s*)*\]',  # Static array of objects
        r'return\s+{\s*(?:id|name|email)\s*:\s*[\'"]\w+[\'"]',  # Static object
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('*'):
            continue
            
        for pattern in patterns:
            if re.search(pattern, line):
                # Check if it's in a legitimate context (like default values)
                context = '\n'.join(lines[max(0, i-3):min(len(lines), i+3)])
                if 'default' not in context.lower() and 'fallback' not in context.lower():
                    issues.append({
                        'line': i + 1,
                        'type': 'static_return',
                        'content': line.strip(),
                        'severity': 'high'
                    })
    
    return issues


def check_todo_without_implementation(content):
    """Check for TODO comments without actual implementation."""
    issues = []
    
    # Pattern for TODO followed by return/throw
    todo_patterns = [
        r'//\s*TODO[:\s].*?\n\s*return\s+(?:null|undefined|0|false|\[\]|{})',
        r'//\s*TODO[:\s].*?\n\s*throw\s+new\s+Error\([\'"]Not implemented',
        r'//\s*FIXME[:\s].*?\n\s*return\s+',
        r'/\*\s*TODO[:\s].*?\*/\s*\n?\s*return\s+',
    ]
    
    lines = content.split('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        next_line = lines[i + 1] if i + 1 < len(lines) else ''
        
        if re.search(r'(?://|/\*)\s*(?:TODO|FIXME)', line, re.IGNORECASE):
            # Check if next non-empty line is a placeholder return
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            
            if j < len(lines):
                next_code = lines[j].strip()
                if any(pattern in next_code for pattern in ['return null', 'return undefined', 'return 0', 'return false', 'return []', 'return {}', 'throw new Error']):
                    issues.append({
                        'line': i + 1,
                        'type': 'todo_no_impl',
                        'content': line.strip(),
                        'severity': 'high'
                    })
    
    return issues


def check_fake_async_operations(content):
    """Check for fake async operations."""
    issues = []
    
    # Patterns for fake delays
    fake_async_patterns = [
        r'setTimeout\s*\([^,]+,\s*\d+\s*\)\s*;?\s*//?\s*(?:fake|mock|simulate|delay)',
        r'new\s+Promise\s*\(\s*resolve\s*=>\s*setTimeout\s*\(\s*resolve\s*,\s*\d+\s*\)',
        r'await\s+new\s+Promise\s*\(\s*resolve\s*=>\s*setTimeout',
        r'Promise\.resolve\s*\(\s*{\s*(?:id|data|success)\s*:\s*[\'"]\w+[\'"]',
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        for pattern in fake_async_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    'line': i + 1,
                    'type': 'fake_async',
                    'content': line.strip(),
                    'severity': 'medium'
                })
    
    return issues


def check_placeholder_content(content, file_path):
    """Check for placeholder content in code."""
    issues = []
    
    # Skip certain file types
    skip_patterns = ['test.', 'spec.', '__tests__', 'mock', '.stories.', 'seed', 'fixture', 'example']
    if any(pattern in file_path.lower() for pattern in skip_patterns):
        return issues
    
    lines = content.split('\n')
    
    for category, patterns in PLACEHOLDER_PATTERNS.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                
                # Skip if in comment
                line = lines[line_num - 1] if line_num <= len(lines) else ''
                if line.strip().startswith('//') or line.strip().startswith('*'):
                    continue
                
                issues.append({
                    'line': line_num,
                    'type': f'placeholder_{category}',
                    'content': match.group(0),
                    'severity': 'high' if category in ['lorem', 'names', 'emails'] else 'medium'
                })
    
    return issues


def check_commented_real_code(content):
    """Check for commented out real code with temporary implementations."""
    issues = []
    
    # Pattern for commented code followed by simple implementation
    patterns = [
        r'//\s*const\s+\w+\s*=\s*await\s+\w+\.(?:query|find|fetch).*?\n\s*const\s+\w+\s*=\s*\[',
        r'//\s*\w+\.(?:get|post|put|delete)\(.*?\n\s*return\s*{',
        r'/\*\s*await\s+db\.\w+.*?\*/\s*\n?\s*return\s*\[',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'commented_real_code',
                'content': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0),
                'severity': 'medium'
            })
    
    return issues


def extract_content(tool_name, tool_input):
    """Extract content from different tool inputs."""
    if tool_name == 'Write':
        return tool_input.get('content', ''), tool_input.get('file_path', '')
    elif tool_name == 'Edit':
        return tool_input.get('new_string', ''), tool_input.get('file_path', '')
    elif tool_name == 'MultiEdit':
        content = '\n'.join(edit.get('new_string', '') for edit in tool_input.get('edits', []))
        return content, tool_input.get('file_path', '')
    
    return '', ''


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Handle git commits
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'git commit' in command:
                # Check all staged files
                import subprocess
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                files = result.stdout.strip().split('\n') if result.stdout else []
                
                all_issues = []
                for file_path in files:
                    # Skip non-code files
                    if not any(file_path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rb']):
                        continue
                    
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        issues = []
                        issues.extend(check_placeholder_content(content, file_path))
                        issues.extend(check_static_return_values(content, file_path))
                        issues.extend(check_todo_without_implementation(content))
                        issues.extend(check_fake_async_operations(content))
                        issues.extend(check_commented_real_code(content))
                        
                        if issues:
                            all_issues.append((file_path, issues))
                
                if all_issues:
                    print("\n❌ Mock/Placeholder Code Detected!\n", file=sys.stderr)
                    
                    blocking = False
                    for file_path, issues in all_issues:
                        high_severity = [i for i in issues if i['severity'] == 'high']
                        medium_severity = [i for i in issues if i['severity'] == 'medium']
                        
                        if high_severity:
                            blocking = True
                            print(f"🚫 {file_path}:", file=sys.stderr)
                            for issue in high_severity:
                                print(f"   Line {issue['line']}: {issue['type'].replace('_', ' ').title()}", file=sys.stderr)
                                print(f"   Found: {issue['content'][:80]}{'...' if len(issue['content']) > 80 else ''}", file=sys.stderr)
                        
                        if medium_severity:
                            print(f"\n⚠️  {file_path}:", file=sys.stderr)
                            for issue in medium_severity:
                                print(f"   Line {issue['line']}: {issue['type'].replace('_', ' ').title()}", file=sys.stderr)
                    
                    print("\n💡 Fix Suggestions:", file=sys.stderr)
                    print("   • Replace placeholder data with database queries", file=sys.stderr)
                    print("   • Implement TODO items or create tracking issues", file=sys.stderr)
                    print("   • Use real API calls instead of static returns", file=sys.stderr)
                    print("   • Remove commented code and implement properly", file=sys.stderr)
                    
                    if blocking:
                        sys.exit(2)
        
        # Handle file writes/edits
        elif tool_name in ['Write', 'Edit', 'MultiEdit']:
            content, file_path = extract_content(tool_name, tool_input)
            
            if content and any(file_path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rb']):
                issues = []
                issues.extend(check_placeholder_content(content, file_path))
                issues.extend(check_static_return_values(content, file_path))
                issues.extend(check_todo_without_implementation(content))
                
                high_severity = [i for i in issues if i['severity'] == 'high']
                
                if high_severity:
                    print("\n⚠️  Mock/Placeholder Code Warning:", file=sys.stderr)
                    for issue in high_severity[:3]:  # Show first 3 issues
                        print(f"   Line {issue['line']}: {issue['type'].replace('_', ' ').title()}", file=sys.stderr)
                    print("   💡 Remember to use real implementations, not mock data", file=sys.stderr)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in no-mock-code hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()