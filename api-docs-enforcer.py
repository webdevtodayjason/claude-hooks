#!/usr/bin/env python3
"""
API Documentation and Security Enforcer Hook.
Ensures all API changes are documented in Swagger/OpenAPI, have Postman collections,
and implement proper security for internal APIs.
"""
import json
import os
import re
import sys
from pathlib import Path
import yaml


def load_swagger_doc(project_root):
    """Load Swagger/OpenAPI documentation."""
    # Check for common swagger/openapi file locations
    possible_paths = [
        'swagger.json',
        'openapi.json',
        'swagger.yaml',
        'openapi.yaml',
        'docs/swagger.json',
        'docs/openapi.json',
        'api-docs/swagger.json',
        'api-docs/openapi.yaml'
    ]
    
    for path in possible_paths:
        full_path = Path(project_root) / path
        if full_path.exists():
            if full_path.suffix == '.json':
                with open(full_path, 'r') as f:
                    return json.load(f), full_path
            else:  # YAML
                with open(full_path, 'r') as f:
                    return yaml.safe_load(f), full_path
    
    return None, None


def load_postman_collection(project_root):
    """Load Postman collection."""
    possible_paths = [
        'postman/collection.json',
        'postman_collection.json',
        'api.postman_collection.json',
        'docs/postman_collection.json'
    ]
    
    for path in possible_paths:
        full_path = Path(project_root) / path
        if full_path.exists():
            with open(full_path, 'r') as f:
                return json.load(f), full_path
    
    return None, None


def extract_api_endpoints_from_code(content, file_path):
    """Extract API endpoint definitions from code."""
    endpoints = []
    
    # Next.js App Router pattern
    if 'route.ts' in file_path or 'route.js' in file_path:
        # Extract HTTP methods
        methods = re.findall(r'export\s+async\s+function\s+(GET|POST|PUT|DELETE|PATCH)', content)
        # Extract route from file path
        route_match = re.search(r'/app(/api/[^/]+(?:/[^/]+)*)', file_path)
        if route_match and methods:
            route = route_match.group(1).replace('/route.ts', '').replace('/route.js', '')
            for method in methods:
                endpoints.append({
                    'path': route,
                    'method': method.upper(),
                    'file': file_path
                })
    
    # Express/FastAPI style routes
    route_patterns = [
        r'router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
        r'app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
        r'@(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
    ]
    
    for pattern in route_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for method, path in matches:
            endpoints.append({
                'path': path,
                'method': method.upper(),
                'file': file_path
            })
    
    return endpoints


def check_api_security(content, endpoint, file_path):
    """Check if API endpoint has proper security implementation."""
    security_issues = []
    
    # Check if it's an internal API
    internal_patterns = ['/internal/', '/admin/', '/system/', '/private/']
    is_internal = any(pattern in endpoint['path'] for pattern in internal_patterns)
    
    if is_internal:
        # Look for authentication checks
        auth_patterns = [
            r'request\.headers\.get\([\'"](?:x-api-key|authorization|api-key)',
            r'validateApiKey',
            r'checkAuth',
            r'requireAuth',
            r'isAuthenticated',
            r'verifyToken',
            r'middleware.*auth',
        ]
        
        has_auth = any(re.search(pattern, content, re.IGNORECASE) for pattern in auth_patterns)
        
        # Check for internal call bypass
        internal_bypass_patterns = [
            r'X-Internal-Call',
            r'isInternalIP',
            r'request\.ip',
            r'INTERNAL_SECRET',
        ]
        
        has_internal_bypass = any(re.search(pattern, content, re.IGNORECASE) for pattern in internal_bypass_patterns)
        
        if not has_auth:
            security_issues.append({
                'type': 'missing_auth',
                'message': f"Internal API endpoint {endpoint['method']} {endpoint['path']} lacks authentication",
                'suggestion': "Add API key validation or authentication middleware"
            })
        
        if has_auth and not has_internal_bypass:
            security_issues.append({
                'type': 'missing_internal_bypass',
                'message': f"Internal API {endpoint['path']} doesn't allow internal service calls",
                'suggestion': "Consider adding bypass for legitimate internal calls (with proper validation)"
            })
    
    return security_issues


