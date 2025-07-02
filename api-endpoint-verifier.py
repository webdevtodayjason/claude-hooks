#!/usr/bin/env python3
"""
API endpoint verification hook.
Verifies API endpoints are properly configured and follow conventions.
"""
import json
import re
import sys
from pathlib import Path


def extract_api_methods(content):
    """Extract HTTP methods from route handler."""
    methods = []
    
    # Next.js 13+ App Router patterns
    method_patterns = [
        r'export\s+async\s+function\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)',
        r'export\s+function\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)',
        r'export\s+const\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)',
    ]
    
    for pattern in method_patterns:
        matches = re.findall(pattern, content)
        methods.extend(matches)
    
    # Legacy API routes (pages/api)
    if 'export default' in content:
        if 'req.method' in content:
            # Extract methods from switch/if statements
            method_checks = re.findall(r'req\.method\s*===?\s*[\'"](\w+)[\'"]', content)
            methods.extend(method_checks)
    
    return list(set(methods))


def check_api_response_format(content):
    """Check if API responses follow consistent format."""
    issues = []
    warnings = []
    
    # Check for consistent response patterns
    response_patterns = {
        'NextResponse.json': r'NextResponse\.json\(',
        'res.json': r'res\.json\(',
        'Response.json': r'new\s+Response.*?JSON\.stringify\(',
        'return json': r'return\s+.*?\.json\(',
    }
    
    response_types = []
    for name, pattern in response_patterns.items():
        if re.search(pattern, content):
            response_types.append(name)
    
    # Check for mixed response types
    if len(response_types) > 1:
        warnings.append(f"Mixed response types found: {', '.join(response_types)}. Use consistent response format.")
    
    # Check for error handling
    if not any(pattern in content for pattern in ['try', 'catch', '.catch', 'error']):
        warnings.append("No error handling found. Consider adding try-catch blocks.")
    
    # Check for status codes
    if 'status(' not in content and 'status:' not in content:
        warnings.append("No explicit status codes found. Consider setting appropriate HTTP status codes.")
    
    return issues, warnings


def check_api_authentication(content, file_path):
    """Check if API routes have authentication."""
    warnings = []
    
    # Skip if it's a public API route
    public_indicators = ['public', 'webhook', 'health', 'ping']
    if any(indicator in file_path.lower() for indicator in public_indicators):
        return warnings
    
    # Check for authentication patterns
    auth_patterns = [
        r'getServerSession',
        r'verifyToken',
        r'authenticate',
        r'requireAuth',
        r'withAuth',
        r'auth\(',
        r'currentUser',
        r'getUser',
        r'clerk',
        r'useAuth',
    ]
    
    has_auth = any(re.search(pattern, content, re.IGNORECASE) for pattern in auth_patterns)
    
    if not has_auth:
        warnings.append("No authentication check found. Ensure this API route is properly secured.")
    
    return warnings


def check_api_validation(content):
    """Check for input validation."""
    warnings = []
    
    # Check for validation patterns
    validation_patterns = [
        r'zod',
        r'yup',
        r'joi',
        r'validate',
        r'schema',
        r'\.parse\(',
        r'\.safeParse\(',
    ]
    
    has_validation = any(re.search(pattern, content, re.IGNORECASE) for pattern in validation_patterns)
    
    # Check if there's body/query/params access without validation
    access_patterns = [
        r'req\.body',
        r'request\.json\(',
        r'searchParams',
        r'params\.',
    ]
    
    has_data_access = any(re.search(pattern, content) for pattern in access_patterns)
    
    if has_data_access and not has_validation:
        warnings.append("API accesses request data without apparent validation. Consider adding input validation.")
    
    return warnings


def check_api_naming_convention(file_path):
    """Check API route naming conventions."""
    warnings = []
    
    path_parts = Path(file_path).parts
    
    # Check for RESTful naming
    if 'api' in path_parts:
        api_index = path_parts.index('api')
        resource_parts = path_parts[api_index + 1:]
        
        # Check for proper resource naming
        for part in resource_parts:
            if part not in ['route.ts', 'route.js', 'index.ts', 'index.js']:
                # Resources should be plural nouns
                if not part.endswith('s') and part not in ['auth', 'health', 'config', 'webhook']:
                    warnings.append(f"Resource '{part}' should be plural (e.g., '{part}s') for RESTful conventions")
                
                # Check for kebab-case
                if '_' in part:
                    warnings.append(f"Use kebab-case instead of snake_case: '{part}'")
                
                # Check for camelCase in URLs
                if part != part.lower():
                    warnings.append(f"Use lowercase for API routes: '{part}'")
    
    return warnings


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
        
        # Only check API route files
        if not any(pattern in file_path for pattern in ['route.ts', 'route.js', '/api/']):
            sys.exit(0)
        
        # Get content based on tool type
        if tool_name == 'Write':
            content = tool_input.get('content', '')
        elif tool_name == 'Edit':
            content = tool_input.get('new_string', '')
        else:  # MultiEdit
            content = ""
            for edit in tool_input.get('edits', []):
                content += edit.get('new_string', '') + "\n"
        
        all_issues = []
        all_warnings = []
        
        # Run checks
        methods = extract_api_methods(content)
        if not methods and 'route.' in file_path:
            all_issues.append("No HTTP method handlers found (GET, POST, etc.)")
        
        # Check response format
        issues, warnings = check_api_response_format(content)
        all_issues.extend(issues)
        all_warnings.extend(warnings)
        
        # Check authentication
        auth_warnings = check_api_authentication(content, file_path)
        all_warnings.extend(auth_warnings)
        
        # Check validation
        validation_warnings = check_api_validation(content)
        all_warnings.extend(validation_warnings)
        
        # Check naming conventions
        naming_warnings = check_api_naming_convention(file_path)
        all_warnings.extend(naming_warnings)
        
        # Output warnings (non-blocking)
        if all_warnings:
            print("API endpoint suggestions:", file=sys.stderr)
            for warning in all_warnings:
                print(f"💡 {warning}", file=sys.stderr)
            print("\nBest practices:", file=sys.stderr)
            print("• Use consistent response formats", file=sys.stderr)
            print("• Add authentication for protected routes", file=sys.stderr)
            print("• Validate all input data", file=sys.stderr)
            print("• Follow RESTful naming conventions", file=sys.stderr)
            print("• Include proper error handling", file=sys.stderr)
        
        # Only block on critical issues
        if all_issues:
            print("API endpoint errors:", file=sys.stderr)
            for issue in all_issues:
                print(f"❌ {issue}", file=sys.stderr)
            sys.exit(2)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in API verification hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()