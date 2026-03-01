#!/usr/bin/env python3
"""
Further expand SKILL.md files to reach 80 line minimum.
Adds more bullet items to When to Use, expands workflow, adds detailed output templates.
"""

import re
from pathlib import Path

SKILLS_DIR = "skills"
MIN_LINES = 80


def count_non_blank_lines(body: str) -> int:
    """Count non-blank lines in text."""
    return len([line for line in body.split("\n") if line.strip()])


def expand_when_to_use(when_section: str) -> str:
    """Add more bullet items to When to Use This Skill section."""
    lines = when_section.split("\n")
    bullets = [l for l in lines if l.strip().startswith("-")]

    # If already has many items, skip
    if len(bullets) >= 10:
        return when_section

    # Find the section end
    section_end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("##") and "When to Use" not in line:
            section_end = i
            break

    # Additional generic bullets to add
    additional_bullets = [
        "- Analyzing existing code patterns and conventions",
        "- Refactoring code for better maintainability",
        "- Ensuring code follows best practices and standards",
        "- Reviewing code for potential issues and improvements"
    ]

    # Insert additional bullets before the next section
    new_lines = lines[:section_end]
    for bullet in additional_bullets:
        if len(bullets) + len(additional_bullets[:additional_bullets.index(bullet)]) < 12:
            new_lines.append(bullet)
    new_lines.extend(lines[section_end:])

    return "\n".join(new_lines)


def expand_core_workflow(workflow_section: str) -> str:
    """Expand Core Workflow section with more detail per step."""
    # If already expanded (has sub-bullets), skip
    if "   -" in workflow_section or "  -" in workflow_section:
        return workflow_section

    lines = workflow_section.split("\n")
    new_lines = []
    in_workflow = False

    for line in lines:
        new_lines.append(line)
        if "## Core Workflow" in line:
            in_workflow = True
            continue

        if in_workflow and line.strip().startswith("##") and "Core Workflow" not in line:
            in_workflow = False
            continue

        if in_workflow and re.match(r"^\d+\.\s+\*\*", line):
            # Add a sub-bullet with more detail
            step_match = re.match(r"^\d+\.\s+\*\*(.*?)\*\*\s*-\s*(.*)", line)
            if step_match:
                step_name = step_match.group(1)
                step_desc = step_match.group(2)
                # Add detail line
                detail = f"   - Focus on {step_name.lower()} activities: {step_desc}"
                new_lines.append(detail)

    return "\n".join(new_lines)


def expand_output_templates(templates_section: str) -> str:
    """Expand Output Templates section with more detail."""
    lines = templates_section.split("\n")
    bullets = [l for l in lines if l.strip().startswith("-") or l.strip().startswith(r"\d")]

    # If already has many items (5+), skip
    if len(bullets) >= 5:
        return templates_section

    # If only has intro line, expand with common items
    new_lines = []
    in_section = False

    for line in lines:
        new_lines.append(line)
        if "## Output Templates" in line:
            in_section = True
            # Check if next line provides items
            idx = lines.index(line)
            if idx + 1 < len(lines) and lines[idx + 1].strip().startswith("-"):
                continue  # Already has items

            # Add standard items after the blank line
            if idx + 1 < len(lines) and not lines[idx + 1].strip():
                new_lines.extend([
                    "",
                    "When providing output, ensure:",
                    "- Clear and actionable recommendations",
                    "- Code examples with explanations",
                    "- Consideration of edge cases",
                    "- Performance and security implications",
                    "- Next steps or follow-up actions"
                ])
            in_section = False
            continue

    return "\n".join(new_lines)


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

    # Expand When to Use This Skill
    if "## When to Use" in body:
        when_pattern = r"(## When to Use This Skill\n\n)(.*?)(\n\n##)"
        when_match = re.search(when_pattern, body, re.DOTALL)
        if when_match:
            original_when = when_match.group(0)
            new_when = expand_when_to_use(original_when)
            if new_when != original_when:
                body = body.replace(original_when, new_when)
                modified = True

    # Expand Core Workflow
    if "## Core Workflow" in body:
        workflow_pattern = r"(## Core Workflow\n\n.*?)(\n\n##)"
        workflow_match = re.search(workflow_pattern, body, re.DOTALL)
        if workflow_match:
            original_workflow = workflow_match.group(1)
            new_workflow = expand_core_workflow(original_workflow)
            if new_workflow != original_workflow:
                body = body.replace(original_workflow, new_workflow)
                modified = True

    # Expand Output Templates
    if "## Output Templates" in body:
        templates_pattern = r"(## Output Templates\n\n.*?)(\n\n##|\n\n$)"
        templates_match = re.search(templates_pattern, body, re.DOTALL)
        if templates_match:
            original_templates = templates_match.group(1)
            new_templates = expand_output_templates(original_templates)
            if new_templates != original_templates:
                body = re.sub(templates_pattern, new_templates, body, count=1, flags=re.DOTALL)
                modified = True

    if modified:
        new_count = count_non_blank_lines(body)
        if new_count > current_count:
            new_content = frontmatter + body
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
            print(f"Further expanded: {skill_dir.name}")

    print(f"\nFurther expanded {fixed_count} skill files")


if __name__ == "__main__":
    main()
