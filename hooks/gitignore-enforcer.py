#!/usr/bin/env python3
"""
Gitignore Enforcer Hook.
Ensures .gitignore exists and prevents committing sensitive or unnecessary files.
"""
import json
import os
import re
import sys
from pathlib import Path


# Files/patterns that should always be in .gitignore
REQUIRED_GITIGNORE_PATTERNS = {
    'environment': [
        '.env',
        '.env.*',
        '!.env.example',
        '!.env.sample',
        '!.env.template',
    ],
    'secrets': [
        '*.pem',
        '*.key',
        '*.cert',
        '*.p12',
        '*.pfx',
        'secrets.yml',
        'secrets.json',
        'credentials.json',
        'service-account*.json',
    ],
    'ide': [
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        '*~',
        '.DS_Store',
        'Thumbs.db',
    ],
    'dependencies': [
        'node_modules/',
        'vendor/',
        'venv/',
        'env/',
        '__pycache__/',
        '*.pyc',
        '.pytest_cache/',
    ],
    'build': [
        'dist/',
        'build/',
        'out/',
        '*.log',
        '*.tmp',
        '.next/',
        '.nuxt/',
        '.cache/',
    ],
    'test': [
        'coverage/',
        '.nyc_output/',
        '*.test.log',
        'test-results/',
        'playwright-report/',
        'test-artifacts/',
    ],
    'database': [
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        'database.yml',
    ]
}

# Files that should NEVER be committed
FORBIDDEN_FILES = {
    'private_keys': [
        r'.*\.pem$',
        r'.*\.key$',
        r'.*private.*key.*',
        r'id_rsa.*',
        r'id_dsa.*',
        r'id_ecdsa.*',
        r'id_ed25519.*',
    ],
    'env_files': [
        r'^\.env$',
        r'^\.env\.[^.]+$',
        r'.*\.env\.(?!example|sample|template).*$',
    ],
    'credentials': [
        r'.*credentials.*\.(json|yml|yaml)$',
        r'.*service[-_]?account.*\.json$',
        r'.*secrets?\.(json|yml|yaml|txt)$',
        r'.*password.*\.(txt|json|yml|yaml)$',
    ],
    'test_scripts': [
        r'.*test[-_]?script.*\.(sh|bash|py|js)$',
        r'.*scratch.*\.(py|js|ts|sh)$',
        r'.*temp[-_]?test.*',
        r'.*debug[-_]?script.*',
    ],
    'backups': [
        r'.*\.backup$',
        r'.*\.bak$',
        r'.*\.old$',
        r'.*~$',
        r'.*\.(orig|save)$',
    ],
    'archives': [
        r'.*\.(zip|tar|tar\.gz|tgz|rar|7z)$',
    ],
    'large_files': [
        r'.*\.(mp4|avi|mov|mkv|wmv)$',  # Videos
        r'.*\.(psd|ai|sketch|fig)$',  # Design files
        r'.*\.(exe|dmg|pkg|deb|rpm)$',  # Executables
    ]
}

# Files that might be okay but should prompt a warning
WARNING_FILES = {
    'configs': [
        r'config\.(json|yml|yaml)$',
        r'settings\.(json|yml|yaml)$',
    ],
    'data': [
        r'.*\.(csv|xlsx|xls)$',
        r'.*\.sql$',
        r'.*dump.*',
    ],
    'logs': [
        r'.*\.log$',
        r'debug\.txt$',
        r'error\.txt$',
    ]
}


def check_gitignore_exists():
    """Check if .gitignore exists."""
    gitignore_path = Path('.gitignore')
    return gitignore_path.exists(), gitignore_path


def parse_gitignore(gitignore_path):
    """Parse .gitignore file and return patterns."""
    patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def check_missing_patterns(gitignore_patterns):
    """Check for missing required patterns in .gitignore."""
    missing = {}
    
    for category, required_patterns in REQUIRED_GITIGNORE_PATTERNS.items():
        category_missing = []
        for pattern in required_patterns:
            # Skip negation patterns for this check
            if pattern.startswith('!'):
                continue
            
            # Check if pattern or a broader version exists
            found = False
            for gitignore_pattern in gitignore_patterns:
                # Direct match
                if pattern == gitignore_pattern:
                    found = True
                    break
                
                # Check for broader patterns
                if pattern.endswith('/') and gitignore_pattern == pattern.rstrip('/'):
                    found = True
                    break
                
                # Check for wildcard matches
                if '*' in gitignore_pattern:
                    # Simple wildcard matching
                    regex_pattern = gitignore_pattern.replace('*', '.*').replace('?', '.')
                    if re.match(f'^{regex_pattern}$', pattern):
                        found = True
                        break
            
            if not found:
                category_missing.append(pattern)
        
        if category_missing:
            missing[category] = category_missing
    
    return missing


