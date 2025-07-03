#!/usr/bin/env python3
"""
Duplicate detection hook.
Prevents creation of duplicate routes, pages, API endpoints, and components.
"""
import json
import os
import re
import sys
from pathlib import Path


def find_project_root(start_path):
    """Find the project root by looking for package.json."""
    path = Path(start_path).resolve()
    
    while path != path.parent:
        if (path / 'package.json').exists():
            return path
        path = path.parent
    
    return Path(start_path).resolve()


def get_route_from_path(file_path, project_root):
    """Extract route from Next.js app directory structure."""
    try:
        rel_path = Path(file_path).relative_to(project_root)
        
        # Check if it's in app directory
        if rel_path.parts[0] == 'app' and 'page.tsx' in str(rel_path):
            # Build route from directory structure
            route_parts = []
            for part in rel_path.parts[1:-1]:  # Skip 'app' and filename
                if part.startswith('(') and part.endswith(')'):
                    # Route groups don't affect the URL
                    continue
                elif part.startswith('[') and part.endswith(']'):
                    # Dynamic routes
                    route_parts.append(part)
                else:
                    route_parts.append(part)
            
            return '/' + '/'.join(route_parts) if route_parts else '/'
    except:
        pass
    
    return None


def get_api_route_from_path(file_path, project_root):
    """Extract API route from file path."""
    try:
        rel_path = Path(file_path).relative_to(project_root)
        
        # Check for Next.js API routes
        if rel_path.parts[0] == 'app' and 'route.ts' in str(rel_path):
            route_parts = []
            for part in rel_path.parts[1:-1]:  # Skip 'app' and filename
                if part == 'api':
                    route_parts.append(part)
                elif not (part.startswith('(') and part.endswith(')')):
                    route_parts.append(part)
            
            return '/'.join(route_parts) if route_parts else None
        
        # Legacy pages/api structure
        elif len(rel_path.parts) > 2 and rel_path.parts[0] == 'pages' and rel_path.parts[1] == 'api':
            return 'api/' + '/'.join(rel_path.parts[2:]).replace('.ts', '').replace('.js', '')
    except:
        pass
    
    return None


def find_existing_routes(project_root):
    """Find all existing routes in the project."""
    routes = set()
    api_routes = set()
    
    # Check app directory (Next.js 13+)
    app_dir = project_root / 'app'
    if app_dir.exists():
        for page_file in app_dir.rglob('page.tsx'):
            route = get_route_from_path(str(page_file), project_root)
            if route:
                routes.add(route)
        
        for route_file in app_dir.rglob('route.ts'):
            api_route = get_api_route_from_path(str(route_file), project_root)
            if api_route:
                api_routes.add(api_route)
    
    # Check pages directory (legacy)
    pages_dir = project_root / 'pages'
    if pages_dir.exists():
        for page_file in pages_dir.rglob('*.tsx'):
            if 'api/' not in str(page_file):
                # Simple route extraction for pages directory
                rel_path = page_file.relative_to(pages_dir)
                route = '/' + str(rel_path).replace('.tsx', '').replace('/index', '')
                routes.add(route.replace('//', '/'))
    
    return routes, api_routes


def find_similar_components(component_name, project_root):
    """Find components with similar names."""
    similar = []
    
    # Common component directories
    comp_dirs = ['components', 'src/components', 'app/components']
    
    for comp_dir in comp_dirs:
        comp_path = project_root / comp_dir
        if comp_path.exists():
            for comp_file in comp_path.rglob('*.tsx'):
                existing_name = comp_file.stem
                
                # Check for exact match (case-insensitive)
                if existing_name.lower() == component_name.lower():
                    similar.append((existing_name, str(comp_file.relative_to(project_root)), 'exact'))
                
                # Check for similarity
                elif (component_name.lower() in existing_name.lower() or 
                      existing_name.lower() in component_name.lower()):
                    similar.append((existing_name, str(comp_file.relative_to(project_root)), 'similar'))
    
    return similar


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Write tool for new files
        if tool_name != 'Write':
            sys.exit(0)
        
        file_path = tool_input.get('file_path', '')
        if not file_path:
            sys.exit(0)
        
        # Find project root
        project_root = find_project_root(os.getcwd())
        
        warnings = []
        
        # Check for duplicate pages/routes
        if 'page.tsx' in file_path or 'page.jsx' in file_path:
            route = get_route_from_path(file_path, project_root)
            if route:
                existing_routes, _ = find_existing_routes(project_root)
                if route in existing_routes:
                    print(f"Duplicate route detected!\n", file=sys.stderr)
                    print(f"❌ Route '{route}' already exists", file=sys.stderr)
                    print(f"\nCheck existing pages before creating new ones.", file=sys.stderr)
                    sys.exit(2)
        
        # Check for duplicate API routes
        elif 'route.ts' in file_path or 'route.js' in file_path:
            api_route = get_api_route_from_path(file_path, project_root)
            if api_route:
                _, existing_api_routes = find_existing_routes(project_root)
                if api_route in existing_api_routes:
                    print(f"Duplicate API route detected!\n", file=sys.stderr)
                    print(f"❌ API route '{api_route}' already exists", file=sys.stderr)
                    print(f"\nCheck existing API routes before creating new ones.", file=sys.stderr)
                    sys.exit(2)
        
        # Check for similar component names
        elif file_path.endswith(('.tsx', '.jsx')) and 'components' in file_path:
            component_name = Path(file_path).stem
            similar_components = find_similar_components(component_name, project_root)
            
            exact_matches = [c for c in similar_components if c[2] == 'exact']
            if exact_matches:
                print(f"Duplicate component detected!\n", file=sys.stderr)
                for name, path, _ in exact_matches:
                    print(f"❌ Component '{name}' already exists at: {path}", file=sys.stderr)
                print(f"\nUse the existing component or choose a different name.", file=sys.stderr)
                sys.exit(2)
            
            similar_matches = [c for c in similar_components if c[2] == 'similar']
            if similar_matches:
                print(f"Similar components found:", file=sys.stderr)
                for name, path, _ in similar_matches:
                    print(f"⚠️  '{name}' at: {path}", file=sys.stderr)
                warnings.append("Consider if you can use or extend an existing component")
        
        # Check for duplicate utility functions
        elif file_path.endswith(('.ts', '.js')) and any(dir in file_path for dir in ['utils', 'lib', 'helpers']):
            file_name = Path(file_path).stem
            
            # Look for similar utility files
            for util_dir in ['utils', 'lib', 'helpers', 'src/utils', 'src/lib']:
                util_path = project_root / util_dir
                if util_path.exists():
                    for util_file in util_path.rglob('*.[tj]s'):
                        if util_file.stem.lower() == file_name.lower():
                            print(f"Duplicate utility file detected!\n", file=sys.stderr)
                            print(f"❌ Utility '{util_file.stem}' already exists at: {util_file.relative_to(project_root)}", file=sys.stderr)
                            print(f"\nExtend the existing utility file instead of creating a new one.", file=sys.stderr)
                            sys.exit(2)
        
        # Show warnings but don't block
        if warnings:
            for warning in warnings:
                print(f"⚠️  {warning}", file=sys.stderr)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in duplicate detection hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()