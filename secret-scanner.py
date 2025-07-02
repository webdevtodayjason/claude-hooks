#!/usr/bin/env python3
"""
Secret Scanner Hook.
Prevents accidental exposure of secrets, API keys, and sensitive information.
"""
import json
import os
import re
import sys
from pathlib import Path


# Secret patterns to detect
SECRET_PATTERNS = {
    'api_keys': [
        # Generic API key patterns
        r'(?i)api[_-]?key\s*[:=]\s*[\'"][0-9a-zA-Z\-_]{20,}[\'"]',
        r'(?i)apikey\s*[:=]\s*[\'"][0-9a-zA-Z\-_]{20,}[\'"]',
        r'(?i)api[_-]?secret\s*[:=]\s*[\'"][0-9a-zA-Z\-_]{20,}[\'"]',
        # Service-specific patterns
        r'sk_(?:test|live)_[0-9a-zA-Z]{24,}',  # Stripe
        r'AIza[0-9A-Za-z\-_]{35}',  # Google API
        r'(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*[\'"]?AKIA[0-9A-Z]{16}[\'"]?',  # AWS
        r'ghp_[0-9a-zA-Z]{36}',  # GitHub personal access token
        r'gho_[0-9a-zA-Z]{36}',  # GitHub OAuth token
        r'github_pat_[0-9a-zA-Z]{22}_[0-9a-zA-Z]{59}',  # GitHub fine-grained PAT
    ],
    'private_keys': [
        r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
        r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        r'-----BEGIN ENCRYPTED PRIVATE KEY-----',
        r'(?i)private[_-]?key\s*[:=]\s*[\'"][^\'"]{40,}[\'"]',
    ],
    'passwords': [
        r'(?i)password\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
        r'(?i)passwd\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
        r'(?i)pwd\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
        r'(?i)admin[_-]?pass\s*[:=]\s*[\'"][^\'"]+[\'"]',
        r'(?i)db[_-]?pass(?:word)?\s*[:=]\s*[\'"][^\'"]+[\'"]',
    ],
    'tokens': [
        r'(?i)auth[_-]?token\s*[:=]\s*[\'"][0-9a-zA-Z\-_\.]{20,}[\'"]',
        r'(?i)access[_-]?token\s*[:=]\s*[\'"][0-9a-zA-Z\-_\.]{20,}[\'"]',
        r'(?i)bearer\s+[0-9a-zA-Z\-_\.]{20,}',
        r'(?i)jwt\s*[:=]\s*[\'"]eyJ[0-9a-zA-Z\-_\.]+[\'"]',  # JWT token
        r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[0-9a-zA-Z]{24,}',  # Slack
    ],
    'connection_strings': [
        r'(?i)(?:mongodb|postgres|postgresql|mysql|redis|amqp)://[^:]+:[^@]+@[^\s]+',
        r'(?i)Data Source=[^;]+;Password=[^;]+',  # SQL Server
        r'(?i)server=[^;]+;uid=[^;]+;pwd=[^;]+',  # MySQL/SQL Server
    ],
    'env_values': [
        r'(?i)process\.env\.[A-Z_]+\s*\|\|\s*[\'"][^\'"]+[\'"]',  # Hardcoded env fallbacks
        r'(?i)(?:export\s+)?[A-Z_]+=[\'"]?[^\s\'"]+[\'"]?\s*#.*(?:secret|key|token|password)',
    ],
    'ssh': [
        r'ssh-rsa\s+[0-9a-zA-Z+/]+={0,3}\s+[\w+@.]+',  # SSH public key (check context)
        r'(?i)ssh[_-]?key\s*[:=]\s*[\'"][^\'"]+[\'"]',
    ]
}

# Allowed patterns (false positives to ignore)
ALLOWED_PATTERNS = [
    r'(?i)password\s*[:=]\s*[\'"](?:\*{3,}|\.{3,}|x{3,}|\$\{[^}]+\}|<[^>]+>)[\'"]',  # Placeholder passwords
    r'(?i)api[_-]?key\s*[:=]\s*(?:process\.env\.|import\.meta\.env\.|os\.environ)',  # Env var usage
    r'(?i)token\s*[:=]\s*(?:null|undefined|None|""|\'\')',  # Empty values
    r'(?i)password\s*[:=]\s*(?:null|undefined|None|""|\'\')',
    r'(?i)example\.com',  # Example domains
    r'(?i)localhost',
    r'127\.0\.0\.1',
]


