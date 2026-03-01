# TDD for Skills

Applying Test-Driven Development principles to Agent Skills authoring.

## The Core Principle

**Writing skills IS TDD for process documentation.**

The same RED-GREEN-REFACTOR cycle that applies to code applies to skills:

| Code TDD | Skill TDD |
|----------|-----------|
| Write failing test | Run pressure scenario without skill |
| Test fails (RED) | Agent violates rule (baseline) |
| Write minimal code | Write minimal skill addressing violations |
| Test passes (GREEN) | Agent complies with skill |
| Refactor code | Close loopholes, add counters |

## Why TDD for Skills?

### Without Testing (Bad)

1. Write skill based on assumptions
2. Deploy skill
3. Agent doesn't follow it
4. Wonder why
5. Try to fix blind
6. Repeat

### With TDD (Good)

1. Watch agent fail without skill (learn what they do)
2. Write skill addressing specific failures
3. Watch agent succeed with skill
4. Find new loopholes
5. Add explicit counters
6. Verify compliance

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to:
- ✅ New skills
- ✅ Edits to existing skills
- ✅ Documentation updates
- ✅ "Small" additions
- ✅ "Obvious" fixes

**No exceptions.**

## RED Phase: Write Failing Test

### What is a "Test" for Skills?

A test is a **pressure scenario** - a situation where an agent might violate the rule you're trying to enforce.

### Running the Baseline

1. **Create pressure scenario** - Design a situation that would tempt violation
2. **Run WITHOUT skill** - Let agent try to accomplish task
3. **Document behavior** - What did they do? What did they say?
4. **Capture rationalizations** - Verbatim excuses for violations

### Example: TDD Skill

**Pressure Scenario:**
> "I need to add a simple validation function. Time is short."

**Baseline (without skill):**
Agent writes code first, then writes tests.

**Rationalization captured:**
> "This is too simple to need TDD"
> "Tests after will achieve the same goal"
> "It's about spirit, not ritual"

### Types of Pressure Scenarios

**Time Pressure:**
> "We need this done in 10 minutes"

**Authority Pressure:**
> "The lead developer said to skip tests for this"

**Exhaustion:**
> "This is the 50th test case, can't we just add the code?"

**Sunk Cost:**
> "I already wrote 100 lines of code, writing tests now seems wasteful"

**Peer Pressure:**
> "Everyone else skips tests for this type of function"

### Documenting Failures

Create a table:

| Pressure | Agent Behavior | Rationalization |
|----------|---------------|-----------------|
| Time (10 min) | Wrote code first | "Too simple for TDD" |
| Authority | Skipped tests | "Lead said it's OK" |
| Sunk cost | No tests | "Already wrote code" |

## GREEN Phase: Write Minimal Skill

### Address Specific Failures

Write skill that ONLY addresses the failures you observed:

**❌ Bad (too generic):**
> "Always follow TDD. Write tests first."

**✅ Good (addresses specific rationalizations):**
> Write code before test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

### Why Minimal Works

By addressing the exact rationalizations from baseline testing, you:
- Avoid over-engineering the skill
- Keep it concise
- Target real problems, not hypothetical ones

## REFACTOR Phase: Close Loopholes

### Agents Find Loopholes

After writing skill, test again. Agents will find new ways around it.

**Example:**
Original skill: "Write code before test? Delete it."

**New rationalization:** "I'll write the test, but keep the code open as 'reference'."

**Add explicit counter:**
> Don't keep untested code as "reference". That's a violation.

### The Refactor Cycle

1. Test with skill
2. Find new rationalization
3. Add explicit counter to skill
4. Test again
5. Repeat until bulletproof

### Rationalization Table

Maintain a table throughout development:

| Rationalization | Counter Added | Iteration |
|----------------|---------------|-----------|
| "Too simple for TDD" | Delete means delete, no exceptions | 1 |
| "Tests after achieve same goal" | Tests-after = "what does this do?" Tests-first = "what should this do?" | 2 |
| "Keep code as reference" | Don't keep untested code as reference | 3 |

## Testing Different Skill Types

### Discipline Skills (Rules)

**Test with:** Pressure scenarios

**Example:** "verification-before-completion" skill
- Pressure: "Ship it, we're late"
- Pressure: "Just this one time"
- Pressure: "Testing is taking too long"

**Success:** Agent follows rule under maximum pressure

### Technique Skills (How-To)

**Test with:** Application scenarios

**Example:** "condition-based-waiting" skill
- Scenario: Async test that flakes
- Scenario: Need to wait for element
- Scenario: Multiple conditions to check

**Success:** Agent applies technique correctly

### Pattern Skills (Mental Models)

**Test with:** Recognition scenarios

**Example:** "information-hiding" skill
- Scenario: When to use abstraction
- Scenario: When abstraction is overkill
- Scenario: Counter-examples

**Success:** Agent correctly identifies when pattern applies

### Reference Skills (Documentation)

**Test with:** Retrieval scenarios

**Example:** API documentation skill
- Scenario: Find endpoint for X
- Scenario: Look up parameter for Y
- Scenario: Understand error Z

**Success:** Agent finds and applies correct information

## Common Violations

### ❌ "The skill is obviously clear"

**Reality:** Clear to you ≠ clear to other agents.

**Fix:** Test it anyway.

### ❌ "It's just a reference"

**Reality:** References can have gaps, unclear sections.

**Fix:** Test retrieval scenarios.

### ❌ "Testing is overkill"

**Reality:** Untested skills have issues. Always.

**Fix:** 15 min testing saves hours of debugging.

### ❌ "I'll test if problems emerge"

**Reality:** Problems = agents can't use skill.

**Fix:** Test BEFORE deploying.

### ❌ "Too tedious to test"

**Reality:** Testing is less tedious than debugging bad skill.

**Fix:** Test anyway.

## The Testing Checklist

For every skill:

- [ ] Created pressure scenarios (3+ for discipline skills)
- [ ] Ran scenarios WITHOUT skill - documented baseline
- [ ] Identified patterns in rationalizations
- [ ] Wrote skill addressing specific failures
- [ ] Ran scenarios WITH skill - verified compliance
- [ ] Identified NEW rationalizations
- [ ] Added explicit counters
- [ ] Re-tested until bulletproof
- [ ] Documented all rationalizations in table

## Bottom Line

**Creating skills IS TDD for documentation.**

Same Iron Law: No skill without failing test first.
Same cycle: RED → GREEN → REFACTOR.
Same benefits: Better quality, fewer surprises, bulletproof results.

If you follow TDD for code, follow it for skills.
