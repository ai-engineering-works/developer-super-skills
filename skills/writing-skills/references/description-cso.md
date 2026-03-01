# Description CSO (Claude Search Optimization)

Making skills discoverable through the description field.

## What is CSO?

Claude Search Optimization (CSO) is the practice of writing skill descriptions that maximize the likelihood of Claude finding and loading the right skill.

## The Critical Principle

**Description = When to Use, NOT What the Skill Does**

The description should ONLY describe triggering conditions. Do NOT summarize the skill's process or workflow in the description.

## Why This Matters

Testing revealed that when a description summarizes the skill's workflow, Claude may follow the description instead of reading the full skill content. The skill body becomes documentation Claude skips.

### Real Example

**❌ BAD Description:**
```yaml
description: Use when executing plans - dispatches subagent per task with code review between tasks
```

Result: Claude did ONE code review after all tasks, even though the skill clearly showed TWO reviews (spec compliance then code quality).

**✅ GOOD Description:**
```yaml
description: Use when executing implementation plans with independent tasks in the current session
```

Result: Claude read the full skill and followed the two-stage review process correctly.

## The Trap

Descriptions that summarize workflow create a shortcut Claude will take:

```
┌─────────────────┐
│  Description    │ ← Claude reads this
│  (with summary) │
└────────┬────────┘
         │
         ├──────────────────────┐
         ↓                      ↓
   Follow summary         Skip skill body
```

When description doesn't summarize:

```
┌─────────────────┐
│  Description    │ ← Claude reads this
│  (triggers only) │
└────────┬────────┘
         │
         ↓
   Must read skill body to know what to do
```

## Format Rules

### MUST Start With "Use when"

```yaml
# ❌ BAD: Doesn't start with "Use when"
description: For handling async test flakiness

# ❌ BAD: Starts with "When"
description: When tests are flaky...

# ✅ GOOD: Starts with "Use when"
description: Use when tests have race conditions...
```

### Describe Triggers and Symptoms

Focus on:
- **Symptoms:** What the user/agent observes
- **Situations:** When this applies
- **Triggers:** Specific events or conditions

**✅ Good:**
```yaml
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

### Technology-Agnostic (Unless Specific)

Default to technology-agnostic triggers:

**❌ BAD:** Too specific
```yaml
description: Use when setTimeout or sleep calls cause test failures
```

**✅ GOOD:** Technology-agnostic
```yaml
description: Use when tests have timing issues or inconsistent results
```

**✅ GOOD:** Technology-specific (when skill IS specific)
```yaml
description: Use when using React Router and handling authentication redirects
```

### Third Person Voice

**❌ BAD:**
```yaml
description: I'll help you with...
description: You can use this for...
```

**✅ GOOD:**
```yaml
description: Use when...
description: Invoke for...
```

## Length Guidelines

- **Maximum:** 1024 characters
- **Target:** 200-500 characters for most skills
- **Getting-started workflows:** Under 150 characters (load frequently)

**Getting-started example:**
```yaml
description: Use when starting any conversation - establishes how to find and use skills
```

## Keyword Coverage

Include words Claude would search for:

### Error Messages
```yaml
description: Use when encountering "Hook timed out", "ENOTEMPTY", or race conditions
```

### Symptoms
```yaml
description: Use when tests are flaky, hanging, zombie, or have pollution issues
```

### Synonyms
```yaml
description: Use for timeout, hang, freeze, cleanup, or teardown issues
```

### Tools and Libraries
```yaml
description: Use when working with setTimeout, setInterval, Promises, or async/await
```

## Examples by Skill Type

### Discipline Skills (Rules)

```yaml
# TDD
description: Use when implementing any feature or bugfix, before writing implementation code

# Verification
description: Use when completing implementation tasks, before marking as done

# Design-first
description: Use when starting any implementation work, before writing code
```

### Technique Skills (How-To)

```yaml
# Condition-based waiting
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently

# Root-cause tracing
description: Use when investigating errors, analyzing stack traces, or finding origin of bugs

# Defensive programming
description: Use when writing code that handles external inputs, user data, or untrusted sources
```

### Pattern Skills (Mental Models)

```yaml
# Information hiding
description: Use when designing APIs, creating modules, or organizing code structure

# Flatten-with-flags
description: Use when dealing with nested conditionals, complex branching, or control flow clarity
```

### Reference Skills (Documentation)

```yaml
# Office docs
description: Use when automating Word, Excel, or PowerPoint with Python or JavaScript

# React Router
description: Use when using React Router for navigation, routing, or authentication in React apps
```

## Anti-Patterns

### ❌ Process Description

```yaml
description: Use for TDD - write test first, watch it fail, write code, refactor
```

**Why:** Claude follows the summary instead of reading the skill.

### ❌ Outcome Description

```yaml
description: Use to ensure tests pass and code is reliable
```

**Why:** Doesn't tell Claude WHEN to use it.

### ❌ Vague Triggers

```yaml
description: Use for async testing
```

**Why:** Doesn't describe symptoms or situations.

### ❌ First Person

```yaml
description: I help with test-driven development
```

**Why:** Injected into system prompt, should be third-person.

## Validation Checklist

For each description, verify:

- [ ] Starts with "Use when" or "Invoke for"
- [ ] Describes triggering conditions/symptoms
- [ ] Does NOT summarize workflow or process
- [ ] Technology-agnostic (unless skill is specific)
- [ ] Third-person voice
- [ ] Under 1024 characters
- [ ] Includes searchable keywords (errors, symptoms, tools)
- [ ] No "I", "you", "we" pronouns

## Testing Your Description

Test your description by asking:

1. **Can Claude decide to load this skill from the description alone?**
2. **Does the description force Claude to read the skill body to know what to do?**
3. **Will the description match when someone searches for the problem?**

If the answer is "yes" to all three, your description is optimized.