def check_gitignore():
    """Check if .gitignore properly excludes sensitive files."""
    issues = []
    gitignore_path = Path('.gitignore')
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        # Check for common sensitive file patterns
        required_patterns = [
            '.env',
            '*.pem',
            '*.key',
            '.env.local',
            '.env.*.local',
            'config/secrets.yml',
            'config/database.yml',
        ]
        
        missing = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                # Check if a broader pattern covers it
                if pattern.startswith('.env') and '.env*' in gitignore_content:
                    continue
                if pattern.endswith('.local') and '*.local' in gitignore_content:
                    continue
                missing.append(pattern)
        
        if missing:
            issues.append({
                'type': 'gitignore_missing',
                'message': f"Consider adding to .gitignore: {', '.join(missing)}",
                'severity': 'medium'
            })
    
    return issues


def is_allowed_context(content, match_start, match_end):
    """Check if the match is in an allowed context."""
    # Get surrounding context
    context_start = max(0, match_start - 100)
    context_end = min(len(content), match_end + 100)
    context = content[context_start:context_end]
    
    # Check against allowed patterns
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            return True
    
    # Check if it's in a comment
    lines_before = content[:match_start].split('\n')
    if lines_before:
        last_line = lines_before[-1].strip()
        if last_line.startswith('//') or last_line.startswith('#') or last_line.startswith('*'):
            return True
    
    # Check if it's in a test file context (even if not in filename)
    test_indicators = ['describe(', 'it(', 'test(', 'expect(', 'assert', 'should']
    if any(indicator in context for indicator in test_indicators):
        return True
    
    return False


def scan_content(content, file_path):
    """Scan content for potential secrets."""
    issues = []
    
    # Skip binary files
    if '\0' in content:
        return issues
    
    # Skip certain file types entirely
    skip_extensions = ['.md', '.txt', '.json', '.lock', '.svg', '.png', '.jpg', '.jpeg', '.gif']
    if any(file_path.endswith(ext) for ext in skip_extensions):
        return issues
    
    # Check each category of secrets
    for category, patterns in SECRET_PATTERNS.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            
            for match in matches:
                # Skip if in allowed context
                if is_allowed_context(content, match.start(), match.end()):
                    continue
                
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                
                # Redact the actual secret value
                secret_value = match.group(0)
                if len(secret_value) > 20:
                    # Show first 10 chars and redact the rest
                    redacted = secret_value[:10] + '...[REDACTED]'
                else:
                    redacted = '[REDACTED]'
                
                issues.append({
                    'line': line_num,
                    'type': category,
                    'pattern': pattern[:30] + '...' if len(pattern) > 30 else pattern,
                    'value': redacted,
                    'severity': 'high' if category in ['private_keys', 'api_keys', 'tokens'] else 'medium'
                })
    
    return issues


