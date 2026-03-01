# Testing Skills with Subagents

Complete methodology for testing Agent Skills using subagent pressure scenarios.

## Overview

Testing skills requires a different approach than testing code. You don't unit test skills - you test them by running **pressure scenarios** with subagents and observing their behavior.

## The Testing Methodology

### Pressure Scenarios

A pressure scenario is a situation where an agent might be tempted to violate the rule your skill enforces.

**Types of Pressure:**

1. **Time Pressure** - "This needs to be done in 10 minutes"
2. **Authority Pressure** - "The lead developer said skip tests for this"
3. **Sunk Cost** - "I already wrote 100 lines, writing tests now is wasteful"
4. **Exhaustion** - "This is the 50th test case, can't we just move on?"
5. **Peer Pressure** - "Everyone else skips tests for simple functions"

### Testing Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. DESIGN SCENARIO                                        │
│     Create a situation where the skill should apply         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  2. BASELINE TEST (RED)                                     │
│     Run scenario WITHOUT skill - document violations        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  3. WRITE SKILL (GREEN)                                     │
│     Address specific violations with minimal skill          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  4. COMPLIANCE TEST                                        │
│     Run scenario WITH skill - verify compliance             │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  5. FIND NEW RATIONALIZATIONS (REFACTOR)                    │
│     Agent found loopholes? Add explicit counters             │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
         Repeat until bulletproof
```

## Designing Pressure Scenarios

### For Discipline Skills

**Target:** Skills that enforce rules or requirements

**Example:** "test-first-development" skill

**Scenario Design:**
1. **Identify the rule** - Must write test before code
2. **Identify violations** - Writing code first, skipping tests
3. **Design pressures** for each violation:
   - Time: "We're late, just write the code"
   - Complexity: "This is too simple for TDD"
   - Authority: "Lead said skip tests for this one"
   - Sunk cost: "Code is already written"

**Full Scenario:**
```
Task: Add a simple validation function

Pressure: Time constraint - "We need this in 10 minutes"

Expected violation: Agent writes code first
Rationalization: "Too simple for TDD", "Will test after"
```

### For Technique Skills

**Target:** Skills that teach how-to approaches

**Example:** "condition-based-waiting" skill

**Scenario Design:**
1. **Identify the technique** - Wait for conditions vs sleep/timeouts
2. **Identify misuse** - Using setTimeout/sleep
3. **Design test cases:**
   - Basic scenario: Test that flakes occasionally
   - Edge case: Test that times out unpredictably
   - Complex scenario: Multiple conditions to check

**Full Scenario:**
```
Task: Fix a flaky test that sometimes fails

Context: Test checks for element that appears asynchronously

Expected violation: Agent adds sleep(5000)
Rationalization: "Simple fix", "Works reliably now"
```

### For Pattern Skills

**Target:** Skills that teach mental models or approaches

**Example:** "information-hiding" skill

**Scenario Design:**
1. **Identify the pattern** - Hide implementation details
2. **Identify violations** - Exposing internals, tight coupling
3. **Design situations:**
   - When to apply: Multiple components need same data
   - When NOT to apply: Single-use case, simple wrapper

**Full Scenario:**
```
Task: Create a data processing module

Context: Multiple parts of application need user data

Expected violation: Direct database access from each module
Rationalization: "Simpler", "Fewer files", "Easier to debug"
```

## Running the Baseline Test

### Without the Skill

Dispatch a subagent with the scenario, WITHOUT loading your skill:

```python
dispatch_subagent(
    task=scenario,
    context=project_context,
    skill=None  # No skill loaded
)
```

### Document Behavior

Record exactly what happens:

**Observation Template:**
```
Scenario: [Description]

Pressure Applied: [Type and wording]

Agent Behavior:
- [What they did]
- [What they said]

Rationalizations Captured:
- "[Verbatim excuse 1]"
- "[Verbatim excuse 2]"

Violations:
- [Which rule(s) were broken]
- [How they justified it]
```

**Example:**
```
Scenario: Add validation function with 10-minute deadline

Pressure Applied: Time constraint

Agent Behavior:
- Wrote function implementation first (12 lines)
- Added test after function was complete
- Committed code and test together

Rationalizations Captured:
- "This is too simple for full TDD"
- "Writing test first would take too much time"
- "We can test after, it achieves the same goal"

Violations:
- Wrote code before test (TDD violation)
- Skipped RED phase
- No failing test observed
```

## Writing the Skill

### Address Specific Failures

Use the exact rationalizations from baseline testing:

**From Baseline:**
> "This is too simple for TDD"
> "Writing test first takes too much time"
> "Test after achieves same goal"

**Skill Content:**
```markdown
## Constraints

