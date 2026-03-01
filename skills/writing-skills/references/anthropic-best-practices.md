# Anthropic Best Practices

Official skill authoring best practices from Anthropic.

## Overview

This document summarizes Anthropic's official guidance for authoring Agent Skills. It complements the TDD-focused approach in this repository with additional patterns and guidelines.

## Core Principles

### 1. Skills Are Reference Material

Skills are **reference guides** for proven techniques, patterns, or tools. They help future Claude instances find and apply effective approaches.

**Skills are:**
- ✅ Reusable techniques
- ✅ Patterns
- ✅ Tools
- ✅ Reference guides

**Skills are NOT:**
- ❌ Narratives about how you solved a problem once
- ❌ Project-specific instructions (go in CLAUDE.md)
- ❌ One-time solutions

### 2. Discovery is Critical

Future Claude needs to **FIND** your skill before it can use it. Optimize for discoverability.

**Key Elements:**
- Rich description field with triggers and symptoms
- Keyword coverage (errors, tools, symptoms)
- Descriptive naming (verb-first, active)
- Searchable terminology

### 3. Token Efficiency Matters

Getting-started and frequently-referenced skills load into EVERY conversation.

**Targets:**
- Getting-started workflows: <150 words each
- Frequently-loaded skills: <200 words total
- Other skills: <500 words (still be concise)

**Techniques:**
- Move details to tool help (`--help` flag)
- Use cross-references instead of repeating
- Compress examples (20 words not 42)
- Eliminate redundancy

## Skill Structure

### Recommended Format

```markdown
---
name: skill-name
description: Use when [triggering conditions]
---

# Skill Name

## Overview
[What is this? Core principle in 1-2 sentences.]

## When to Use
[Small inline flowchart IF decision non-obvious]

[Bulleted list with symptoms and use cases]

## Core Pattern (for techniques/patterns)
[Before/after code comparison]

## Quick Reference
[Table or bullets for scanning common operations]

## Implementation
[Inline code for simple patterns]
[Link to file for heavy reference or reusable tools]

## Common Mistakes
[What goes wrong + fixes]

## Real-World Impact (optional)
[Concrete results]
```

## Naming Conventions

### Verb-First, Active Voice

**✅ Good:**
- `creating-skills`
- `condition-based-waiting`
- `root-cause-tracing`

**❌ Bad:**
- `skill-creation`
- `async-test-helpers`
- `debugging-techniques`

### Gerunds for Processes

Skills describing ongoing action often work well as gerunds:

- `creating-skills`
- `testing-skills`
- `debugging-with-logs`

## Description Best Practices

### Trigger-Only Format

The description should answer: "Should I read this skill right now?"

**✅ Good:**
```yaml
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

**❌ Bad:**
```yaml
description: Use for fixing race conditions in async tests using polling and conditions
```

### Include Symptoms and Keywords

Add error messages, symptoms, tools, and synonyms:

```yaml
description: Use when encountering "Hook timed out", ENOTEMPTY, or race conditions in async tests
```

## Code Examples

### One Excellent Example

Choose the most relevant language:
- Testing techniques → TypeScript/JavaScript
- System debugging → Shell/Python
- Data processing → Python

**Good Example Qualities:**
- Complete and runnable
- Well-commented explaining WHY
- From real scenario
- Shows pattern clearly
- Ready to adapt (not generic template)

### Don't: Multiple Languages

**❌ Bad:**
```
example.js
example.py
example.go
example.rs
```

**Why:** Mediocre quality, maintenance burden.

## When to Create Separate Files

### Self-Contained Skill (Most Common)

```
defense-in-depth/
  SKILL.md    # Everything inline
```

Use when: All content fits, no heavy reference needed.

### Skill with Reusable Tool

```
condition-based-waiting/
  SKILL.md    # Overview + patterns
  example.ts  # Working helpers to adapt
```

Use when: Tool is reusable code, not just narrative.

### Skill with Heavy Reference

```
pptx/
  SKILL.md       # Overview + workflows
  pptxgenjs.md   # 600 lines API reference
  ooxml.md       # 500 lines XML structure
  scripts/       # Executable tools
```

Use when: Reference material too large for inline.

## Cross-References

### Use Skill Names, Not Paths

**✅ Good:**
```markdown
**REQUIRED SUB-SKILL:** Use test-driven-development
**REQUIRED BACKGROUND:** You MUST understand systematic-debugging
```

**❌ Bad:**
```markdown
See skills/testing/test-driven-development/SKILL.md
@skills/testing/test-driven-development/SKILL.md
```

**Why:** `@` syntax force-loads files immediately, consuming 200k+ context.

## Testing Your Skills

Anthropic emphasizes practical testing:

1. **Write the skill**
2. **Test with real scenarios**
3. **Observe how agents use it**
4. **Iterate based on behavior**
5. **Document edge cases**

This aligns with the TDD approach: watch agents fail without the skill, write skill to address those failures, then verify compliance.

## Additional Resources

For the latest official guidance from Anthropic, see:
- Agent Skills specification: https://agentskills.io/specification
- Official examples and patterns
- Community contributions

## Integration with TDD Approach

The Anthropic best practices complement the TDD approach:

| Aspect | Anthropic Guidance | TDD Approach |
|--------|-------------------|---------------|
| **Testing** | Test with real scenarios | Pressure scenarios (baseline) |
| **Iteration** | Observe and iterate | RED-GREEN-REFACTOR cycle |
| **Quality** | Ensure skill works | Verify agent compliance |
| **Discovery** | Optimize description (CSO) | Keywords in description |
| **Structure** | Overview + references | Progressive disclosure |

Both approaches emphasize:
- Practical testing over theory
- Iteration based on real behavior
- Optimizing for Claude's usage patterns
- Quality over quantity

## Key Takeaways

1. **Skills are reference material** - Not narratives or one-time solutions
2. **Discovery is critical** - Rich descriptions, keyword coverage, clear naming
3. **Token efficiency** - Move details elsewhere, cross-reference, compress examples
4. **One excellent example** - Not multi-language mediocrity
5. **Test your skills** - Observe real usage, iterate based on behavior
6. **Use official structure** - Overview, When to Use, Core Pattern, Quick Reference
7. **Cross-reference smartly** - Skill names only, no @ paths
