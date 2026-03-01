# Task Breakdown

Breaking implementation work into bite-sized, executable tasks that any developer can follow.

## Granularity Principle

**Each step = One action = 2-5 minutes**

If a step takes longer than 5 minutes, it needs to be broken down further.

## What Makes a Good Task?

### Characteristics

✅ **Single action** - Do one thing only
✅ **Atomic** - Can't be meaningfully split further
✅ **Verifiable** - Clear success/failure criteria
✅ **Independent** - Doesn't depend on mid-task decisions
✅ **Complete** - Includes all necessary code/commands

### Examples

**❌ Too coarse:**
> "Implement the user authentication system"

**✅ Proper breakdown:**
1. Write failing test for `login()` function
2. Run test to verify it fails with "function not defined"
3. Write minimal `login()` function signature
4. Run test to verify it fails with "incorrect credentials"
5. Implement credential validation logic
6. Run test to verify it passes
7. Write test for invalid credentials
8. Run test to verify it fails
9. Implement error handling
10. Run test to verify it passes
11. Commit "feat: add user login with validation"

## TDD Task Pattern

Every feature implementation follows this pattern:

### 1. Write the Failing Test

```python
def test_user_login_with_valid_credentials():
    response = auth.login("user@example.com", "password123")
    assert response.status_code == 200
    assert response.json()["token"] is not None
```

**Why:** Establishes what success looks like before writing code.

### 2. Run Test to Verify It Fails

```bash
pytest tests/auth/test_login.py::test_user_login_with_valid_credentials -v
```

**Expected output:** `FAILED - NameError: name 'auth' is not defined`

**Why:** Confirms the test is testing something real, not already implemented.

### 3. Write Minimal Implementation

```python
def login(email, password):
    # TODO: Implement actual authentication
    return {"status": 200, "token": "fake-token"}
```

**Why:** Smallest code that could possibly work.

### 4. Run Test to Verify It Passes

```bash
pytest tests/auth/test_login.py::test_user_login_with_valid_credentials -v
```

**Expected output:** `PASSED`

**Why:** Confirms we're making progress toward the goal.

### 5. Commit

```bash
git add tests/auth/test_login.py src/auth.py
git commit -m "feat: add basic login function"
```

**Why:** Small commits make debugging and rollback easier.

## Common Task Types

### Database Changes

1. Write migration file: `add_users_table.sql`
2. Run migration: `python manage.py migrate`
3. Verify table exists: `\d users` in psql
4. Write model file: `models/user.py`
5. Write test for model creation
6. Run test to verify it fails
7. Implement model with fields
8. Run test to verify it passes
9. Commit

### API Endpoints

1. Write test for endpoint: `test_create_user()`
2. Run test to verify 404
3. Add route to `urls.py`
4. Run test to verify 405 (method not allowed)
5. Add view function in `views.py`
6. Run test to verify 500 (server error)
7. Implement view logic
8. Run test to verify 200
9. Commit

### Frontend Components

1. Write test for component rendering
2. Run test to verify failure
3. Create component file
4. Add basic component structure
5. Run test to verify rendering
6. Add props/types
7. Write test for prop usage
8. Run test to verify failure
9. Implement prop handling
10. Run test to verify pass
11. Commit

### Configuration Changes

1. Write test that reads config value
2. Run test to verify failure (key not found)
3. Add config key to `.env.example`
4. Add config loading code
5. Run test to verify pass
6. Document in README
7. Commit

## Handling Dependencies

### File Creation

1. Write test that imports the file
2. Run test - verify import error
3. Create file with basic structure
4. Run test - verify file exists
5. Continue with implementation...

### Cross-File Changes

1. Write test for both files working together
2. Run test - verify missing functionality
3. Update file A
4. Run test - verify partial progress
5. Update file B
6. Run test - verify pass
7. Commit both files together

### External Services

1. Write test with mock/stub
2. Run test - verify mock called correctly
3. Implement real service call
4. Write integration test (can be skipped in CI)
5. Commit

## Anti-Patterns

### ❌ "Add Validation"

Too vague. What validation? What fields? What rules?

**✅ Instead:**
1. Write test for email format validation
2. Run test to verify it passes invalid email
3. Implement email regex check
4. Run test to verify it rejects invalid email
5. Write test for valid email
6. Run test to verify it accepts valid email
7. Commit

### ❌ "Set Up Database"

Multiple actions disguised as one step.

**✅ Instead:**
1. Create migration file
2. Run migration
3. Verify table created
4. [Commit]

### ❌ "Fix Bug"

Doesn't define what the fix is.

**✅ Instead:**
1. Write failing test demonstrating bug
2. Run test to verify it fails
3. Implement fix
4. Run test to verify it passes
5. Write regression test
6. Run all tests
7. Commit

## Verifying Task Quality

Ask these questions for each task:

1. **Can a new developer complete this in under 5 minutes?**
2. **Is there exactly one action to take?**
3. **Will they know when it's done?**
4. **Are all file paths specified?**
5. **Is all necessary code provided?**

If any answer is "no," the task needs more detail.

## Sample Complete Task

```markdown
### Task 5: User Login

**Files:**
- Create: `src/auth/login.py`
- Test: `tests/auth/test_login.py`

**Step 1: Write failing test**

Create `tests/auth/test_login.py`:

```python
import pytest
from auth.login import login

def test_login_with_valid_credentials():
    result = login("user@example.com", "correct_password")
    assert result["success"] is True
    assert "token" in result
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/auth/test_login.py -v
```

Expected: `FAILED - ImportError: No module named 'auth.login'`

**Step 3: Create module structure**

```bash
touch src/auth/__init__.py
touch src/auth/login.py
```

**Step 4: Run test to verify it fails again**

```bash
pytest tests/auth/test_login.py -v
```

Expected: `FAILED - AttributeError: module 'auth.login' has no attribute 'login'`

**Step 5: Write minimal login function**

Create `src/auth/login.py`:

```python
def login(email, password):
    # TODO: Implement actual auth
    return {"success": True, "token": "temp-token"}
```

**Step 6: Run test to verify it passes**

```bash
pytest tests/auth/test_login.py -v
```

Expected: `PASSED`

**Step 7: Commit**

```bash
git add src/auth/ tests/auth/test_login.py
git commit -m "feat: add basic login function"
```
```
