# Testing Anti-Patterns

---

## Core Principle

> **"Test what the code does, not what the mocks do."**

When tests verify mock behavior instead of actual functionality, they provide false confidence while catching zero real bugs.

---

## The Five Anti-Patterns

### Anti-Pattern 1: Testing Mock Behavior

**The Problem:** Verifying that mocks exist and were called, rather than testing actual component output.

```python
# BAD: Testing the mock, not the behavior
def test_calls_the_api():
    mock_api = Mock()
    mock_api.get_user.return_value = {"id": 1, "name": "Alice"}
    service = UserService(mock_api)

    service.get_user(1)

    mock_api.get_user.assert_called_with(1)  # Testing mock, not result
```

```python
# GOOD: Testing actual behavior
async def test_returns_user_data_from_api():
    mock_api = AsyncMock()
    mock_api.get_user.return_value = {"id": 1, "name": "Alice"}
    service = UserService(mock_api)

    user = await service.get_user(1)

    assert user["name"] == "Alice"  # Testing actual output
```

**Solution:** Test the genuine component output. If you can only verify mock calls, reconsider whether the test adds value.

---

### Anti-Pattern 2: Test-Only Methods in Production

**The Problem:** Adding methods to production classes solely for test setup or cleanup.

```python
# BAD: Production code polluted with test concerns
class UserCache:
    def __init__(self):
        self._cache: dict[int, User] = {}

    def get_user(self, user_id: int) -> User | None:
        return self._cache.get(user_id)

    # This method exists ONLY for tests
    def _reset_for_testing(self):
        self._cache.clear()
```

```python
# GOOD: Test utilities separate from production
# production: user_cache.py
class UserCache:
    def __init__(self):
        self._cache: dict[int, User] = {}

    def get_user(self, user_id: int) -> User | None:
        return self._cache.get(user_id)

# test: conftest.py
@pytest.fixture
def cache():
    """Fresh cache instance per test."""
    return UserCache()
```

**Solution:** Relocate cleanup logic to test fixtures. Use fresh instances per test instead of reset methods.

---

### Anti-Pattern 3: Mocking Without Understanding

**The Problem:** Over-mocking without grasping side effects, leading to tests that pass but hide real issues.

```python
# BAD: Mocking everything without understanding
@patch("app.services.inventory.check_stock")
@patch("app.services.payment.charge")
@patch("app.services.shipping.create_label")
@patch("app.services.notifications.send")
def test_processes_order(mock_notify, mock_ship, mock_pay, mock_stock):
    mock_stock.return_value = True
    mock_pay.return_value = {"status": "success"}

    result = process_order(order)

    assert result["success"] is True  # What did we actually test?
```

```python
# GOOD: Strategic mocking with real components where possible
def test_processes_order_with_real_inventory(db_session):
    # Real inventory service against test database
    inventory = InventoryService(db_session)
    inventory.add_stock("item_1", quantity=10)

    # Mock only external services
    mock_payment = Mock()
    mock_payment.charge.return_value = {"id": "ch_123", "status": "succeeded"}

    processor = OrderProcessor(inventory=inventory, payment=mock_payment)
    order = Order(item_id="item_1", quantity=1)
    result = processor.process(order)

    assert result["success"] is True
    assert inventory.get_stock("item_1") == 9  # Real side effect verified
```

**Solution:** Run tests with real implementations first to understand behavior. Then mock at the appropriate level - external services, not internal logic.

---

### Anti-Pattern 4: Incomplete Mocks

**The Problem:** Partial mock responses missing downstream fields that production code expects.

```python
# BAD: Incomplete mock response
mock_api = Mock()
mock_api.get_user.return_value = {
    "id": 1,
    "name": "Test User",
    # Missing: email, created_at, permissions, settings...
}

# Test passes, but production crashes accessing user["email"]
```

```python
# GOOD: Complete mock matching real API response
mock_api = Mock()
mock_api.get_user.return_value = {
    "id": 1,
    "name": "Test User",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "permissions": ["read", "write"],
    "settings": {
        "theme": "light",
        "notifications": True,
    },
}

# Or use a factory
from tests.factories import UserFactory

mock_api.get_user.return_value = UserFactory.build_response(name="Test User")
```

```python
# Factory for consistent mock data
class UserResponseFactory:
    """Generate complete API response objects."""
    _defaults = {
        "id": 1,
        "name": "Default User",
        "email": "default@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "permissions": ["read"],
        "settings": {"theme": "light", "notifications": True},
    }

    @classmethod
    def build(cls, **overrides) -> dict:
        return {**cls._defaults, **overrides}

# Usage
mock_api.get_user.return_value = UserResponseFactory.build(name="Alice")
```

**Solution:** Mirror complete real API response structure. Use factories to generate complete mock objects with sensible defaults.

---

### Anti-Pattern 5: Integration Tests as Afterthought

**The Problem:** Treating testing as optional follow-up work rather than integral to development.

```python
# BAD: "We'll add tests later"
# Day 1: Write 500 lines of code
# Day 2: Write 500 more lines
# Day 3: "We need to ship, tests can wait"
# Day 30: Catastrophic bug in production
# Day 31: "Why didn't we have tests?"
```

```python
# GOOD: Tests are part of implementation
# Write failing test
def test_rejects_duplicate_usernames(db_session):
    repo = UserRepository(db_session)
    repo.create(username="alice", email="alice@example.com")

    with pytest.raises(DuplicateUsernameError, match="Username already exists"):
        repo.create(username="alice", email="other@example.com")


# Make it pass
class UserRepository:
    def create(self, username: str, email: str) -> User:
        existing = self.session.query(User).filter_by(username=username).first()
        if existing:
            raise DuplicateUsernameError("Username already exists")
        user = User(username=username, email=email)
        self.session.add(user)
        self.session.commit()
        return user

# Feature AND test ship together
```

**Solution:** Follow TDD - testing is implementation, not documentation. No feature is "done" without tests.

---

## Detection Checklist

Review your tests for these warning signs:

| Warning Sign | Anti-Pattern |
|-------------|--------------|
| `mock.assert_called_with()` without testing output | Testing mock behavior |
| Methods starting with `_` or `for_testing` in production | Test-only methods |
| Every dependency is mocked with `@patch` | Mocking without understanding |
| Mocks return `{"success": True}` only | Incomplete mocks |
| Test files added weeks after feature ships | Tests as afterthought |

---

## Quick Reference

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Testing mocks | Only mock assertions, no behavior tests | Assert on actual output |
| Test-only methods | `_reset()`, `_set_for_test()` in prod | Use fresh `@pytest.fixture` instances |
| Over-mocking | 10+ `@patch` decorators per test | Test with real deps first |
| Incomplete mocks | Minimal stub responses | Use factories, match reality |
| Tests as afterthought | Features ship untested | TDD from the start |

---

*Content adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent (@obra), MIT License.*
