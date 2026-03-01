# TDD Planning

Planning Test-Driven Development for implementation plans.

## TDD in Implementation Plans

Every implementation step should follow the TDD cycle:

1. **RED** - Write a failing test
2. **GREEN** - Write minimal code to pass
3. **REFACTOR** - Improve the code
4. **COMMIT** - Save progress

## Planning TDD Tasks

### Task Template

Each TDD task includes:

```markdown
### Step N: [Feature name]

**RED - Write failing test:**
[Test code here]

**GREEN - Run test, verify failure:**
```bash
[Command here]
```
Expected: [Specific failure message]

**GREEN - Write minimal implementation:**
[Code here]

**GREEN - Run test, verify success:**
```bash
[Command here]
```
Expected: PASSED

**[Optional] REFACTOR - Improve:**
[Refactoring description]

**COMMIT:**
```bash
git add [files]
git commit -m "[message]"
```
```

## Test Types to Plan

### Unit Tests

Test individual functions, classes, or components in isolation.

**When:** Every function/method that contains logic

**Example:**
```python
def test_calculate_total_with_single_item():
    result = calculate_total([{"price": 10, "qty": 1}])
    assert result == 10
```

### Integration Tests

Test how components work together.

**When:** Components interact (API → database, service → external API)

**Example:**
```python
def test_create_user_persists_to_database():
    response = client.post("/users", json={"email": "test@example.com"})
    assert response.status_code == 201
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user is not None
```

### Edge Case Tests

Test boundary conditions and error cases.

**When:** After happy path works

**Examples:**
- Empty inputs
- Null/undefined values
- Maximum/minimum values
- Invalid formats
- Concurrent operations

### Regression Tests

Tests for bugs that were found and fixed.

**When:** After fixing any bug

**Purpose:** Ensure the bug doesn't come back

## Planning Test Order

### Start with Happy Path

1. Test the most common, successful scenario
2. Get that working
3. Then add edge cases

**Why:** Establishes baseline functionality first

### Then Edge Cases

After happy path passes:

1. Empty inputs
2. Null/undefined values
3. Invalid data types
4. Boundary values (0, -1, max_int)
5. Duplicate entries

### Then Error Cases

After normal cases work:

1. Network failures
2. Database connection errors
3. Invalid permissions
4. Missing dependencies

## Common TDD Patterns

### Arrange-Act-Assert

```python
def test_user_creation():
    # Arrange
    user_data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = User.create(user_data)

    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

### Given-When-Then

```python
def test_order_processing():
    # Given
    user = create_user()
    product = create_product(price=100)

    # When
    order = process_order(user, product, quantity=2)

    # Then
    assert order.total == 200
    assert order.user_id == user.id
```

### Table-Based Tests

```python
@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (1, 1),
    (2, 4),
    (10, 100),
])
def test_square(input, expected):
    assert square(input) == expected
```

## Planning for Specific Scenarios

### Database Operations

1. **Test:** Query returns empty results
2. **Test:** Insert single record
3. **Test:** Query returns inserted record
4. **Test:** Update record
5. **Test:** Query returns updated record
6. **Test:** Delete record
7. **Test:** Query confirms deletion

### API Endpoints

1. **Test:** GET endpoint returns 404 without data
2. **Test:** POST creates resource
3. **Test:** GET returns created resource
4. **Test:** PUT updates resource
5. **Test:** GET returns updated resource
6. **Test:** DELETE removes resource
7. **Test:** GET returns 404 after deletion

### Authentication/Authorization

1. **Test:** Login fails with wrong credentials
2. **Test:** Login succeeds with correct credentials
3. **Test:** Protected endpoint returns 401 without token
4. **Test:** Protected endpoint returns 403 with wrong permissions
5. **Test:** Protected endpoint succeeds with correct permissions

### Async Operations

1. **Test:** Function starts async operation
2. **Test:** Callback/onSuccess is called on success
3. **Test:** Callback/onError is called on failure
4. **Test:** Cleanup runs after completion

## What NOT to Test

Don't write tests for:

- **Trivial getters/setters** - `return self.variable`
- **External libraries** - Trust their tests
- **Configuration constants** - Not executable code
- **UI that doesn't have logic** - Visual testing is different
- **Code that will be replaced** - Wait for stable design

## Test Data in Plans

Always include complete test data in the plan:

**✅ Good:**
```python
def test_calculate_order_total():
    items = [
        {"name": "Widget", "price": 10.00, "quantity": 2},
        {"name": "Gadget", "price": 15.50, "quantity": 1},
    ]
    result = calculate_total(items)
    assert result == 35.50
```

**❌ Bad:**
```python
def test_calculate_order_total():
    # Use some test items
    result = calculate_total(items)
    assert result == expected  # What's expected?
```

## Mocking in Plans

When to use mocks:

- **External APIs** - Don't call real services in tests
- **Database** - Use in-memory or test database
- **Time/Date** - Freeze time for deterministic tests
- **File System** - Use temp directories

**Example:**
```python
def test_api_client_with_mock():
    # Arrange
    mock_response = {"data": "test"}
    with patch('requests.get', return_value=mock_response):
        client = APIClient()

        # Act
        result = client.fetch_data()

        # Assert
        assert result == {"data": "test"}
```

## Expected Outputs in Plans

Always specify what the test/output should return:

**For tests:**
- Specific assertion that should pass
- Exact error message for failure cases

**For commands:**
- Exit code: `0` for success, `1` for failure
- Output text: Contains specific message
- Side effects: File created, row inserted, etc.

**✅ Good:**
```bash
pytest tests/test_auth.py -v
```
Expected: 5 passed, 0 failed

**❌ Bad:**
```bash
pytest tests/test_auth.py -v
```
Expected: Tests pass
