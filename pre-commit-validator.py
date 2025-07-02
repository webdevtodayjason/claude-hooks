#!/usr/bin/env python3
"""
Pre-commit validation hook that runs tests, linting, and TypeScript checks.
Blocks commits if any checks fail.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out after 120 seconds"
    except Exception as e:
        return False, "", str(e)


def find_project_root(start_path):
    """Find the project root by looking for package.json or other markers."""
    path = Path(start_path).resolve()
    markers = ['package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
    
    while path != path.parent:
        for marker in markers:
            if (path / marker).exists():
                return str(path)
        path = path.parent
    
    return start_path


def detect_project_type(project_root):
    """Detect the project type and available tools."""
    info = {
        'type': 'unknown',
        'package_manager': None,
        'has_typescript': False,
        'has_tests': False,
        'has_lint': False,
        'test_command': None,
        'lint_command': None,
        'ts_check_command': None
    }
    
    # Check for Node.js project
    package_json_path = Path(project_root) / 'package.json'
    if package_json_path.exists():
        info['type'] = 'node'
        
        # Detect package manager
        if (Path(project_root) / 'pnpm-lock.yaml').exists():
            info['package_manager'] = 'pnpm'
        elif (Path(project_root) / 'yarn.lock').exists():
            info['package_manager'] = 'yarn'
        elif (Path(project_root) / 'bun.lockb').exists():
            info['package_manager'] = 'bun'
        else:
            info['package_manager'] = 'npm'
        
        # Read package.json
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                scripts = package_data.get('scripts', {})
                deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                # Check for TypeScript
                if 'typescript' in deps or (Path(project_root) / 'tsconfig.json').exists():
                    info['has_typescript'] = True
                    
                    # Look for TypeScript check command
                    for script_name in ['typecheck', 'type-check', 'tsc', 'check-types']:
                        if script_name in scripts:
                            info['ts_check_command'] = f"{info['package_manager']} run {script_name}"
                            break
                    else:
                        # Fallback to direct tsc
                        info['ts_check_command'] = f"{info['package_manager']} exec tsc --noEmit"
                
                # Check for tests
                test_scripts = ['test', 'test:unit', 'test:all']
                for script in test_scripts:
                    if script in scripts and 'watch' not in scripts[script]:
                        info['has_tests'] = True
                        info['test_command'] = f"{info['package_manager']} run {script}"
                        break
                
                # Check for linting
                lint_scripts = ['lint', 'lint:all', 'lint:fix']
                for script in lint_scripts:
                    if script in scripts and 'fix' not in script:
                        info['has_lint'] = True
                        info['lint_command'] = f"{info['package_manager']} run {script}"
                        break
                        
        except Exception:
            pass
    
    # Check for Python project
    elif (Path(project_root) / 'pyproject.toml').exists() or (Path(project_root) / 'setup.py').exists():
        info['type'] = 'python'
        
        # Check for common Python tools
        if (Path(project_root) / 'pytest.ini').exists() or (Path(project_root) / 'tests').exists():
            info['has_tests'] = True
            info['test_command'] = 'pytest'
        
        if (Path(project_root) / '.ruff.toml').exists():
            info['has_lint'] = True
            info['lint_command'] = 'ruff check .'
        elif (Path(project_root) / '.flake8').exists():
            info['has_lint'] = True
            info['lint_command'] = 'flake8'
    
    return info


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        command = input_data.get('tool_input', {}).get('command', '')
        
        # Only process git commit/push commands
        if tool_name != 'Bash' or not any(cmd in command for cmd in ['git commit', 'git push']):
            sys.exit(0)
        
        # Find project root
        cwd = os.getcwd()
        project_root = find_project_root(cwd)
        
        # Detect project type and available tools
        project_info = detect_project_type(project_root)
        
        if project_info['type'] == 'unknown':
            # Can't determine project type, allow commit
            sys.exit(0)
        
        errors = []
        warnings = []
        
        # Run TypeScript checks if available
        if project_info['has_typescript'] and project_info['ts_check_command']:
            print(f"Running TypeScript checks...", file=sys.stderr)
            success, stdout, stderr = run_command(project_info['ts_check_command'], cwd=project_root)
            if not success:
                errors.append(f"TypeScript errors found:\n{stderr or stdout}")
        
        # Run linting if available
        if project_info['has_lint'] and project_info['lint_command']:
            print(f"Running lint checks...", file=sys.stderr)
            success, stdout, stderr = run_command(project_info['lint_command'], cwd=project_root)
            if not success:
                errors.append(f"Linting errors found:\n{stderr or stdout}")
        
        # Run tests if available (only for commits, not pushes to save time)
        if 'git commit' in command and project_info['has_tests'] and project_info['test_command']:
            print(f"Running tests...", file=sys.stderr)
            success, stdout, stderr = run_command(project_info['test_command'], cwd=project_root)
            if not success:
                errors.append(f"Test failures found:\n{stderr or stdout}")
        
        # If there are errors, block the commit
        if errors:
            print("Pre-commit checks failed!\n", file=sys.stderr)
            for error in errors:
                print(f"❌ {error}\n", file=sys.stderr)
            print("Fix these issues before committing.", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks the tool call
        
        # Success
        if warnings:
            for warning in warnings:
                print(f"⚠️  {warning}", file=sys.stderr)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in pre-commit hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()