### MUST NOT DO
- Write code before test - Delete it, start over
- Skip testing because "too simple" - Simple code breaks too
- Plan to test "after" - Tests after = "what does this do?" Tests first = "what should this do?"

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple for TDD" | Simple code breaks. Test takes 30 seconds. |
| "Test after achieves same goal" | Tests after check behavior. Tests first check understanding. |
| "Takes too much time" | Untested code takes longer to debug. |
```

## Testing Compliance

### With the Skill

Now dispatch a subagent WITH your skill loaded:

```python
dispatch_subagent(
    task=scenario,
    context=project_context,
    skill="your-skill-name"  # Load the skill
)
```

### Success Criteria

- ✅ Agent follows the rule
- ✅ Agent references the skill guidance
- ✅ Agent explains their compliance
- ✅ Output matches expected behavior

### Failure Modes

If agent still violates:
- ❌ Skill is unclear (revise explanation)
- ❌ Skill has loopholes (add explicit counter)
- ❌ Agent didn't read skill (strengthen description)
- ❌ Pressure overcame skill (add more specific counter)

## Finding Loopholes

### Iterative Testing

Agents are smart and will find workarounds:

**Iteration 1:** "Write code before test? Delete it."
**Agent loophole:** Keeps code open in editor as "reference"

**Iteration 2:** Add: "Don't keep untested code as reference. That's a violation."
**Agent loophole:** Writes code in comments first

**Iteration 3:** Add: "No comments with code implementation either."
**Agent complies:** ✓

### Rationalization Table

Maintain throughout iterations:

| Rationalization | Counter Added | Iteration |
|----------------|---------------|-----------|
| Too simple for TDD | Simple code breaks too | 1 |
| Keep as reference | Don't keep untested code as reference | 2 |
| Comments OK | No code in comments either | 3 |

## Meta-Testing

### Testing Your Tests

Are your pressure scenarios realistic?

**Checklist:**
- [ ] Could this actually happen in real usage?
- [ ] Is the pressure something agents face?
- [ ] Are the rationalizations plausible?

### Test Coverage

Do your scenarios cover:

- [ ] **Primary use case** - Main skill purpose
- [ ] **Edge cases** - Boundary conditions
- [ ] **Pressure situations** - Time, authority, exhaustion
- [ ] **Ambiguity** - When it's unclear if skill applies

## Testing Workflow Checklist

For each skill:

### Design Phase
- [ ] Identified skill type (discipline/technique/pattern)
- [ ] Listed all expected violations
- [ ] Designed 3+ pressure scenarios
- [ ] Included combined pressures (time + authority, etc.)

### Baseline Phase
- [ ] Ran scenario WITHOUT skill
- [ ] Documented agent behavior verbatim
- [ ] Captured exact rationalizations
- [ ] Identified which rules were broken

### Skill Writing Phase
- [ ] Wrote skill addressing specific failures
- [ ] Added rationalization table
- [ ] Included explicit counters for each rationalization
- [ ] Added "Red Flags" list for self-checking

### Compliance Phase
- [ ] Ran scenario WITH skill
- [ ] Verified agent compliance
- [ ] Documented any new rationalizations
- [ ] Added counters for new rationalizations
- [ ] Re-tested until bulletproof

## Common Testing Mistakes

### ❌ Testing with Yourself

Testing by using the skill yourself doesn't count.

**Why:** You wrote it, so you know what it means.

**Fix:** Always test with a fresh subagent that hasn't seen the skill.

### ❌ Weak Pressures

Gentle scenarios that don't really tempt violation.

**Why:** Real pressures are stronger.

**Fix:** Use realistic, strong pressures from actual experience.

### ❌ Skipping Edge Cases

Only testing the happy path.

**Why:** Agents exploit edge cases.

**Fix:** Test boundaries, empty inputs, weird combinations.

### ❌ Stopping After First Pass

Testing once and declaring success.

**Why:** Agents find new loopholes each round.

**Fix:** Iterate until you see no new rationalizations.

## Example Complete Test

### Skill: test-first-development

**Scenario 1: Simple Function**
```
Task: Add email validation function (5 min deadline)

Baseline: Wrote function first, no test
Skill: Must write test first, observe failure, then implement
Result: ✓ Complied
```

**Scenario 2: Complex Feature**
```
Task: Build payment processing (lead says skip tests)

Baseline: Started implementation, "tests slow us down"
Skill: No exceptions, no authority overrides TDD
Result: ✓ Complied after revision
```

**Scenario 3: Bug Fix**
```
Task: Fix production issue (code already written)

Baseline: "Adding test now is pointless"
Skill: Start over if code written before test
Result: ✓ Deleted code, started with test
```

## Tools and Techniques

### Subagent Dispatch

Use the Task tool with a clean context:

```
Test this scenario WITHOUT the skill:
[Scenario description]

Do NOT use [skill-name]. Just do what seems natural.
```

### Observation Scripting

Create a script for each test:

```python
# test_tdd_skill.py

def test_simple_function_pressure():
    scenario = """
    Task: Add email validation function
    Constraint: 5 minute deadline
    """

    # Run without skill
    baseline = run_subagent(scenario, skill=None)
    assert violates_tdd(baseline)
    assert "too simple" in baseline.rationalizations

    # Run with skill
    with_skill = run_subagent(scenario, skill="tdd")
    assert follows_tdd(with_skill)
```

### Documentation Template

For each test run, document:

```
Date: YYYY-MM-DD
Skill: [skill-name]
Scenario: [description]

Baseline:
- Behavior: [what happened]
- Rationalizations: [verbatim quotes]
- Violations: [which rules]

With Skill:
- Behavior: [what happened]
- Compliance: [yes/no]
- Issues: [any problems]

Next Actions:
- [ ] Add counter for [rationalization]
- [ ] Clarify section about [topic]
- [ ] Re-test scenario
```

## Summary

Testing skills with subagents is different from unit testing code:

1. **Design pressure scenarios** - Situations that tempt violations
2. **Run baseline** - Document what agents do WITHOUT skill
3. **Write targeted skill** - Address specific rationalizations
4. **Test compliance** - Verify agents follow skill with pressure
5. **Iterate** - Close loopholes until bulletproof

This is the TDD cycle applied to documentation: RED (watch them fail), GREEN (write skill), REFACTOR (close loopholes).
