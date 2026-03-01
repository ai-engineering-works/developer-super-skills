# Skill Anti-Patterns

Common mistakes to avoid when authoring Agent Skills.

## Anti-Patterns

### ❌ Narrative Storytelling

Telling a story about how you solved a problem once.

**Example:**
```markdown
## The Problem

In session 2025-10-03, we were working on project X and noticed that empty projectDir caused our CI to fail...

## The Solution

We discovered that adding a check for empty strings fixed the issue...
```

**Why Bad:** Too specific, not reusable, hard to extract principles.

**✅ Instead:** Describe the pattern and when to apply it.

### ❌ Multi-Language Dilution

Providing the same example in multiple languages.

**Example:**
```
skills/my-skill/
  example.js
  example.py
  example.go
  example.rs
```

**Why Bad:** Mediocre quality across all, maintenance burden.

**✅ Instead:** One excellent example in the most relevant language.

### ❌ Code in Flowcharts

Putting code inside graphviz diagrams.

**Example:**
```dot
step1 [label="import fs"];
step2 [label="read file"];
```

**Why Bad:** Can't copy-paste, hard to read.

**✅ Instead:** Use markdown code blocks outside flowcharts.

### ❌ Generic Labels

Non-semantic labels in diagrams.

**Example:**
```dot
helper1 [shape=box];
helper2 [shape=box];
pattern4 [shape=diamond];
```

**Why Bad:** Labels don't convey meaning.

**✅ Instead:** Use descriptive names.
```dot
validateInput [shape=box];
parseData [shape=box];
hasData? [shape=diamond];
```

### ❌ Description Summarizes Workflow

Including process steps in the description field.

**Example:**
```yaml
description: Use for TDD - write test first, watch it fail, write minimal code, refactor
```

**Why Bad:** Claude follows description instead of reading skill body.

**✅ Instead:** Trigger-only description.
```yaml
description: Use when implementing any feature or bugfix, before writing implementation code
```

### ❌ Verbose Examples

Long examples with unnecessary detail.

**Example:**
```python
# ❌ BAD: 42 words with setup
def test_user_login():
    # First, we need to create a test user in the database
    # We'll use the SQLAlchemy ORM for this
    # The user needs an email and a password
    user = User(
        email="test@example.com",  # Using test email
        password="secret123"       # Using a simple password
    )
    # Now we can test the login function...
```

**✅ Instead:** Concise example (20 words).
```python
# ✅ GOOD: To the point
def test_user_login():
    result = login("test@example.com", "secret123")
    assert result["token"] is not None
```

### ❌ Over-Engineering

Adding complexity "just in case."

**Example:**
```markdown
## When to Use This Skill

Use this when:
- Testing functions (or methods, or procedures)
- Testing classes (or modules, or components)
- Testing APIs (or endpoints, or interfaces)
- Testing data structures (or objects, or records)
```

**Why Bad:** Redundant, harder to scan.

**✅ Instead:** "Testing functions, classes, APIs, data structures"

### ❌ Premature Abstraction

Creating reference files for minimal content.

**Example:**
```
skills/my-skill/
  SKILL.md          # 50 lines
  references/
    patterns.md     # 15 lines - too short!
```

**Why Bad:** Reference files should be 100+ lines.

**✅ Instead:** Keep content inline until it grows.

### ❌ Redundant Cross-References

Repeating content from other skills.

**Example:**
```markdown
## TDD Workflow

1. Write failing test
2. Run test to verify it fails
3. Write minimal code
4. Run test to verify it passes
5. Refactor

[TDD is explained in detail in the tdd skill...]
```

**Why Bad:** Wastes tokens, maintenance burden.

**✅ Instead:** "See tdd skill for complete TDD workflow."

### ❌ Fill-in-the-Blank Templates

Templates that require user to figure out what goes in blanks.

**Example:**
```python
def test_[name]():
    input = [TODO: add test input]
    result = [TODO: call function]
    assert result == [TODO: expected result]
```

**Why Bad:** Not a complete, working example.

**✅ Instead:** Full example with real values.

### ❌ Contrived Examples

Examples that don't come from real scenarios.

**Example:**
```python
# ❌ BAD: Not a real test case
def test_foo_adds_numbers():
    assert foo.add(1, 1) == 2
    assert foo.add(2, 2) == 4
```

**✅ Instead:** Example from actual usage.
```python
# ✅ GOOD: Real scenario
def test_calculate_order_total():
    items = [{"price": 10.00, "qty": 2}, {"price": 15.50, "qty": 1}]
    assert calculate_total(items) == 35.50
```

## Anti-Pattern Detection

### Check Your Skill For:

1. **Narrative elements** - "In session X we did Y"
2. **Multiple language examples** - More than one code language
3. **Code in diagrams** - Code inside graphviz/mermaid
4. **Generic labels** - helper1, step2, pattern3
5. **Workflow in description** - "Use for X - does A, then B"
6. **Verbose examples** - Long setup, unnecessary comments
7. **Over-categorization** - Excessive parenthetical alternatives
8. **Tiny reference files** - Under 100 lines
9. **Repeated content** - Same info in multiple skills
10. **Template placeholders** - TODO, FIXME, [add here]

### Quick Validation

Ask these questions:

- [ ] Would another developer understand this without context?
- [ ] Can I extract the principle from one concrete example?
- [ ] Is the example real (not contrived)?
- [ ] Does the description force reading the skill body?
- [ ] Are reference files 100+ lines (if they exist)?
- [ ] Is every word earning its keep?

## Red Flags

🚩 **"This is simple so..."** - Maybe needs design too

🚩 **"Everyone knows..."** - Not true, document it

🚩 **"It's obvious..."** - If it were, we wouldn't need skills

🚩 **"Just add..."** - Vague, be specific

🚩 **"Etc., etc."** - Finish the list

🚩 **"And so on"** - Complete the thought

🚩 **"For more info see..."** - Include the info or reference

## Learning from Mistakes

### Common First-Time Mistakes

1. **Writing prose instead of patterns**
   - **Fix:** Extract the reusable pattern

2. **Including too much context**
   - **Fix:** Get to the point, reference for details

3. **Making assumptions about reader knowledge**
   - **Fix:** Include complete working examples

4. **Creating for yourself, not others**
   - **Fix:** Write for someone with zero context

5. **Not testing the skill**
   - **Fix:** Always run pressure scenarios first