def validate_swagger_completeness(swagger_doc, endpoints):
    """Validate that all endpoints are documented in Swagger."""
    issues = []
    
    if not swagger_doc:
        if endpoints:
            issues.append({
                'type': 'missing_swagger',
                'message': "No Swagger/OpenAPI documentation found",
                'suggestion': "Create swagger.json or openapi.yaml in project root or docs folder"
            })
        return issues
    
    # Get documented paths
    documented_paths = swagger_doc.get('paths', {})
    
    for endpoint in endpoints:
        path = endpoint['path']
        method = endpoint['method'].lower()
        
        # Normalize path parameters for comparison
        normalized_path = re.sub(r'\{[^}]+\}', '{}', path)
        
        # Check if endpoint is documented
        documented = False
        for doc_path in documented_paths:
            normalized_doc_path = re.sub(r'\{[^}]+\}', '{}', doc_path)
            if normalized_path == normalized_doc_path or path == doc_path:
                if method in documented_paths[doc_path]:
                    documented = True
                    # Additional checks for quality
                    endpoint_doc = documented_paths[doc_path][method]
                    
                    # Check for security definition
                    if 'security' not in endpoint_doc and any(p in path for p in ['/internal/', '/admin/', '/private/']):
                        issues.append({
                            'type': 'missing_security_def',
                            'message': f"{method.upper()} {path} missing security definition in Swagger",
                            'suggestion': "Add security: [{ apiKey: [] }] to the endpoint definition"
                        })
                    
                    # Check for response schemas
                    if 'responses' not in endpoint_doc or '200' not in endpoint_doc['responses']:
                        issues.append({
                            'type': 'incomplete_docs',
                            'message': f"{method.upper()} {path} missing response documentation",
                            'suggestion': "Add response schemas and examples"
                        })
                    
                    # Check for Postman link
                    description = endpoint_doc.get('description', '')
                    if 'postman' not in description.lower() and 'collection' not in description.lower():
                        issues.append({
                            'type': 'missing_postman_link',
                            'message': f"{method.upper()} {path} missing Postman collection link",
                            'suggestion': "Add Postman collection link to description"
                        })
                break
        
        if not documented:
            issues.append({
                'type': 'undocumented_endpoint',
                'message': f"Endpoint {method.upper()} {path} not documented in Swagger",
                'suggestion': f"Add documentation for this endpoint in {path}"
            })
    
    return issues


