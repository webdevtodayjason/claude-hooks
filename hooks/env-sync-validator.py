#!/usr/bin/env python3
"""
Environment Sync Validator Hook.
Ensures .env and .env.example files stay in sync.
Prevents missing environment variable documentation.
"""
import json
import os
import re
import sys
from pathlib import Path


def parse_env_file(file_path):
    """Parse an env file and extract variable names."""
    variables = {}
    
    if not os.path.exists(file_path):
        return variables
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments and empty lines
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Match KEY=value pattern
        match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            
            # Remove quotes if present
            if value and value[0] in ['"', "'"] and value[0] == value[-1]:
                value = value[1:-1]
            
            variables[key] = {
                'value': value,
                'line': line_num,
                'has_value': bool(value)
            }
    
    return variables


def find_env_files(project_root):
    """Find all .env and .env.example files in the project."""
    env_files = {
        'env': [],
        'example': []
    }
    
    # Common patterns
    env_patterns = ['.env', '.env.local', '.env.development', '.env.production', '.env.test']
    example_patterns = ['.env.example', '.env.sample', '.env.template', '.env.example.local']
    
    for pattern in env_patterns:
        path = Path(project_root) / pattern
        if path.exists():
            env_files['env'].append(str(path))
    
    for pattern in example_patterns:
        path = Path(project_root) / pattern
        if path.exists():
            env_files['example'].append(str(path))
    
    return env_files


def suggest_safe_value(key, actual_value):
    """Suggest a safe example value for a given key."""
    key_lower = key.lower()
    
    # Database URLs
    if any(db in key_lower for db in ['database', 'db', 'postgres', 'mysql', 'mongo', 'redis']):
        if 'url' in key_lower or 'uri' in key_lower:
            if 'postgres' in key_lower:
                return 'postgresql://user:password@localhost:5432/dbname'
            elif 'mysql' in key_lower:
                return 'mysql://user:password@localhost:3306/dbname'
            elif 'mongo' in key_lower:
                return 'mongodb://localhost:27017/dbname'
            elif 'redis' in key_lower:
                return 'redis://localhost:6379'
            return 'protocol://user:password@host:port/database'
    
    # API keys and secrets
    if any(secret in key_lower for secret in ['key', 'secret', 'token', 'password', 'pwd']):
        if 'api' in key_lower:
            return 'your-api-key-here'
        elif 'secret' in key_lower:
            return 'your-secret-here'
        elif 'token' in key_lower:
            return 'your-token-here'
        elif 'password' in key_lower or 'pwd' in key_lower:
            return 'your-password-here'
        return 'your-value-here'
    
    # URLs and endpoints
    if any(url in key_lower for url in ['url', 'uri', 'endpoint', 'host']):
        if 'api' in key_lower:
            return 'https://api.example.com'
        elif 'webhook' in key_lower:
            return 'https://example.com/webhook'
        return 'https://example.com'
    
    # Ports
    if 'port' in key_lower:
        if 'db' in key_lower or 'database' in key_lower:
            return '5432'
        elif 'redis' in key_lower:
            return '6379'
        return '3000'
    
    # Email
    if 'email' in key_lower or 'mail' in key_lower:
        if 'from' in key_lower or 'sender' in key_lower:
            return 'noreply@example.com'
        return 'user@example.com'
    
    # Booleans
    if actual_value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
        return 'false'
    
    # Numbers
    if actual_value.isdigit():
        return '0'
    
    # Default
    return 'your-value-here'