def check_forbidden_files(files):
    """Check if any forbidden files are being committed."""
    issues = []
    
    for file_path in files:
        # Skip if file doesn't exist (deleted files)
        if not os.path.exists(file_path):
            continue
        
        # Check against forbidden patterns
        for category, patterns in FORBIDDEN_FILES.items():
            for pattern in patterns:
                if re.match(pattern, file_path, re.IGNORECASE):
                    issues.append({
                        'file': file_path,
                        'category': category,
                        'severity': 'high'
                    })
                    break
        
        # Check against warning patterns
        for category, patterns in WARNING_FILES.items():
            for pattern in patterns:
                if re.match(pattern, file_path, re.IGNORECASE):
                    # Check if it's already in issues
                    if not any(issue['file'] == file_path for issue in issues):
                        issues.append({
                            'file': file_path,
                            'category': category,
                            'severity': 'medium'
                        })
                    break
    
    return issues


def suggest_gitignore_additions(forbidden_files):
    """Suggest .gitignore patterns for forbidden files."""
    suggestions = set()
    
    for issue in forbidden_files:
        file_path = issue['file']
        category = issue['category']
        
        if category == 'env_files':
            if file_path == '.env':
                suggestions.add('.env')
            else:
                suggestions.add('.env.*')
        elif category == 'private_keys':
            if file_path.endswith('.pem'):
                suggestions.add('*.pem')
            elif file_path.endswith('.key'):
                suggestions.add('*.key')
            else:
                suggestions.add(file_path)
        elif category == 'test_scripts':
            suggestions.add('*test-script*')
            suggestions.add('*scratch*')
        elif category == 'backups':
            ext = Path(file_path).suffix
            if ext:
                suggestions.add(f'*{ext}')
        else:
            # For other categories, suggest the specific file
            suggestions.add(file_path)
    
    return sorted(suggestions)


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Handle git commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'git add' in command or 'git commit' in command:
                import subprocess
                
                # Check if .gitignore exists
                exists, gitignore_path = check_gitignore_exists()
                if not exists:
                    print("\n❌ No .gitignore file found!", file=sys.stderr)
                    print("   Create a .gitignore file to prevent committing sensitive files", file=sys.stderr)
                    print("\n   Suggested initial .gitignore:", file=sys.stderr)
                    print("   ```", file=sys.stderr)
                    for category, patterns in REQUIRED_GITIGNORE_PATTERNS.items():
                        print(f"   # {category.title()}", file=sys.stderr)
                        for pattern in patterns[:3]:  # Show first 3 from each category
                            print(f"   {pattern}", file=sys.stderr)
                        print("", file=sys.stderr)
                    print("   ```", file=sys.stderr)
                    sys.exit(2)
                
                # Parse existing .gitignore
                gitignore_patterns = parse_gitignore(gitignore_path)
                
                # Check for missing required patterns
                missing = check_missing_patterns(gitignore_patterns)
                
                # Get staged files
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                staged_files = result.stdout.strip().split('\n') if result.stdout else []
                
                # Check for forbidden files
                forbidden = check_forbidden_files(staged_files)
                
                # Output results
                if missing or forbidden:
                    print("\n🚨 Gitignore Security Check:\n", file=sys.stderr)
                    
                    blocking = False
                    
                    # Show forbidden files
                    high_severity = [f for f in forbidden if f['severity'] == 'high']
                    medium_severity = [f for f in forbidden if f['severity'] == 'medium']
                    
                    if high_severity:
                        blocking = True
                        print("❌ FORBIDDEN FILES (must not commit):", file=sys.stderr)
                        for issue in high_severity:
                            print(f"   • {issue['file']} ({issue['category'].replace('_', ' ')})", file=sys.stderr)
                        
                        # Suggest gitignore additions
                        suggestions = suggest_gitignore_additions(high_severity)
                        if suggestions:
                            print("\n   Add to .gitignore:", file=sys.stderr)
                            for suggestion in suggestions:
                                print(f"   {suggestion}", file=sys.stderr)
                    
                    if medium_severity:
                        print("\n⚠️  WARNING FILES (review before committing):", file=sys.stderr)
                        for issue in medium_severity:
                            print(f"   • {issue['file']} ({issue['category'].replace('_', ' ')})", file=sys.stderr)
                    
                    # Show missing gitignore patterns
                    if missing:
                        print("\n📝 Missing .gitignore patterns:", file=sys.stderr)
                        for category, patterns in missing.items():
                            print(f"\n   {category.title()}:", file=sys.stderr)
                            for pattern in patterns:
                                print(f"   • {pattern}", file=sys.stderr)
                    
                    print("\n💡 Best Practices:", file=sys.stderr)
                    print("   • Never commit .env files or private keys", file=sys.stderr)
                    print("   • Keep test scripts and temporary files out of the repo", file=sys.stderr)
                    print("   • Use .gitignore to exclude build artifacts and dependencies", file=sys.stderr)
                    print("   • Review data files before committing", file=sys.stderr)
                    
                    if blocking:
                        print("\n❌ Commit blocked due to forbidden files", file=sys.stderr)
                        sys.exit(2)
        
        # Handle file creation
        elif tool_name == 'Write':
            file_path = tool_input.get('file_path', '')
            
            # Check if creating a potentially sensitive file
            for category, patterns in FORBIDDEN_FILES.items():
                for pattern in patterns:
                    if re.match(pattern, file_path, re.IGNORECASE):
                        print(f"\n⚠️  Creating {category.replace('_', ' ')} file: {file_path}", file=sys.stderr)
                        print("   Remember to add this to .gitignore if it contains sensitive data", file=sys.stderr)
                        break
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in gitignore enforcer hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()