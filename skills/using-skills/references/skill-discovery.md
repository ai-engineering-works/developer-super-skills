# Skill Discovery

How Claude finds and loads relevant skills for any given task.

## The Discovery Process

When Claude encounters a task, it follows this process to find applicable skills:

```
┌──────────────────────┐
│  1. Analyze Request  │
│     What is needed?   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  2. Search Skills    │
│     Match triggers/   │
│     keywords          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  3. Read Descriptions│
│     Find matches     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  4. Select Skills   │
│     Choose relevant  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  5. Load Skills     │
│     Invoke Skill tool│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  6. Follow Guidance │
│     Execute per skill │
└──────────────────────┘
```

## How Skills Are Matched

### Description Matching

Claude reads the `description` field from each skill to determine relevance.

**Key factors:**
- **Triggers** - "Use when X, Y, Z" patterns
- **Symptoms** - Error messages, problem descriptions
- **Keywords** - Technology names, tools, concepts
- **Context** - Domain, scope, role

### Example Matches

**User Request:** "Tests are failing randomly"

**Skills that match:**
- `condition-based-waiting` - "Use when tests have race conditions..."
- `debugging-wizard` - "Use when investigating errors..."
- `test-master` - "Use when writing tests..."

**Why:** Descriptions contain relevant keywords (tests, failing, race conditions, errors).

### Keyword Coverage

Skills with rich descriptions are more discoverable:

**✅ Good (rich keywords):**
description: Use when encountering "Hook timed out", ENOTEMPTY, or race conditions in async tests. Invoke for setTimeout, setInterval, Promise handling, or async/await timing issues.

**❌ Bad (poor keywords):**
description: Use for async test issues

## Search Strategy

### Claude searches for:

1. **Direct matches** - Exact phrase matches
2. **Semantic matches** - Similar meaning phrases
3. **Technology matches** - Framework/library names
4. **Symptom matches** - Error messages, problems
5. **Domain matches** - Backend, frontend, devops, etc.

### Search Order

Claude typically searches in this order:

1. **Exact phrase matches** in descriptions
2. **Keyword overlap** in triggers field
3. **Domain matching** (backend → backend skills)
4. **Role matching** (architect → architecture skills)
5. **Output format** (code → code-generating skills)

## Improving Discoverability

### For Skill Authors

**1. Rich Descriptions**
- Include error messages: "ENOTEMPTY", "race condition"
- Include symptoms: "flaky", "hanging", "timeout"
- Include tools: "setTimeout", "pytest", "docker"
- Include synonyms: "cleanup", "teardown", "afterEach"

**2. Accurate Triggers**
- List in \`metadata.triggers\`: comma-separated keywords
- Be specific: "jwt", "oauth", "session" instead of "auth"
- Include variations: "database, db, sql, query"

**3. Appropriate Domain**
- Choose correct \`metadata.domain\`
- Helps domain-specific filtering
- \`language\`, \`backend\`, \`frontend\`, \`infrastructure\`, etc.

**4. Clear Role/Scope**
- \`metadata.role\`: specialist, expert, architect, engineer
- \`metadata.scope\`: implementation, design, review, testing

### For Users

**1. Be Specific**
- ❌ "Help with tests"
- ✅ "Tests are flaky with timing issues"

**2. Mention Technologies**
- ❌ "Fix the database problem"
- ✅ "PostgreSQL query is slow with large joins"

**3. Describe Symptoms**
- ❌ "It doesn't work"
- ✅ "API returns 500 error when user email is null"
