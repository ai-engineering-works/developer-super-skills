#!/usr/bin/env python3
"""
Automatically fix bidirectional related-skills references.
Adds missing reverse references to make skill relationships symmetric.
"""

import re
from pathlib import Path
from typing import Dict, Set

SKILLS_DIR = "skills"


def parse_frontmatter(file_path: Path) -> dict:
    """Parse YAML frontmatter from a file."""
    try:
        import yaml
        content = file_path.read_text()
        if not content.startswith("---"):
            return {}
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
        return yaml.safe_load(parts[1]) or {}
    except ImportError:
        # Fallback to simple parser
        return simple_parse(file_path)


def simple_parse(file_path: Path) -> dict:
    """Simple YAML parser for basic frontmatter."""
    content = file_path.read_text()
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    result = {}
    current_key = None
    in_metadata = False

    for line in parts[1].strip().split("\n"):
        if line.startswith("metadata:"):
            in_metadata = True
            result["metadata"] = {}
            continue
        if in_metadata and line.startswith("  ") and ":" in line:
            nested_parts = line.strip().split(":", 1)
            nested_key = nested_parts[0].strip()
            nested_value = nested_parts[1].strip() if len(nested_parts) > 1 else ""
            if nested_value.startswith('"') and nested_value.endswith('"'):
                nested_value = nested_value[1:-1]
            result["metadata"][nested_key] = nested_value

    return result


def get_related_skills(skill_path: Path) -> Set[str]:
    """Extract related-skills from a skill's frontmatter."""
    frontmatter = parse_frontmatter(skill_path / "SKILL.md")
    metadata = frontmatter.get("metadata", {})
    if not isinstance(metadata, dict):
        return set()

    related = metadata.get("related-skills", "")
    if isinstance(related, str) and related.strip():
        return {r.strip() for r in related.split(",") if r.strip()}
    return set()


def add_related_skill(file_path: Path, new_skill: str) -> bool:
    """Add a skill to the related-skills list."""
    content = file_path.read_text()

    # Find the related-skills line
    pattern = r"(related-skills:\s*)([^\n]*)"
    match = re.search(pattern, content)

    if not match:
        return False

    existing_skills = match.group(2).strip()
    if not existing_skills:
        # Empty related-skills, just add the new one
        new_line = f"related-skills: {new_skill}"
        content = re.sub(pattern, new_line, content, count=1)
    else:
        # Check if already present
        skills_list = [s.strip() for s in existing_skills.split(",")]
        if new_skill in skills_list:
            return False  # Already exists

        # Add to the end
        new_line = f"related-skills: {existing_skills},{new_skill}"
        content = re.sub(pattern, new_line, content, count=1)

    file_path.write_text(content)
    return True


def main():
    skills_dir = Path(SKILLS_DIR)
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return

    # Build the reference graph
    graph: Dict[str, Set[str]] = {}
    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        graph[skill_name] = get_related_skills(skill_dir)

    # Find asymmetric references
    asymmetric = []
    for skill, refs in sorted(graph.items()):
        for ref in sorted(refs):
            if ref not in graph:
                continue  # Non-existent skill
            if skill not in graph[ref]:
                asymmetric.append((ref, skill))  # ref needs to add skill

    print(f"Found {len(asymmetric)} asymmetric references")
    print()

    # Group by target skill for efficient fixing
    fixes: Dict[str, Set[str]] = {}
    for target_skill, missing_ref in asymmetric:
        if target_skill not in fixes:
            fixes[target_skill] = set()
        fixes[target_skill].add(missing_ref)

    # Apply fixes
    for skill_name, missing_refs in sorted(fixes.items()):
        skill_path = skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            continue

        print(f"Fixing {skill_name}: adding {', '.join(sorted(missing_refs))}")

        for ref in sorted(missing_refs):
            add_related_skill(skill_path, ref)

    print()
    print(f"Fixed {len(asymmetric)} asymmetric references across {len(fixes)} skills")


if __name__ == "__main__":
    main()