def compare_env_files(env_vars, example_vars):
    """Compare env and example files and find discrepancies."""
    issues = []
    
    # Find variables in .env but not in .env.example
    missing_in_example = set(env_vars.keys()) - set(example_vars.keys())
    for var in missing_in_example:
        actual_value = env_vars[var]['value']
        suggested_value = suggest_safe_value(var, actual_value)
        issues.append({
            'type': 'missing_in_example',
            'variable': var,
            'suggestion': f'{var}={suggested_value}',
            'severity': 'high'
        })
    
    # Find variables in .env.example but not in .env (informational)
    missing_in_env = set(example_vars.keys()) - set(env_vars.keys())
    for var in missing_in_env:
        issues.append({
            'type': 'missing_in_env',
            'variable': var,
            'severity': 'info'
        })
    
    # Check for exposed sensitive values in .env.example
    for var, data in example_vars.items():
        value = data['value']
        if value and len(value) > 10:
            # Check if it looks like a real secret
            suspicious_patterns = [
                r'^[a-zA-Z0-9]{32,}$',  # Long random string
                r'^ey[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$',  # JWT
                r'^[0-9a-f]{40}$',  # SHA1 hash
                r'^sk_(?:test|live)_',  # Stripe key
                r'password|secret|key|token',  # Actual words suggesting secrets
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    issues.append({
                        'type': 'exposed_secret',
                        'variable': var,
                        'line': data['line'],
                        'severity': 'high'
                    })
                    break
    
    return issues


def extract_env_vars_from_content(content):
    """Extract environment variable references from code."""
    env_vars = set()
    
    # Patterns for different languages
    patterns = [
        r'process\.env\.([A-Z_][A-Z0-9_]*)',  # Node.js
        r'process\.env\[[\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # Node.js bracket notation
        r'os\.environ\.get\([\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # Python
        r'os\.environ\[[\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # Python
        r'ENV\[[\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # Ruby
        r'getenv\([\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # PHP/C
        r'\$_ENV\[[\'"]([A-Z_][A-Z0-9_]*)[\'"]',  # PHP
        r'import\.meta\.env\.([A-Z_][A-Z0-9_]*)',  # Vite
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        env_vars.update(matches)
    
    return env_vars


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        project_root = os.getcwd()
        
        # Handle .env file edits
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', '')
            
            # Check if editing .env file
            if '.env' in file_path and not any(skip in file_path for skip in ['.example', '.sample', '.template']):
                # Find env files
                env_files = find_env_files(project_root)
                
                if not env_files['example']:
                    print("\n⚠️  No .env.example file found!", file=sys.stderr)
                    print("   Create .env.example with safe placeholder values", file=sys.stderr)
                    print("   This helps other developers understand required variables", file=sys.stderr)
                else:
                    print("\n📝 Remember to update .env.example if adding new variables", file=sys.stderr)
                    print("   Use safe placeholder values, never real secrets", file=sys.stderr)
            
            # Check for env var usage in code
            elif any(file_path.endswith(ext) for ext in ['.js', '.ts', '.py', '.rb', '.php']):
                content = ''
                if tool_name == 'Write':
                    content = tool_input.get('content', '')
                elif tool_name == 'Edit':
                    content = tool_input.get('new_string', '')
                elif tool_name == 'MultiEdit':
                    content = '\n'.join(edit.get('new_string', '') for edit in tool_input.get('edits', []))
                
                if content:
                    used_vars = extract_env_vars_from_content(content)
                    if used_vars:
                        # Check if these vars are documented
                        env_files = find_env_files(project_root)
                        if env_files['example']:
                            example_vars = parse_env_file(env_files['example'][0])
                            missing = used_vars - set(example_vars.keys())
                            
                            if missing:
                                print(f"\n📋 New environment variables detected: {', '.join(sorted(missing))}", file=sys.stderr)
                                print("   Remember to add them to .env.example with placeholder values", file=sys.stderr)
        
        # Handle git commits
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'git commit' in command:
                # Check if any .env files were modified
                import subprocess
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                files = result.stdout.strip().split('\n') if result.stdout else []
                
                env_modified = any('.env' in f and not any(skip in f for skip in ['.example', '.sample']) for f in files)
                
                if env_modified:
                    # Find and compare env files
                    env_files = find_env_files(project_root)
                    
                    if not env_files['example']:
                        print("\n❌ Environment Configuration Error:", file=sys.stderr)
                        print("   No .env.example file found!", file=sys.stderr)
                        print("   Create .env.example to document required variables", file=sys.stderr)
                        sys.exit(2)
                    
                    # Parse files
                    all_issues = []
                    for env_file in env_files['env']:
                        env_vars = parse_env_file(env_file)
                        for example_file in env_files['example']:
                            example_vars = parse_env_file(example_file)
                            issues = compare_env_files(env_vars, example_vars)
                            
                            if issues:
                                all_issues.append({
                                    'env_file': env_file,
                                    'example_file': example_file,
                                    'issues': issues
                                })
                    
                    if all_issues:
                        print("\n🔧 Environment File Sync Issues:\n", file=sys.stderr)
                        
                        blocking = False
                        for file_data in all_issues:
                            high_issues = [i for i in file_data['issues'] if i['severity'] == 'high']
                            info_issues = [i for i in file_data['issues'] if i['severity'] == 'info']
                            
                            if high_issues:
                                blocking = True
                                print(f"❌ {file_data['example_file']} is missing variables:", file=sys.stderr)
                                for issue in high_issues:
                                    if issue['type'] == 'missing_in_example':
                                        print(f"   Add: {issue['suggestion']}", file=sys.stderr)
                                    elif issue['type'] == 'exposed_secret':
                                        print(f"   Line {issue['line']}: {issue['variable']} contains a real secret!", file=sys.stderr)
                                        print(f"   Replace with a placeholder value", file=sys.stderr)
                            
                            if info_issues and not blocking:
                                missing_vars = [i['variable'] for i in info_issues if i['type'] == 'missing_in_env']
                                if missing_vars:
                                    print(f"\n💡 Optional: These variables are in .env.example but not .env:", file=sys.stderr)
                                    print(f"   {', '.join(missing_vars)}", file=sys.stderr)
                        
                        if blocking:
                            print("\n📝 Best Practices:", file=sys.stderr)
                            print("   • Keep .env.example updated with all required variables", file=sys.stderr)
                            print("   • Use descriptive placeholder values", file=sys.stderr)
                            print("   • Never commit real secrets to .env.example", file=sys.stderr)
                            print("   • Document variable purposes with comments", file=sys.stderr)
                            sys.exit(2)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in env sync validator hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()