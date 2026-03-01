# Plan Template

Standard template for implementation plan documents.

## Plan Document Structure

Every implementation plan must follow this structure:

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED: Use executing-plans skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---

## File Structure

**New Files:**
- `path/to/new/file.ext` - [Brief description]

**Modified Files:**
- `path/to/existing/file.ext:123-145` - [What changes]

---

## Task Breakdown

[All tasks listed here]

---

## Testing Strategy

[How we'll verify this works]

---

## Deployment Notes

[Any special deployment considerations]
```

## Header Section

### Goal

Single, clear sentence:

**✅ Good:**
> Build a user authentication system with email/password login and JWT token management.

**❌ Bad:**
> Implement auth stuff.

### Architecture

2-3 sentences explaining the approach:

**✅ Good:**
> We'll use JWT tokens stored in HTTP-only cookies for session management. Passwords will be hashed with bcrypt. The authentication service will be a separate module that can be imported by both API and web frontends.

**❌ Bad:**
> Use JWT and bcrypt.

### Tech Stack

List key technologies:

**✅ Good:**
> Python 3.11+, FastAPI 0.100+, SQLAlchemy 2.0, PostgreSQL 15, bcrypt, PyJWT

**❌ Bad:**
> Python and some libraries.

## File Structure Section

List all files that will be created or modified:

```markdown
## File Structure

**New Files:**
- `src/auth/__init__.py` - Auth module initialization
- `src/auth/models.py` - User model and database schema
- `src/auth/service.py` - Authentication logic
- `src/auth/routes.py` - API endpoints
- `tests/auth/test_login.py` - Login tests
- `tests/auth/test_registration.py` - Registration tests
- `migrations/001_create_users.sql` - Database schema

**Modified Files:**
- `src/main.py:15-20` - Register auth routes
- `src/database.py:10-15` - Add user table to base
- `requirements.txt` - Add dependencies
```

## Task Section Format

Each task follows this exact format:

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: [Action description]**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: [Action description]**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: [Action description]**

```python
def function(input):
    return expected
```

**Step 4: [Action description]**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASSED

**Step 5: [Action description]**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Testing Strategy Section

Brief overview of the testing approach:

```markdown
## Testing Strategy

- **Unit Tests:** All business logic in service.py
- **Integration Tests:** API endpoints with test database
- **Edge Cases:** Empty inputs, invalid passwords, duplicate emails
- **Performance:** Login response time < 200ms at 100 req/s
```

## Deployment Notes Section

Any special considerations for deployment:

```markdown
## Deployment Notes

- Run migrations before deploying code
- Set JWT_SECRET environment variable
- Update production database schema
- Clear cached user data after deployment
```

## Example Complete Plan

```markdown
# User Authentication Implementation Plan

> **For Claude:** REQUIRED: Use executing-plans skill to implement this plan task-by-task.

**Goal:** Build a user authentication system with email/password login and JWT token management.

**Architecture:** We'll use JWT tokens stored in HTTP-only cookies for session management. Passwords will be hashed with bcrypt. The authentication service will be a separate module that can be imported by both API and web frontends.

**Tech Stack:** Python 3.11+, FastAPI 0.100+, SQLAlchemy 2.0, PostgreSQL 15, bcrypt, PyJWT

---

## File Structure

**New Files:**
- `src/auth/__init__.py` - Auth module initialization
- `src/auth/models.py` - User model and database schema
- `src/auth/service.py` - Authentication logic
- `src/auth/routes.py` - API endpoints
- `tests/auth/test_login.py` - Login tests
- `tests/auth/test_registration.py` - Registration tests
- `migrations/001_create_users.sql` - Database schema

**Modified Files:**
- `src/main.py:15-20` - Register auth routes
- `src/database.py:10-15` - Add user table to base
- `requirements.txt` - Add fastapi, sqlalchemy, bcrypt, pyjwt

---

## Task Breakdown

### Task 1: Create User Model

**Files:**
- Create: `src/auth/models.py`
- Test: `tests/auth/test_models.py`

**Step 1: Write failing test for user creation**

Create `tests/auth/test_models.py`:

```python
import pytest
from auth.models import User

def test_create_user_with_password():
    user = User(email="test@example.com", password="secret123")
    assert user.email == "test@example.com"
    assert user.password_hash != "secret123"  # Should be hashed
    assert user.check_password("secret123") is True
    assert user.check_password("wrong") is False
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/auth/test_models.py -v
```
Expected: `FAILED - ImportError: No module named 'auth.models'`

**Step 3: Create user model**

Create `src/auth/models.py`:

```python
import bcrypt
from sqlalchemy import Column, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/auth/test_models.py::test_create_user_with_password -v
```
Expected: PASSED

**Step 5: Commit**

```bash
git add src/auth/models.py tests/auth/test_models.py
git commit -m "feat: add user model with password hashing"
```

### Task 2: Create Authentication Service

[Continues with all tasks...]

---

## Testing Strategy

- **Unit Tests:** All business logic in service.py
- **Integration Tests:** API endpoints with test database
- **Edge Cases:** Empty inputs, invalid passwords, duplicate emails
- **Performance:** Login response time < 200ms at 100 req/s

---

## Deployment Notes

- Run migrations before deploying code
- Set JWT_SECRET environment variable
- Update production database schema
- Clear cached user data after deployment
```

## Anti-Patterns

### ❌ Missing File Paths

> "Create a user model"

**✅ Include exact paths:**
> Create: `src/auth/models.py`

### ❌ Vague Steps

> "Add validation"

**✅ Be specific:**
> Write test for email format validation
> Run test to verify it accepts valid email
> Implement email regex check
> Run test to verify it rejects invalid email

### ❌ Missing Expected Output

> "Run the tests"

**✅ Include expected result:**
> Run: `pytest tests/auth/test_login.py -v`
> Expected: 3 passed, 0 failed

### ❌ Grouping Actions

> "Create the model, write tests, and implement"

**✅ Separate into discrete steps:**
> Step 1: Write failing test
> Step 2: Run test to verify failure
> Step 3: Implement model
> Step 4: Run test to verify pass
> Step 5: Commit