def validate_postman_collection(postman_collection, endpoints, swagger_doc):
    """Validate Postman collection completeness."""
    issues = []
    
    if not postman_collection and endpoints:
        issues.append({
            'type': 'missing_postman',
            'message': "No Postman collection found",
            'suggestion': "Create postman/collection.json or generate from Swagger"
        })
        return issues
    
    if not postman_collection:
        return issues
    
    # Extract requests from Postman collection
    postman_requests = []
    
    def extract_requests(items):
        for item in items:
            if 'request' in item:
                method = item['request'].get('method', '')
                url = item['request'].get('url', {})
                if isinstance(url, dict):
                    path = url.get('raw', '').split('{{')[0].split('?')[0]
                else:
                    path = url.split('{{')[0].split('?')[0]
                
                # Normalize path
                path = re.sub(r'https?://[^/]+', '', path)
                path = re.sub(r':\w+', '{}', path)  # Convert :param to {}
                
                postman_requests.append({
                    'method': method,
                    'path': path,
                    'name': item.get('name', '')
                })
            
            # Recurse into folders
            if 'item' in item:
                extract_requests(item['item'])
    
    extract_requests(postman_collection.get('item', []))
    
    # Check each endpoint
    for endpoint in endpoints:
        found = False
        normalized_endpoint = re.sub(r'\{[^}]+\}', '{}', endpoint['path'])
        
        for req in postman_requests:
            normalized_req = re.sub(r'\{[^}]+\}', '{}', req['path'])
            if (req['method'] == endpoint['method'] and 
                (normalized_req == normalized_endpoint or req['path'] == endpoint['path'])):
                found = True
                break
        
        if not found:
            issues.append({
                'type': 'missing_in_postman',
                'message': f"Endpoint {endpoint['method']} {endpoint['path']} missing from Postman collection",
                'suggestion': "Add this endpoint to the Postman collection"
            })
    
    # Check for auth configuration
    if not postman_collection.get('auth') and any('/internal/' in e['path'] or '/admin/' in e['path'] for e in endpoints):
        issues.append({
            'type': 'missing_postman_auth',
            'message': "Postman collection missing authentication configuration",
            'suggestion': "Add collection-level auth configuration for API keys"
        })
    
    return issues


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Process different tools
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Check for git commit commands
            if 'git commit' in command or 'git push' in command:
                # Run full API documentation check
                project_root = os.getcwd()
                
                # Get changed files
                import subprocess
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                changed_files = result.stdout.strip().split('\n') if result.stdout else []
                
                # Filter for API-related files
                api_files = [f for f in changed_files if any(pattern in f for pattern in 
                            ['/api/', 'route.ts', 'route.js', 'controller.', '.route.'])]
                
                if api_files:
                    all_issues = []
                    all_endpoints = []
                    
                    # Analyze each API file
                    for file_path in api_files:
                        if os.path.exists(file_path):
                            with open(file_path, 'r') as f:
                                content = f.read()
                            
                            endpoints = extract_api_endpoints_from_code(content, file_path)
                            all_endpoints.extend(endpoints)
                            
                            # Check security for each endpoint
                            for endpoint in endpoints:
                                security_issues = check_api_security(content, endpoint, file_path)
                                all_issues.extend(security_issues)
                    
                    if all_endpoints:
                        # Load documentation
                        swagger_doc, swagger_path = load_swagger_doc(project_root)
                        postman_collection, postman_path = load_postman_collection(project_root)
                        
                        # Validate Swagger documentation
                        swagger_issues = validate_swagger_completeness(swagger_doc, all_endpoints)
                        all_issues.extend(swagger_issues)
                        
                        # Validate Postman collection
                        postman_issues = validate_postman_collection(postman_collection, all_endpoints, swagger_doc)
                        all_issues.extend(postman_issues)
                        
                        # Output issues
                        if all_issues:
                            print("\n🚨 API Documentation & Security Issues Found:\n", file=sys.stderr)
                            
                            blocking_issues = []
                            warnings = []
                            
                            for issue in all_issues:
                                if issue['type'] in ['missing_auth', 'missing_swagger', 'undocumented_endpoint']:
                                    blocking_issues.append(issue)
                                else:
                                    warnings.append(issue)
                            
                            # Show blocking issues
                            if blocking_issues:
                                print("❌ BLOCKING ISSUES (must fix before commit):", file=sys.stderr)
                                for issue in blocking_issues:
                                    print(f"\n   • {issue['message']}", file=sys.stderr)
                                    print(f"     💡 {issue['suggestion']}", file=sys.stderr)
                            
                            # Show warnings
                            if warnings:
                                print("\n⚠️  WARNINGS (should fix):", file=sys.stderr)
                                for issue in warnings:
                                    print(f"\n   • {issue['message']}", file=sys.stderr)
                                    print(f"     💡 {issue['suggestion']}", file=sys.stderr)
                            
                            # Provide helpful commands
                            print("\n📝 Helpful commands:", file=sys.stderr)
                            print("   • Generate Swagger: npx swagger-jsdoc -d swaggerDef.js -o swagger.json", file=sys.stderr)
                            print("   • Convert to Postman: npx openapi-to-postmanv2 -s swagger.json -o postman/collection.json", file=sys.stderr)
                            print("   • Test collection: npx newman run postman/collection.json", file=sys.stderr)
                            
                            if blocking_issues:
                                sys.exit(2)  # Block the commit
        
        elif tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', '')
            
            # Check if it's an API file being edited
            if any(pattern in file_path for pattern in ['/api/', 'route.ts', 'route.js', 'controller.', '.route.']):
                content = ''
                if tool_name == 'Write':
                    content = tool_input.get('content', '')
                elif tool_name == 'Edit':
                    content = tool_input.get('new_string', '')
                elif tool_name == 'MultiEdit':
                    # Get the full content after edits
                    content = '\n'.join(edit.get('new_string', '') for edit in tool_input.get('edits', []))
                
                if content:
                    endpoints = extract_api_endpoints_from_code(content, file_path)
                    
                    if endpoints:
                        print("\n📌 API Endpoint Detected:", file=sys.stderr)
                        for endpoint in endpoints:
                            print(f"   • {endpoint['method']} {endpoint['path']}", file=sys.stderr)
                        
                        print("\n📝 Remember to:", file=sys.stderr)
                        print("   1. Update Swagger/OpenAPI documentation", file=sys.stderr)
                        print("   2. Update Postman collection", file=sys.stderr)
                        print("   3. Add security for internal APIs", file=sys.stderr)
                        print("   4. Include example requests/responses", file=sys.stderr)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in API docs enforcer hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()