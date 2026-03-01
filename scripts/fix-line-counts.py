#!/usr/bin/env python3
"""
Expand SKILL.md files to meet minimum line count requirements.
Focuses on expanding the Constraints section with more detailed MUST DO / MUST NOT DO items.
"""

import re
from pathlib import Path

SKILLS_DIR = "skills"
MIN_LINES = 80


def count_non_blank_lines(body: str) -> int:
    """Count non-blank lines in text."""
    return len([line for line in body.split("\n") if line.strip()])


def expand_constraints_section(content: str) -> str:
    """Expand the Constraints section to be more verbose."""
    # Find the Constraints section
    pattern = r"(## Constraints\n\n)(.*?)(\n\n##|\n\n$)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return content

    current_constraints = match.group(2)

    # If already expanded (has subsections), skip
    if "### MUST DO" in current_constraints or "### MUST NOT DO" in current_constraints:
        return content

    # Extract current MUST DO and MUST NOT items
    must_do_pattern = r"\*\*MUST DO\*\*:\s*(.*?)(?:\n\n\*\*MUST NOT|$)"
    must_not_pattern = r"\*\*MUST NOT.*?:\s*(.*?)(?:\n\n##|\n\n$)"

    must_do_match = re.search(must_do_pattern, current_constraints, re.DOTALL)
    must_not_match = re.search(must_not_pattern, current_constraints, re.DOTALL)

    must_do_items = []
    must_not_items = []

    if must_do_match:
        must_do_text = must_do_match.group(1).strip()
        must_do_items = [item.strip() for item in must_do_text.split(", ") if item.strip()]

    if must_not_match:
        must_not_text = must_not_match.group(2).strip()
        # Remove trailing stuff before MUST NOT items
        must_not_text = re.sub(r"\*\*MUST NOT.*?:\s*", "", must_not_text)
        must_not_items = [item.strip() for item in must_not_text.split(", ") if item.strip()]

    # Build expanded constraints
    expanded = "## Constraints\n\n"

    if must_do_items:
        expanded += "### MUST DO\n"
        for item in must_do_items:
            # Capitalize first letter
            item = item[0].upper() + item[1:] if item else ""
            expanded += f"- {item}\n"
        expanded += "\n"

    if must_not_items:
        expanded += "### MUST NOT DO\n"
        for item in must_not_items:
            # Capitalize first letter
            item = item[0].upper() + item[1:] if item else ""
            # Add common prefixes if not present
            if not item.startswith("Use") and not item.startswith("Skip") and not item.startswith("Ignore"):
                item = "Don't " + item[0].lower() + item[1:] if item else ""
            expanded += f"- {item}\n"

    # Add next section marker
    expanded += "\n##"

    # Replace the old constraints section
    new_content = re.sub(pattern, expanded, content, count=1, flags=re.DOTALL)

    return new_content


def expand_skill_file(file_path: Path) -> bool:
    """Expand a skill file to meet minimum line count."""
    content = file_path.read_text()

    # Split frontmatter and body
    if not content.startswith("---"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[0] + "---" + parts[1] + "---"
    body = parts[2]

    current_count = count_non_blank_lines(body)
    if current_count >= MIN_LINES:
        return False  # Already meets minimum

    # Try expanding constraints
    new_body = expand_constraints_section(body)
    new_count = count_non_blank_lines(new_body)

    if new_count > current_count:
        new_content = frontmatter + new_body
        file_path.write_text(new_content)
        return True

    return False


def main():
    skills_dir = Path(SKILLS_DIR)
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return

    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    fixed_count = 0
    for skill_dir in skill_dirs:
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.exists():
            continue

        if expand_skill_file(skill_path):
            fixed_count += 1
            print(f"Expanded: {skill_dir.name}")

    print(f"\nExpanded {fixed_count} skill files")


if __name__ == "__main__":
    main()
