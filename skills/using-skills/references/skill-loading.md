# Skill Loading

How Claude loads and executes skills using the Skill tool.

## The Skill Tool

Claude uses the \`Skill\` tool to load skill content into context.

## Loading Process

### 1. Skill Discovery

Claude searches for relevant skills (see \`skill-discovery.md\`)

### 2. Skill Invocation

When a skill is found, Claude invokes it:

\`\`\`python
Skill(skill_name="skill-name")
\`\`\`

### 3. Content Injection

The skill's content is loaded into Claude's context:
- YAML frontmatter is parsed
- Markdown body is available for reference
- Claude follows the skill's guidance

### 4. Execution

Claude executes according to the skill's instructions.

## What Gets Loaded

### Frontmatter (Parsed)

\`\`\`yaml
name: skill-name
description: Use when [triggers]
license: MIT
metadata:
  author: https://github.com/...
  version: "1.0.0"
  domain: [domain]
  triggers: [keywords]
  role: [role]
  scope: [scope]
  output-format: [format]
  related-skills: [skills]
\`\`\`

### Body (Raw Markdown)

The full markdown body of the skill is available for Claude to reference during execution.

## Loading Behavior

### Single Skill

\`\`\`python
Skill(skill_name="condition-based-waiting")
\`\`\`

Claude loads one skill and follows its guidance.

### Multiple Skills

\`\`\`python
Skill(skill_name="test-master")
Skill(skill_name="debugging-wizard")
Skill(skill_name="condition-based-waiting")
\`\`\`

Claude loads multiple skills - they compose/stack their guidance.

### Skill Selection

Claude may load multiple skills when:
- Skills have non-overlapping domains
- Skills complement each other
- Task requires multiple perspectives

## Reading Skills

### ✅ Correct: Use Skill Tool

\`\`\`python
# Claude does this internally
Skill(skill_name="test-master")
# Then follows the skill content
\`\`\`

### ❌ Wrong: Read Tool

\`\`\`markdown
<!-- DO NOT do this -->
@skills/test-master/SKILL.md
<!-- Or -->
Read skills/test-master/SKILL.md
\`\`\`

**Why Wrong:**
- \`@\` syntax force-loads 200k+ tokens
- Read doesn't parse frontmatter
- Bypasses skill discovery
- Wastes context

## When Skills Load

### Automatic Loading

Skills load automatically when:

1. **Description matches** - Trigger conditions met
2. **User request** - User explicitly asks for skill
3. **Related skills** - Skill references another skill
4. **Workflow commands** - Command invokes skill

### Explicit Loading

Users can explicitly request skills:

\`\`\`
> Use the test-master skill for this
\`\`\`

### Conditional Loading

Some skills are conditional:

\`\`\`yaml
description: Use when implementing any feature, BEFORE writing code
\`\`\`

Only loads if the condition is met.

## Context After Loading

### What Claude Knows

After loading a skill, Claude has:

1. **Skill metadata** - Domain, role, scope, triggers
2. **Skill content** - Full markdown body
3. **Constraints** - MUST DO / MUST NOT DO requirements
4. **Workflow** - Core workflow steps
5. **Outputs** - What to produce

### How Claude Uses It

Claude references the skill content while:
- Planning approach
- Making decisions
- Generating code
- Handling edge cases
- Formatting output

## Loading Best Practices

### For Users

**1. Let Claude discover skills**
- ❌ "Load test-master skill"
- ✅ "I need to write tests for this feature"

**2. Be explicit when needed**
- ❌ "Help with this"
- ✅ "Use test-master for this testing task"

**3. Trust the loading system**
- Claude will find relevant skills
- Multiple skills compose when needed
- Skills reference each other automatically

### For Skill Authors

**1. Enable discoverability**
- Rich descriptions with triggers
- Accurate domain classification
- Related skills references

**2. Make instructions clear**
- Unambiguous constraints
- Step-by-step workflows
- Examples for common cases

**3. Reference, don't duplicate**
- Cross-reference related skills
- Don't repeat other skills' content
- Use related-skills field
