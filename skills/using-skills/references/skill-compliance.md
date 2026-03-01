# Skill Compliance

Ensuring agents follow skill protocols correctly and consistently.

## What is Skill Compliance?

Skill compliance means agents:
1. **Find applicable skills** before responding
2. **Load skills** using the Skill tool
3. **Follow skill guidance** exactly
4. **Maintain compliance** throughout the task

## The Compliance Protocol

### Before ANY Response

\`\`\`
┌─────────────────────────────────────────┐
│  1. CHECK FOR SKILLS                    │
│     Is there a skill that applies?      │
└──────────────┬──────────────────────────┘
               │
         ┌─────┴─────┐
         │           │
        Yes          No
         │           │
         ▼           ▼
┌──────────────┐  ┌──────────────┐
│  2. INVOKE    │  │  3. RESPOND  │
│     SKILL     │  │     NORMALLY  │
└──────────────┘  └──────────────┘
\`\`\`

### The 1% Rule

> If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

**No exceptions.** This is not negotiable.

## Compliance Checklist

### Before Starting Work

- [ ] Searched for relevant skills?
- [ ] Read descriptions of potential skills?
- [ ] Loaded all applicable skills?
- [ ] Understood skill requirements?

### During Work

- [ ] Following skill workflow?
- [ ] Obeying skill constraints?
- [ ] Producing required outputs?
- [ ] Checking skill references?

### After Completion

- [ ] Verified skill requirements met?
- [ ] Documented any deviations?
- [ ] Updated related skills if needed?

## Common Violations

### ❌ Skipping Discovery

**Violation:** Not searching for skills before responding

**Example:**
\`\`\`
User: "Help me write tests"
Agent: [Immediately writes tests without loading test-master]
\`\`\`

**Correct:**
\`\`\`
User: "Help me write tests"
Agent: [Searches for skills, loads test-master, follows its workflow]
\`\`\`

### ❌ Reading Instead of Loading

**Violation:** Using Read tool on skill files

**Example:**
\`\`\`
@skills/test-master/SKILL.md
\`\`\`

**Why:** Force-loads 200k+ tokens, bypasses discovery

**Correct:**
\`\`\`
Skill(skill_name="test-master")
\`\`\`

### ❌ Partial Compliance

**Violation:** Following some parts but not others

**Example:**
\`\`\`
Skill says: "Write test first, then code"
Agent: Writes test, but also writes code in same step (partial compliance)
\`\`\`

**Correct:**
\`\`\`
Step 1: Write test only
Step 2: Run test (verify fails)
Step 3: Write code
\`\`\`

### ❌ "Too Simple" Rationalization

**Violation:** Not loading skill because task seems simple

**Example:**
\`\`\`
Agent: "This is just a simple validation, doesn't need test-first"
\`\`\`

**Reality:** Simple code breaks too. 1% rule applies.

## Enforcing Compliance

### For Skill Authors

**1. Clear Instructions**
\`\`\`markdown
## Requirements

**REQUIRED:** This skill MUST be used for [X].

**Non-negotiable:** [Y] must happen before [Z].
\`\`\`

**2. Hard Gates**
\`\`\`markdown
<HARD-GATE>
Do NOT proceed to [next phase] until [condition] is verified.
</HARD-GATE>
\`\`\`

**3. Red Flag Lists**
\`\`\`markdown
## Red Flags - STOP and Start Over

- [Violation 1]
- [Violation 2]

**All of these mean:** [Consequence]
\`\`\`

**4. Rationalization Tables**
\`\`\`markdown
| Excuse | Reality |
|--------|---------|
| "Too simple" | Simple code breaks |
| "Not enough time" | Untested code takes longer |
\`\`\`

### For Users

**1. Explicit Requests**
\`\`\`
> Use test-master for this testing task
\`\`\`

**2. Verification**
\`\`\`
> Did you load the test-master skill? Please follow its workflow.
\`\`\`

**3. Correction**
\`\`\`
> The skill says to write tests first. Please start over with TDD.
\`\`\`

## Monitoring Compliance

### Signs of Non-Compliance

- **Skipping steps** - "I'll combine steps 2 and 3"
- **Premature optimization** - "I'll add this now while I'm thinking of it"
- **"Just this once"** - "For this simple case, I'll skip it"
- **Workflow modification** - "This workflow doesn't quite fit our situation"

### Correcting Non-Compliance

When you detect non-compliance:

1. **Stop immediately** - "Please stop. The skill requires X."
2. **Cite requirement** - "The skill says [exact quote]"
3. **Request restart** - "Please start over from step N"
4. **Verify** - Check that compliance is restored

## The Compliance Mindset

### Agents Should Think

- "Is there ANY skill that might apply?"
- "What does the skill require me to do?"
- "Am I following the EXACT workflow?"
- "What constraints must I obey?"

### Agents Should NOT Think

- "This is too simple for a skill"
- "I'll adapt the workflow slightly"
- "Just this once won't matter"
- "The skill doesn't quite fit, so I'll modify it"

## Summary

Skill compliance is mandatory:

1. **ALWAYS search** for applicable skills before responding
2. **LOAD skills** using the Skill tool (not Read)
3. **FOLLOW skill guidance** exactly
4. **MAINTAIN compliance** throughout the task
5. **VERIFY** requirements are met

The 1% rule means: If there's even a 1% chance a skill applies, you MUST use it.

This is not optional. This is not negotiable.
