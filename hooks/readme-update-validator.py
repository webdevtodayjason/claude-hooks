#!/usr/bin/env python3
"""
README Update Validator Hook.
Ensures README is updated when features are added or changed.
"""
import json
import os
import re
import sys
from pathlib import Path


def find_readme_files():
    """Find all README files in the project."""
    readme_files = []
    patterns = ['README.md', 'README.rst', 'README.txt', 'readme.md', 'Readme.md']
    
    for pattern in patterns:
        path = Path(pattern)
        if path.exists():
            readme_files.append(str(path))
    
    # Also check docs folder
    docs_patterns = ['docs/README.md', 'documentation/README.md']
    for pattern in docs_patterns:
        path = Path(pattern)
        if path.exists():
            readme_files.append(str(path))
    
    return readme_files


def analyze_changes(files):
    """Analyze changed files to determine what README updates might be needed."""
    suggestions = []
    
    # Categorize changes
    new_features = []
    api_changes = []
    config_changes = []
    dependency_changes = []
    script_changes = []
    hook_changes = []
    component_changes = []
    
    for file_path in files:
        # Skip if file was deleted
        if not os.path.exists(file_path):
            continue
        
        file_lower = file_path.lower()
        
        # New API endpoints
        if any(pattern in file_path for pattern in ['/api/', 'route.', 'controller.', 'endpoint']):
            api_changes.append(file_path)
        
        # Configuration files
        elif any(pattern in file_lower for pattern in ['config.', 'settings.', '.env.example']):
            config_changes.append(file_path)
        
        # Dependencies
        elif file_path in ['package.json', 'requirements.txt', 'Gemfile', 'go.mod', 'Cargo.toml', 'pom.xml']:
            dependency_changes.append(file_path)
        
        # Scripts
        elif file_path.endswith(('.sh', '.bash')) or 'scripts/' in file_path:
            script_changes.append(file_path)
        
        # Hooks (for this project specifically)
        elif file_path.endswith('.py') and 'hook' in file_lower:
            hook_changes.append(file_path)
        
        # UI Components
        elif any(pattern in file_path for pattern in ['/components/', '/pages/', '/views/']):
            component_changes.append(file_path)
        
        # New features (heuristic)
        elif any(pattern in file_lower for pattern in ['feature', 'service', 'util', 'helper', 'lib']):
            new_features.append(file_path)
    
    # Generate suggestions based on changes
    if api_changes:
        suggestions.append({
            'type': 'api',
            'files': api_changes,
            'sections': ['API Documentation', 'API Reference', 'Endpoints', 'Routes'],
            'suggestion': 'Document new API endpoints, request/response formats, and authentication'
        })
    
    if config_changes:
        suggestions.append({
            'type': 'configuration',
            'files': config_changes,
            'sections': ['Configuration', 'Environment Variables', 'Setup', 'Installation'],
            'suggestion': 'Update configuration instructions and environment variable documentation'
        })
    
    if dependency_changes:
        suggestions.append({
            'type': 'dependencies',
            'files': dependency_changes,
            'sections': ['Installation', 'Requirements', 'Dependencies', 'Prerequisites'],
            'suggestion': 'Update installation instructions and dependency requirements'
        })
    
    if script_changes:
        suggestions.append({
            'type': 'scripts',
            'files': script_changes,
            'sections': ['Scripts', 'Usage', 'Commands', 'Development'],
            'suggestion': 'Document new scripts, their purpose, and usage examples'
        })
    
    if hook_changes:
        suggestions.append({
            'type': 'hooks',
            'files': hook_changes,
            'sections': ['Hooks Overview', 'Configuration', 'Features'],
            'suggestion': 'Update hooks documentation with new hooks and their purposes'
        })
    
    if component_changes:
        suggestions.append({
            'type': 'components',
            'files': component_changes,
            'sections': ['Components', 'UI Documentation', 'Features'],
            'suggestion': 'Document new UI components and their usage'
        })
    
    if new_features:
        suggestions.append({
            'type': 'features',
            'files': new_features,
            'sections': ['Features', 'What\'s New', 'Functionality'],
            'suggestion': 'Add documentation for new features and capabilities'
        })
    
    return suggestions


def check_readme_sections(readme_path, suggestions):
    """Check if README has sections for the suggested updates."""
    if not os.path.exists(readme_path):
        return []
    
    with open(readme_path, 'r') as f:
        content = f.read().lower()
    
    missing_sections = []
    
    for suggestion in suggestions:
        # Check if any of the suggested sections exist
        has_section = False
        for section in suggestion['sections']:
            if section.lower() in content:
                has_section = True
                break
        
        if not has_section:
            missing_sections.append({
                'type': suggestion['type'],
                'suggested_sections': suggestion['sections'],
                'reason': suggestion['suggestion']
            })
    
    return missing_sections


