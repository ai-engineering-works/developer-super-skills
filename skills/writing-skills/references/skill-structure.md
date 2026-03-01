# Skill Structure

Standard SKILL.md document organization and format.

## Document Structure

Every SKILL.md follows this structure:

```markdown
---
[YAML frontmatter]
---

# Skill Name

[Optional brief tagline]

## Role Definition

[2-3 sentences defining expertise level and approach]

## When to Use This Skill

[Bulleted list of triggers and use cases]

## Core Workflow

[5 numbered steps]

## Reference Guide

[Table linking to reference files]

## Constraints

### MUST DO
[Bulleted requirements]

### MUST NOT DO
[Bulleted prohibitions]

## Output Templates

[What outputs to provide]

## Knowledge Reference

[Keywords and technologies]
```

## Section Guidelines

### Role Definition (2-5 lines)

Defines who you are and your expertise level.

**✅ Good:**
```markdown
You are a senior [domain] specialist with [N]+ years of experience. You approach problems with [specific philosophy]. You ensure [key principles].
```

**Example:**
```markdown
You are a senior test engineer with 12+ years of testing experience. You think in three testing modes: functional correctness, performance, and security. You ensure features work correctly, perform well, and are secure.
```

### When to Use This Skill (5-15 bullets)

Bulleted list of triggers and symptoms.

**Format:**
- Start with verb/action
- Be specific about symptoms
- Include edge cases

**✅ Good:**
```markdown
- Writing unit, integration, or E2E tests
- Creating test strategies and plans
- Analyzing test coverage and quality metrics
- Performance testing and benchmarking
- Security testing for vulnerabilities
```

### Core Workflow (5 steps)

Exactly 5 numbered steps, each with:
- **Bold step name** - Short, action-oriented
- Brief description - What this step accomplishes

**Format:**
```markdown
1. **Step name** - Brief description
2. **Step name** - Brief description
3. **Step name** - Brief description
4. **Step name** - Brief description
5. **Step name** - Brief description
```

**✅ Good:**
```markdown
1. **Define scope** - Identify what to test and testing types needed
2. **Create strategy** - Plan test approach using all three perspectives
3. **Write tests** - Implement tests with proper assertions
4. **Execute** - Run tests and collect results
5. **Report** - Document findings with actionable recommendations
```

### Reference Guide (Table)

Table linking detailed guidance to specific situations.

**Format:**
```markdown
| Topic | Reference | Load When |
|-------|-----------|-----------|
| [Topic] | `[path/to/reference.md]` | [When to load] |
```

**✅ Good:**
```markdown
| Topic | Reference | Load When |
|-------|-----------|-----------|
| Unit Testing | `references/unit-testing.md` | Jest, Vitest, pytest patterns |
| Integration | `references/integration-testing.md` | API testing, Supertest |
| E2E | `references/e2e-testing.md` | E2E strategy, user flows |
```

### Constraints (MUST DO / MUST NOT DO)

Two subsections with bulleted lists.

**Format:**
```markdown
### MUST DO
- [Requirement 1]
- [Requirement 2]

### MUST NOT DO
- [Prohibition 1]
- [Prohibition 2]
```

**✅ Good:**
```markdown
### MUST DO
- Test both happy paths and error cases
- Mock external dependencies (APIs, databases, services)
- Use meaningful test descriptions
- Assert specific outcomes
- Test edge cases and boundary conditions

### MUST NOT DO
- Skip error testing and edge cases
- Use production data in tests
- Create order-dependent tests
- Ignore or silence flaky tests
- Test implementation details instead of behavior
```

### Output Templates

Describe what outputs the skill produces.

**Format:**
```markdown
When [action], provide:
1. [Output 1]
2. [Output 2]
3. [Output 3]
```

**✅ Good:**
```markdown
When creating test plans, provide:
1. Test scope and approach
2. Test cases with expected outcomes
3. Coverage analysis
4. Findings with severity (Critical/High/Medium/Low)
5. Specific fix recommendations
```

### Knowledge Reference

Comma-separated list of technologies, concepts, and tools.

**Format:**
```markdown
[Keyword 1], [Keyword 2], [Keyword 3], ...
```

**✅ Good:**
```markdown
Jest, Vitest, pytest, React Testing Library, Supertest, Playwright, Cypress, k6, Artillery, OWASP testing, code coverage, mocking, fixtures, test automation frameworks
```

## Line Count Guidelines

**Target:** 80-100 non-blank lines (excluding frontmatter)

**Breakdown:**
- Role Definition: 2-5 lines
- When to Use: 5-15 lines
- Core Workflow: 5-7 lines
- Reference Guide: 10-15 lines (table)
- Constraints: 10-20 lines
- Output Templates: 5-10 lines
- Knowledge Reference: 3-10 lines

## Progressive Disclosure

Skills follow the progressive disclosure architecture:

**Tier 1 - SKILL.md (80-100 lines)**
- Role definition and expertise level
- When-to-use guidance (triggers)
- Core workflow (5 steps)
- Constraints (MUST DO / MUST NOT DO)
- Routing table to references

**Tier 2 - Reference Files (100-600 lines each)**
- Deep technical content
- Complete code examples
- Edge cases and anti-patterns
- Loaded only when context requires

**Goal:** 50% token reduction through selective loading.

## Common Section Variations

### Routing Table (Optional)

Some skills include a routing table in Reference Guide:

```markdown
### Routing Table

| When you need... | Load this reference |
|-----------------|---------------------|
| Quick refresher | See Reference Guide table above |
| Deep technical details | Any reference from the table |
| Pattern examples | Reference specific to your topic |
```

### Common Pitfalls (Optional)

Some skills include a common pitfalls section:

```markdown
## Common Pitfalls

- **Pitfall 1** - Why it's bad, how to avoid
- **Pitfall 2** - Why it's bad, how to avoid
```

### Best Practices (Optional)

Some skills include a best practices section:

```markdown
## Best Practices

- **Practice 1** - When and how to apply
- **Practice 2** - When and how to apply
```

## Format Tips

### Use Markdown Headers

- `#` for skill name (only one)
- `##` for main sections
- `###` for subsections

### Use Lists for Readability

- Bullet points for items
- Numbered lists for sequences
- Tables for structured data

### Use Code Blocks

```
For code examples
```

### Use Bold for Emphasis

`**Bold**` key terms, step names, important concepts

### Avoid

- Over-sectioning (too many `###` headers)
- Nested lists beyond 2 levels
- Duplicate information
- Verbose examples (keep in references)