def check_env_file_commit(files):
    """Check if .env files are being committed."""
    env_files = [f for f in files if f.endswith('.env') or '.env.' in f]
    env_files = [f for f in env_files if not f.endswith('.example') and not f.endswith('.sample')]
    
    if env_files:
        return [{
            'type': 'env_file_commit',
            'files': env_files,
            'severity': 'high'
        }]
    
    return []


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Handle git commits
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'git commit' in command or 'git add' in command:
                import subprocess
                
                # Get staged files
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                files = result.stdout.strip().split('\n') if result.stdout else []
                
                all_issues = []
                
                # Check for .env files
                env_issues = check_env_file_commit(files)
                if env_issues:
                    all_issues.extend(env_issues)
                
                # Check .gitignore
                gitignore_issues = check_gitignore()
                all_issues.extend(gitignore_issues)
                
                # Scan each file for secrets
                for file_path in files:
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            file_issues = scan_content(content, file_path)
                            if file_issues:
                                all_issues.append({
                                    'file': file_path,
                                    'issues': file_issues
                                })
                        except Exception as e:
                            # Skip files that can't be read
                            continue
                
                # Output results
                if all_issues:
                    print("\n🔒 Security Scan Results:\n", file=sys.stderr)
                    
                    blocking = False
                    
                    # Check for .env file commits
                    env_commits = [i for i in all_issues if isinstance(i, dict) and i.get('type') == 'env_file_commit']
                    if env_commits:
                        blocking = True
                        print("🚨 CRITICAL: Attempting to commit .env files:", file=sys.stderr)
                        for issue in env_commits:
                            for f in issue['files']:
                                print(f"   ❌ {f}", file=sys.stderr)
                        print("\n   💡 Add these to .gitignore immediately!", file=sys.stderr)
                    
                    # Show file-specific issues
                    file_issues = [i for i in all_issues if isinstance(i, dict) and 'file' in i]
                    for file_data in file_issues:
                        high_severity = [i for i in file_data['issues'] if i['severity'] == 'high']
                        medium_severity = [i for i in file_data['issues'] if i['severity'] == 'medium']
                        
                        if high_severity:
                            blocking = True
                            print(f"\n🚫 {file_data['file']}:", file=sys.stderr)
                            for issue in high_severity:
                                print(f"   Line {issue['line']}: Potential {issue['type'].replace('_', ' ')}", file=sys.stderr)
                                print(f"   Found: {issue['value']}", file=sys.stderr)
                        
                        if medium_severity:
                            print(f"\n⚠️  {file_data['file']}:", file=sys.stderr)
                            for issue in medium_severity[:3]:  # Limit output
                                print(f"   Line {issue['line']}: Possible {issue['type'].replace('_', ' ')}", file=sys.stderr)
                    
                    # Show gitignore issues
                    gitignore_issues = [i for i in all_issues if isinstance(i, dict) and i.get('type') == 'gitignore_missing']
                    if gitignore_issues:
                        print("\n📝 .gitignore suggestions:", file=sys.stderr)
                        for issue in gitignore_issues:
                            print(f"   {issue['message']}", file=sys.stderr)
                    
                    print("\n💡 Security Best Practices:", file=sys.stderr)
                    print("   • Use environment variables for sensitive data", file=sys.stderr)
                    print("   • Never commit .env files (add to .gitignore)", file=sys.stderr)
                    print("   • Use secret management services in production", file=sys.stderr)
                    print("   • Rotate any accidentally exposed credentials immediately", file=sys.stderr)
                    
                    if blocking:
                        print("\n❌ Commit blocked due to security issues", file=sys.stderr)
                        sys.exit(2)
        
        # Handle file writes/edits
        elif tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', '')
            
            # Warn about writing to .env files
            if '.env' in file_path and not file_path.endswith('.example'):
                print("\n⚠️  Security Reminder:", file=sys.stderr)
                print("   You're editing a .env file. Ensure it's in .gitignore!", file=sys.stderr)
            
            # Extract content
            content = ''
            if tool_name == 'Write':
                content = tool_input.get('content', '')
            elif tool_name == 'Edit':
                content = tool_input.get('new_string', '')
            elif tool_name == 'MultiEdit':
                content = '\n'.join(edit.get('new_string', '') for edit in tool_input.get('edits', []))
            
            if content:
                issues = scan_content(content, file_path)
                high_severity = [i for i in issues if i['severity'] == 'high']
                
                if high_severity:
                    print("\n🔒 Security Warning - Potential secrets detected:", file=sys.stderr)
                    # Deduplicate by line number
                    seen_lines = set()
                    for issue in high_severity:
                        if issue['line'] not in seen_lines:
                            seen_lines.add(issue['line'])
                            print(f"   Line {issue['line']}: {issue['type'].replace('_', ' ')}", file=sys.stderr)
                            if len(seen_lines) >= 3:
                                break
                    print("   💡 Use environment variables instead of hardcoded secrets", file=sys.stderr)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in secret scanner hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()