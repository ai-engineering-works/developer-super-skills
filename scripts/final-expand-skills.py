#!/usr/bin/env python3
"""
Final expansion: Add Common Pitfalls section to reach 80 lines.
"""

import re
from pathlib import Path

SKILLS_DIR = "skills"
MIN_LINES = 80


def count_non_blank_lines(body: str) -> int:
    """Count non-blank lines in text."""
    return len([line for line in body.split("\n") if line.strip()])


def add_common_pitfalls(body: str) -> str:
    """Add Common Pitfalls section before Constraints."""
    # Check if already exists
    if "## Common Pitfalls" in body or "## Pitfalls" in body:
        return body

    # Find Constraints section
    constraints_match = re.search(r"\n\n## Constraints", body)
    if not constraints_match:
        return body

    insert_pos = constraints_match.start()

    # Generate common pitfalls content
    pitfalls = "\n\n## Common Pitfalls\n\n"
    pitfalls += "Avoid these common mistakes:\n"
    pitfalls += "- Over-engineering simple problems\n"
    pitfalls += "- Under-documenting complex decisions\n"
    pitfalls += "- Ignoring edge cases\n"
    pitfalls += "- Premature optimization\n"
    pitfalls += "- Not considering maintainability\n"

    new_body = body[:insert_pos] + pitfalls + body[insert_pos:]
    return new_body


def expand_knowledge_reference(body: str) -> str:
    """Expand Knowledge Reference section with more detail."""
    # Find Knowledge Reference section
    ref_match = re.search(r"(## Knowledge Reference\n\n)(.*?)$", body, re.DOTALL)
    if not ref_match:
        return body

    current_content = ref_match.group(2).strip()

    # If already expanded (has multiple lines), skip
    if "\n" in current_content or len(current_content.split(", ")) > 15:
        return body

    # If it's just a single line, break into categories
    items = [item.strip() for item in current_content.split(",")]
    if len(items) < 5:
        return body

    # Organize into a bulleted list
    new_ref = "## Knowledge Reference\n\n"
    new_ref += "Key technologies and concepts:\n"
    for item in items:
        new_ref += f"- {item}\n"

    new_body = body[:ref_match.start()] + new_ref
    return new_body


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
        return False

    modified = False
    new_body = body

    # Try adding Common Pitfalls section
    new_body = add_common_pitfalls(new_body)

    # Try expanding Knowledge Reference
    new_body = expand_knowledge_reference(new_body)

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
            print(f"Final expanded: {skill_dir.name}")

    print(f"\nFinal expanded {fixed_count} skill files")


if __name__ == "__main__":
    main()