def check_for_new_files_without_docs(files):
    """Check for new significant files that might need documentation."""
    new_files_needing_docs = []
    
    significant_patterns = [
        (r'.*\.(sh|bash)$', 'Script'),
        (r'.*/hooks/.*\.py$', 'Hook'),
        (r'.*/api/.*', 'API endpoint'),
        (r'.*config.*\.(json|yml|yaml)$', 'Configuration file'),
        (r'.*/components/.*', 'Component'),
        (r'.*/utils/.*', 'Utility'),
        (r'.*/services/.*', 'Service'),
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            for pattern, file_type in significant_patterns:
                if re.match(pattern, file_path):
                    # Check if it's a new file (simple heuristic)
                    try:
                        import subprocess
                        result = subprocess.run(['git', 'diff', '--cached', file_path], 
                                              capture_output=True, text=True)
                        if result.stdout and '--- /dev/null' in result.stdout:
                            new_files_needing_docs.append({
                                'file': file_path,
                                'type': file_type
                            })
                    except:
                        pass
                    break
    
    return new_files_needing_docs


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only check on git commits
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'git commit' in command:
                import subprocess
                
                # Get staged files
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                staged_files = result.stdout.strip().split('\n') if result.stdout else []
                
                # Filter out deleted files and README itself
                staged_files = [f for f in staged_files if f and not f.lower().startswith('readme')]
                
                if staged_files:
                    # Find README files
                    readme_files = find_readme_files()
                    
                    if not readme_files:
                        print("\n📝 No README file found!", file=sys.stderr)
                        print("   Consider creating a README.md to document your project", file=sys.stderr)
                    else:
                        # Analyze changes
                        suggestions = analyze_changes(staged_files)
                        
                        # Check for new files
                        new_files = check_for_new_files_without_docs(staged_files)
                        
                        # Check if README is being updated
                        readme_updated = any('readme' in f.lower() for f in staged_files)
                        
                        if (suggestions or new_files) and not readme_updated:
                            print("\n📚 README Update Reminder:\n", file=sys.stderr)
                            
                            if new_files:
                                print("🆕 New files added that may need documentation:", file=sys.stderr)
                                for file_info in new_files[:5]:  # Limit output
                                    print(f"   • {file_info['file']} ({file_info['type']})", file=sys.stderr)
                                print("", file=sys.stderr)
                            
                            if suggestions:
                                print("📝 Based on your changes, consider updating these README sections:", file=sys.stderr)
                                for suggestion in suggestions:
                                    print(f"\n   {suggestion['type'].upper()} changes detected:", file=sys.stderr)
                                    print(f"   Files: {', '.join(suggestion['files'][:3])}", file=sys.stderr)
                                    if len(suggestion['files']) > 3:
                                        print(f"          ... and {len(suggestion['files']) - 3} more", file=sys.stderr)
                                    print(f"   💡 {suggestion['suggestion']}", file=sys.stderr)
                                    print(f"   📍 Suggested sections: {', '.join(suggestion['sections'][:2])}", file=sys.stderr)
                            
                            # Check for missing sections
                            for readme_path in readme_files[:1]:  # Check main README only
                                missing = check_readme_sections(readme_path, suggestions)
                                if missing:
                                    print(f"\n⚠️  {readme_path} might be missing sections for:", file=sys.stderr)
                                    for section in missing[:3]:
                                        print(f"   • {section['type']}: Add a '{section['suggested_sections'][0]}' section", file=sys.stderr)
                            
                            print("\n💡 Tips for good documentation:", file=sys.stderr)
                            print("   • Include usage examples for new features", file=sys.stderr)
                            print("   • Update installation steps if dependencies changed", file=sys.stderr)
                            print("   • Document environment variables and configuration", file=sys.stderr)
                            print("   • Add API documentation with request/response examples", file=sys.stderr)
                            
                            # This is a warning, not blocking
                            print("\n✅ Proceeding with commit - don't forget to update docs later!", file=sys.stderr)
        
        # Handle writing to files - suggest README updates for significant new files
        elif tool_name == 'Write':
            file_path = tool_input.get('file_path', '')
            
            # Check if creating a significant new file
            significant_new_files = [
                ('api/', 'API endpoint'),
                ('/hooks/', 'hook'),
                ('/scripts/', 'script'),
                ('config', 'configuration file'),
                ('/components/', 'component'),
            ]
            
            for pattern, file_type in significant_new_files:
                if pattern in file_path.lower():
                    print(f"\n📝 Creating new {file_type}: {file_path}", file=sys.stderr)
                    print("   Remember to update README with:", file=sys.stderr)
                    print(f"   • Purpose and functionality", file=sys.stderr)
                    print(f"   • Usage instructions", file=sys.stderr)
                    print(f"   • Configuration details", file=sys.stderr)
                    break
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in README update validator hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()