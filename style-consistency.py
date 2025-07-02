#!/usr/bin/env python3
"""
Style consistency hook.
Enforces theme-aware CSS classes, ShadCN component usage, and consistent styling.
"""
import json
import re
import sys
from pathlib import Path


def check_hardcoded_colors(content):
    """Check for hardcoded color values."""
    issues = []
    
    # Patterns for hardcoded colors
    color_patterns = [
        (r'#[0-9a-fA-F]{3,6}\b', 'hex color'),
        (r'rgb\([^)]+\)', 'rgb color'),
        (r'rgba\([^)]+\)', 'rgba color'),
        (r'(?:bg|text|border)-(?:red|blue|green|yellow|purple|pink|gray)-\d{3}', 'Tailwind color without dark mode variant'),
    ]
    
    # Allowed patterns (theme-aware)
    allowed_patterns = [
        r'dark:',
        r'var\(--',
        r'currentColor',
        r'transparent',
        r'inherit',
        r'black',
        r'white',
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Skip comments and imports
        if line.strip().startswith('//') or line.strip().startswith('import'):
            continue
        
        for pattern, color_type in color_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                color_value = match.group(0)
                
                # Check if it's in an allowed context
                if not any(re.search(allowed, line) for allowed in allowed_patterns):
                    # Special case for Tailwind colors - check if they have dark: variant
                    if 'bg-' in color_value or 'text-' in color_value or 'border-' in color_value:
                        # Check if there's a corresponding dark: variant nearby
                        context = content[max(0, match.start() - 50):match.end() + 50]
                        if 'dark:' not in context:
                            issues.append((i + 1, f"Missing dark mode variant for {color_value}"))
                    else:
                        issues.append((i + 1, f"Hardcoded {color_type}: {color_value}"))
    
    return issues


def check_shadcn_imports(content):
    """Check for proper ShadCN component imports."""
    issues = []
    warnings = []
    
    # Common UI elements that should use ShadCN
    ui_patterns = {
        r'<button\b': 'Use ShadCN Button component instead of <button>',
        r'<input\b': 'Use ShadCN Input component instead of <input>',
        r'<select\b': 'Use ShadCN Select component instead of <select>',
        r'<textarea\b': 'Use ShadCN Textarea component instead of <textarea>',
        r'<dialog\b': 'Use ShadCN Dialog component instead of <dialog>',
        r'<details\b': 'Use ShadCN Accordion component instead of <details>',
    }
    
    # Check if ShadCN components are imported
    has_shadcn_imports = '@/components/ui/' in content
    
    # Look for UI elements that should use ShadCN
    for pattern, message in ui_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            # Check if the corresponding ShadCN component is imported
            component_name = message.split()[2]  # Extract component name
            if not re.search(f'from ["\']@/components/ui/{component_name.lower()}', content):
                warnings.append(message)
    
    return issues, warnings


def check_theme_consistency(content):
    """Check for theme-aware class usage."""
    issues = []
    
    # Patterns that need dark mode variants
    needs_dark_variant = [
        r'\bclassName\s*=\s*["\'][^"\']*(?:bg|text|border)-(?!transparent|current|inherit)',
        r'\bclass\s*=\s*["\'][^"\']*(?:bg|text|border)-(?!transparent|current|inherit)',
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        for pattern in needs_dark_variant:
            match = re.search(pattern, line)
            if match:
                class_content = match.group(0)
                # Check if it has a dark: variant
                if 'dark:' not in class_content and not any(skip in class_content for skip in ['slate', 'gray', 'neutral', 'zinc']):
                    # Extract the specific class that needs dark variant
                    color_class = re.search(r'((?:bg|text|border)-\S+)', class_content)
                    if color_class:
                        issues.append((i + 1, f"Consider adding dark mode variant for {color_class.group(1)}"))
    
    return issues


def check_spacing_consistency(content):
    """Check for consistent spacing values."""
    warnings = []
    
    # Check for inconsistent spacing
    spacing_pattern = r'(?:p|m|gap|space)-(\d+)'
    spacings = re.findall(spacing_pattern, content)
    
    if spacings:
        # Preferred spacing scale
        preferred_spacings = ['0', '1', '2', '3', '4', '5', '6', '8', '10', '12', '16', '20', '24']
        non_standard = [s for s in set(spacings) if s not in preferred_spacings]
        
        if non_standard:
            warnings.append(f"Non-standard spacing values found: {', '.join(non_standard)}. Consider using standard scale.")
    
    return warnings


def extract_content(tool_name, tool_input):
    """Extract content from different tool inputs."""
    if tool_name == 'Write':
        return tool_input.get('content', '')
    elif tool_name == 'Edit':
        return tool_input.get('new_string', '')
    elif tool_name == 'MultiEdit':
        # Combine all edits
        content = ""
        for edit in tool_input.get('edits', []):
            content += edit.get('new_string', '') + "\n"
        return content
    
    return ""


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Write/Edit/MultiEdit tools
        if tool_name not in ['Write', 'Edit', 'MultiEdit']:
            sys.exit(0)
        
        # Get file path
        file_path = tool_input.get('file_path', '')
        
        # Only check TypeScript/JavaScript files and style files
        if not any(file_path.endswith(ext) for ext in ['.tsx', '.jsx', '.ts', '.js', '.css']):
            sys.exit(0)
        
        # Skip test files and config files
        if any(pattern in file_path for pattern in ['test.', 'spec.', 'config.', '.config.', 'tailwind.']):
            sys.exit(0)
        
        # Extract content
        content = extract_content(tool_name, tool_input)
        if not content:
            sys.exit(0)
        
        all_issues = []
        all_warnings = []
        
        # Run checks for React/TSX files
        if file_path.endswith(('.tsx', '.jsx')):
            # Check for hardcoded colors
            color_issues = check_hardcoded_colors(content)
            for line_num, issue in color_issues:
                all_warnings.append(f"Line {line_num}: {issue}")
            
            # Check for ShadCN usage
            shadcn_issues, shadcn_warnings = check_shadcn_imports(content)
            all_issues.extend(shadcn_issues)
            all_warnings.extend(shadcn_warnings)
            
            # Check theme consistency
            theme_issues = check_theme_consistency(content)
            for line_num, issue in theme_issues:
                all_warnings.append(f"Line {line_num}: {issue}")
            
            # Check spacing consistency
            spacing_warnings = check_spacing_consistency(content)
            all_warnings.extend(spacing_warnings)
        
        # For CSS files, check for hardcoded colors
        elif file_path.endswith('.css'):
            color_issues = check_hardcoded_colors(content)
            for line_num, issue in color_issues:
                all_warnings.append(f"Line {line_num}: {issue}")
        
        # Output warnings (non-blocking)
        if all_warnings:
            print("Style consistency suggestions:", file=sys.stderr)
            for warning in all_warnings:
                print(f"💡 {warning}", file=sys.stderr)
            print("\nBest practices:", file=sys.stderr)
            print("• Always use theme-aware classes (with dark: variants)", file=sys.stderr)
            print("• Use ShadCN UI components for consistency", file=sys.stderr)
            print("• Use CSS variables for custom colors", file=sys.stderr)
            print("• Follow the project's spacing scale", file=sys.stderr)
        
        # Only block on critical issues
        if all_issues:
            print("Style consistency errors:", file=sys.stderr)
            for issue in all_issues:
                print(f"❌ {issue}", file=sys.stderr)
            sys.exit(2)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in style consistency hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()