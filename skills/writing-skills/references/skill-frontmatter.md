# Skill Frontmatter

YAML frontmatter format and requirements for Agent Skills.

## Required Fields

### Top-Level (Specification)

```yaml
---
name: skill-name-with-hyphens
description: Use when [triggering conditions] - max 1024 chars
license: MIT
---
```

### Optional Top-Level

```yaml
---
allowed-tools: Tool1 Tool2 Tool3  # Space-delimited tool list
---
```

Use `allowed-tools` ONLY for skills that restrict available tools.

### Metadata Section

All custom fields go under `metadata:`:

```yaml
---
metadata:
  author: https://github.com/username
  version: "1.0.0"
  domain: [domain]
  triggers: keyword1, keyword2, keyword3
  role: [role]
  scope: [scope]
  output-format: [format]
  related-skills: skill-one,skill-two
---
```

## Field Specifications

### name

- **Format:** Letters, numbers, and hyphens only
- **No:** Parentheses, special characters, underscores
- **Case:** lowercase with hyphens (kebab-case)

**✅ Good:**
```yaml
name: condition-based-waiting
name: test-driven-development
name: ml-pipeline
```

**❌ Bad:**
```yaml
name: Condition_Based_Waiting
name: TDD (Test-Driven Development)
name: ML_Pipeline
```

### description

**CRITICAL:** Description must be TRIGGER-ONLY.

**Format:** `Use when [triggering conditions and symptoms]`

- **Max length:** 1024 characters
- **Start with:** "Use when"
- **Content:** WHEN to use, NOT what the skill does
- **No workflow summary:** Don't describe the process

**✅ Good:**
```yaml
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
description: Use when implementing any feature or bugfix, before writing implementation code
```

**❌ Bad:**
```yaml
description: For fixing flaky async tests  # Too short
description: Use for TDD - write test first, watch it fail, write minimal code, refactor  # Summarizes workflow
description: I can help with async tests  # First person
```

### license

Always `MIT` for this project.

```yaml
license: MIT
```

### metadata.author

GitHub profile URL of the skill author.

```yaml
metadata:
  author: https://github.com/selvakumarEsra
```

### metadata.version

Semantic version string (quoted).

```yaml
metadata:
  version: "1.0.0"
```

### metadata.domain

Category from the domain list:

`language` | `backend` | `frontend` | `infrastructure` | `api-architecture` | `quality` | `devops` | `security` | `data-ml` | `platform` | `specialized` | `workflow`

```yaml
metadata:
  domain: language
```

### metadata.triggers

Comma-separated searchable keywords.

```yaml
metadata:
  triggers: test, testing, unit test, integration test, E2E, coverage
```

### metadata.role

`specialist` | `expert` | `architect` | `engineer`

```yaml
metadata:
  role: specialist
```

### metadata.scope

`implementation` | `review` | `design` | `system-design` | `testing` | `analysis` | `infrastructure` | `optimization` | `architecture`

```yaml
metadata:
  scope: implementation
```

### metadata.output-format

`code` | `document` | `report` | `architecture` | `specification` | `schema` | `manifests` | `analysis` | `analysis-and-code`

```yaml
metadata:
  output-format: code
```

### metadata.related-skills

Comma-separated skill directory names.

```yaml
metadata:
  related-skills: test-master, debugging-wizard, fullstack-guardian
```

## Complete Example

```yaml
---
name: condition-based-waiting
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently. Invoke for async operations, polling, waiting for conditions, flaky tests.
license: MIT
metadata:
  author: https://github.com/selvakumarEsra
  version: "1.0.0"
  domain: quality
  triggers: async, await, race condition, flaky test, timing, polling, wait, sleep, timeout
  role: specialist
  scope: implementation
  output-format: code
  related-skills: test-master, debugging-wizard, playwright-expert
---
```

## Validation

The `validate-skills.py` script checks:

- ✅ YAML parses correctly
- ✅ `name` and `description` present
- ✅ `name` uses only letters, numbers, hyphens
- ✅ `description` max 1024 chars, starts with "Use when"
- ✅ `metadata` section exists
- ✅ Required metadata fields present
- ✅ `output-format` uses valid enum value
- ✅ `license` is MIT
- ✅ `related-skills` references existing skills

## Common Errors

### ❌ Missing metadata

```yaml
---
name: my-skill
description: Use when...
---
```

**Fix:** Add metadata section with required fields.

### ❌ Invalid name format

```yaml
name: My_Skill
name: my-skill (v2)
```

**Fix:** Use only lowercase letters, numbers, hyphens.

### ❌ Description summarizes workflow

```yaml
description: Use for testing - write test, run it, fix it
```

**Fix:** Describe triggers only, not process.

### ❌ Wrong output-format

```yaml
metadata:
  output-format: code+analysis
```

**Fix:** Use `analysis-and-code` instead.

### ❌ Invalid domain

```yaml
metadata:
  domain: frontend-development
```

**Fix:** Use `frontend` (from domain list).

### ❌ Related skills don't exist

```yaml
metadata:
  related-skills: non-existent-skill
```

**Fix:** Reference only valid skill directory names.

## Frontmatter in Action

When Claude loads a skill, it:

1. Parses the YAML frontmatter
2. Reads the `description` to decide if the skill applies
3. If applicable, loads the full skill content
4. Follows the skill's guidance

**This is why the description is so critical** - it's the only thing Claude sees before deciding to load the skill.
