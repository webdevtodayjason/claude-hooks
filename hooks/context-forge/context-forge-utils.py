#!/usr/bin/env python3
"""
Utility functions for Context Forge hooks
Provides advanced stage detection, PRP analysis, and context extraction
"""

import re
import json
from pathlib import Path
from datetime import datetime

def analyze_implementation_stage(implementation_path=None):
    """
    Analyze Implementation.md to understand stages and current progress
    Returns dict with stage information
    """
    if implementation_path is None:
        implementation_path = Path.cwd() / "Docs" / "Implementation.md"
    
    if not implementation_path.exists():
        return None
        
    stages = {}
    current_stage = None
    
    try:
        with open(implementation_path, 'r') as f:
            content = f.read()
            
        # Find all stages
        stage_pattern = r'##\s*(Stage\s*\d+)[:\s-]*(.*?)(?=##\s*Stage|\Z)'
        matches = re.findall(stage_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (stage_name, stage_content) in enumerate(matches):
            stage_name = stage_name.strip()
            
            # Extract stage title
            title_match = re.search(r'^(.*?)[\n\r]', stage_content.strip())
            title = title_match.group(1).strip() if title_match else ""
            
            # Count tasks (look for checkboxes)
            total_tasks = len(re.findall(r'^\s*-\s*\[[ x]\]', stage_content, re.MULTILINE))
            completed_tasks = len(re.findall(r'^\s*-\s*\[x\]', stage_content, re.MULTILINE))
            
            stages[stage_name] = {
                "title": title,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "progress": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "content_preview": stage_content[:200].strip()
            }
            
        return stages
        
    except Exception as e:
        return None

def detect_active_features(transcript_path=None):
    """
    Analyze transcript to detect which features are being worked on
    """
    features = []
    
    # Common feature keywords to look for
    feature_keywords = [
        "authentication", "auth", "login", "signup",
        "database", "schema", "model",
        "api", "endpoint", "route",
        "frontend", "ui", "component",
        "testing", "test", "spec",
        "deployment", "docker", "ci/cd"
    ]
    
    try:
        if transcript_path and Path(transcript_path).exists():
            with open(transcript_path, 'r') as f:
                # Read last 10KB to avoid processing huge files
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                f.seek(max(0, file_size - 10240))  # Go back 10KB
                recent_content = f.read().lower()
                
            for keyword in feature_keywords:
                if keyword in recent_content:
                    features.append(keyword)
                    
    except Exception:
        pass
        
    return list(set(features))  # Remove duplicates

def get_prp_summary():
    """
    Get a summary of available PRPs and their purposes
    """
    prp_dir = Path.cwd() / "PRPs"
    
    if not prp_dir.exists():
        return {}
        
    prp_info = {}
    
    # Standard PRPs and their purposes
    prp_purposes = {
        "base.md": "Core implementation blueprint with pseudocode",
        "planning.md": "Architecture decisions and system design",
        "spec.md": "Technical specifications and API details",
        "validation-gate.md": "Quality checkpoints and validation criteria"
    }
    
    for prp_file in prp_dir.glob("*.md"):
        purpose = prp_purposes.get(prp_file.name, "Custom PRP file")
        
        # Try to extract first heading as description
        try:
            with open(prp_file, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith("#"):
                    purpose = first_line.lstrip("#").strip()
        except Exception:
            pass
            
        prp_info[prp_file.name] = {
            "path": str(prp_file),
            "purpose": purpose,
            "size": prp_file.stat().st_size,
            "modified": datetime.fromtimestamp(prp_file.stat().st_mtime).isoformat()
        }
        
    return prp_info

def get_project_tech_stack():
    """
    Extract tech stack information from CLAUDE.md or config
    """
    tech_stack = {
        "frontend": None,
        "backend": None,
        "database": None,
        "detected": []
    }
    
    # Try to read from Context Forge config first
    config_path = Path.cwd() / ".context-forge" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "techStack" in config:
                    tech_stack.update(config["techStack"])
        except Exception:
            pass
    
    # Also check CLAUDE.md for tech stack mentions
    claude_md = Path.cwd() / "CLAUDE.md"
    if claude_md.exists():
        try:
            with open(claude_md, 'r') as f:
                content = f.read().lower()
                
            # Common tech stack patterns
            tech_patterns = {
                "frontend": ["react", "vue", "angular", "svelte", "next.js", "nuxt"],
                "backend": ["express", "fastapi", "django", "flask", "rails", "spring"],
                "database": ["postgresql", "mysql", "mongodb", "sqlite", "redis"]
            }
            
            for category, techs in tech_patterns.items():
                for tech in techs:
                    if tech in content:
                        tech_stack["detected"].append(tech)
                        if not tech_stack[category]:
                            tech_stack[category] = tech
                            
        except Exception:
            pass
            
    return tech_stack

def generate_context_summary():
    """
    Generate a comprehensive summary of the project context
    """
    summary = {
        "is_context_forge": is_context_forge_project(),
        "tech_stack": get_project_tech_stack(),
        "stages": analyze_implementation_stage(),
        "prps": get_prp_summary(),
        "has_bug_tracking": (Path.cwd() / "Docs" / "Bug_tracking.md").exists(),
        "has_ui_docs": (Path.cwd() / "Docs" / "UI_UX_doc.md").exists()
    }
    
    return summary

def is_context_forge_project():
    """Check if current directory is a Context Forge project"""
    cwd = Path.cwd()
    
    has_claude_md = (cwd / "CLAUDE.md").exists()
    has_docs = (cwd / "Docs" / "Implementation.md").exists()
    has_prps = (cwd / "PRPs").is_dir()
    has_config = (cwd / ".context-forge" / "config.json").exists()
    
    return has_claude_md and (has_docs or has_prps or has_config)

if __name__ == "__main__":
    # Test utilities
    print("Context Forge Project Analysis")
    print("=" * 50)
    
    if is_context_forge_project():
        print("✓ This is a Context Forge project\n")
        
        summary = generate_context_summary()
        print(json.dumps(summary, indent=2))
    else:
        print("✗ Not a Context Forge project")