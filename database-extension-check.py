#!/usr/bin/env python3
"""
Database schema protection hook.
Prevents new table creation and suggests extending existing tables.
"""
import json
import re
import sys
from pathlib import Path


def analyze_prisma_changes(content, file_path):
    """Analyze Prisma schema changes for new models."""
    errors = []
    warnings = []
    suggestions = []
    
    # Pattern to detect new models
    model_pattern = r'model\s+(\w+)\s*\{'
    
    # Try to read the existing file to compare
    existing_models = set()
    try:
        existing_content = Path(file_path).read_text()
        existing_models = set(re.findall(model_pattern, existing_content))
    except:
        # File doesn't exist yet or can't be read
        pass
    
    # Find all models in new content
    new_models = set(re.findall(model_pattern, content))
    
    # Check for newly added models
    added_models = new_models - existing_models
    
    if added_models:
        errors.append(f"New database tables detected: {', '.join(added_models)}")
        errors.append("Creating new tables is discouraged. Consider extending existing tables instead.")
        
        # Provide suggestions based on common patterns
        for model in added_models:
            if 'Setting' in model or 'Config' in model:
                suggestions.append(f"Consider adding fields to an existing settings table instead of creating {model}")
            elif 'Log' in model or 'History' in model:
                suggestions.append(f"Consider using an existing audit/activity table instead of creating {model}")
            elif 'Type' in model or 'Category' in model:
                suggestions.append(f"Consider using an enum or a field in the related table instead of creating {model}")
            elif 'Meta' in model or 'Data' in model:
                suggestions.append(f"Consider using JSON fields in the parent table instead of creating {model}")
            else:
                suggestions.append(f"Review if {model} functionality can be added to an existing related table")
    
    # Check for relationship patterns that could be simplified
    content_lines = content.split('\n')
    for i, line in enumerate(content_lines):
        # Check for many-to-many relations that might need a join table
        if '@relation' in line and added_models:
            warnings.append(f"Line {i+1}: Ensure relationships are properly configured")
    
    # Check for fields that might be better as enums
    for model in new_models:
        model_match = re.search(f'model\\s+{model}\\s*{{([^}}]+)}}', content, re.DOTALL)
        if model_match:
            model_content = model_match.group(1)
            if model_content.count('\n') < 5:  # Small model, might be better as enum
                warnings.append(f"Model '{model}' appears small. Consider using an enum instead")
    
    return errors, warnings, suggestions


def analyze_sql_changes(content):
    """Analyze SQL for CREATE TABLE statements."""
    errors = []
    
    # Pattern to detect CREATE TABLE
    create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?'
    
    tables = re.findall(create_table_pattern, content, re.IGNORECASE)
    if tables:
        errors.append(f"New tables detected in SQL: {', '.join(tables)}")
        errors.append("Consider extending existing tables instead of creating new ones")
    
    return errors


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Write/Edit/MultiEdit tools
        if tool_name not in ['Write', 'Edit', 'MultiEdit']:
            sys.exit(0)
        
        # Get file path and content
        file_path = tool_input.get('file_path', '')
        
        # Check if it's a database-related file
        if not any(pattern in file_path.lower() for pattern in ['schema.prisma', '.sql', 'migration', 'database', 'db']):
            sys.exit(0)
        
        errors = []
        warnings = []
        suggestions = []
        
        # Get content based on tool type
        if tool_name == 'Write':
            content = tool_input.get('content', '')
        elif tool_name == 'Edit':
            content = tool_input.get('new_string', '')
        else:  # MultiEdit
            # For MultiEdit, we need to analyze all changes
            content = ""
            for edit in tool_input.get('edits', []):
                content += edit.get('new_string', '') + "\n"
        
        # Analyze based on file type
        if 'schema.prisma' in file_path:
            errs, warns, suggs = analyze_prisma_changes(content, file_path)
            errors.extend(errs)
            warnings.extend(warns)
            suggestions.extend(suggs)
        elif '.sql' in file_path:
            errors.extend(analyze_sql_changes(content))
        
        # If there are errors, block the operation
        if errors:
            print("Database schema validation failed!\n", file=sys.stderr)
            for error in errors:
                print(f"❌ {error}", file=sys.stderr)
            
            if suggestions:
                print("\nSuggestions:", file=sys.stderr)
                for suggestion in suggestions:
                    print(f"💡 {suggestion}", file=sys.stderr)
            
            print("\nBest practices:", file=sys.stderr)
            print("• Extend existing tables with new fields", file=sys.stderr)
            print("• Use JSON fields for flexible data", file=sys.stderr)
            print("• Use enums for type/category data", file=sys.stderr)
            print("• Consider database normalization principles", file=sys.stderr)
            
            sys.exit(2)  # Block the operation
        
        # Show warnings but don't block
        if warnings:
            for warning in warnings:
                print(f"⚠️  {warning}", file=sys.stderr)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in database schema hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()