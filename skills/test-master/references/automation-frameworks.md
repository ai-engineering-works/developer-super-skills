# Automation Frameworks

## Page Object Pattern (Playwright for Python)

```python
from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects."""
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str):
        self.page.goto(path)
        return self


class LoginPage(BasePage):
    @property
    def email_input(self):
        return self.page.get_by_label("Email")

    @property
    def password_input(self):
        return self.page.get_by_label("Password")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Login")

    @property
    def error_message(self):
        return self.page.get_by_test_id("login-error")

    def goto(self):
        self.navigate("/login")
        return self

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
        return self

    def expect_error(self, message: str):
        expect(self.error_message).to_have_text(message)

    def expect_redirect_to_dashboard(self):
        expect(self.page).to_have_url(r".*dashboard")


class ProductsPage(BasePage):
    def goto(self):
        self.navigate("/products")
        return self

    def search(self, query: str):
        self.page.get_by_placeholder("Search products").fill(query)
        self.page.get_by_role("button", name="Search").click()
        return self

    def get_product_cards(self):
        return self.page.get_by_test_id("product-card")

    def click_product(self, name: str):
        self.page.get_by_role("link", name=name).click()
        return ProductDetailPage(self.page)


class ProductDetailPage(BasePage):
    def add_to_cart(self):
        self.page.get_by_role("button", name="Add to Cart").click()
        return self

    def expect_in_cart(self, count: int):
        expect(self.page.get_by_test_id("cart-count")).to_have_text(str(count))


# Usage in tests
def test_search_and_add_to_cart(page: Page):
    products = ProductsPage(page).goto()
    products.search("Widget")

    detail = products.click_product("Premium Widget")
    detail.add_to_cart()
    detail.expect_in_cart(1)
```

## Screenplay Pattern

```python
from playwright.sync_api import Page
from dataclasses import dataclass
from typing import Protocol


class Task(Protocol):
    def perform_as(self, actor: "Actor") -> None: ...


class Question(Protocol):
    def answered_by(self, actor: "Actor"): ...


class Actor:
    def __init__(self, page: Page):
        self.page = page

    def attempts_to(self, *tasks: Task):
        for task in tasks:
            task.perform_as(self)
        return self

    def asks(self, question: Question):
        return question.answered_by(self)


@dataclass
class Login:
    email: str
    password: str

    def perform_as(self, actor: Actor):
        actor.page.goto("/login")
        actor.page.get_by_label("Email").fill(self.email)
        actor.page.get_by_label("Password").fill(self.password)
        actor.page.get_by_role("button", name="Login").click()


@dataclass
class AddToCart:
    product_id: str

    def perform_as(self, actor: Actor):
        actor.page.goto(f"/products/{self.product_id}")
        actor.page.get_by_role("button", name="Add to Cart").click()


@dataclass
class CartTotal:
    def answered_by(self, actor: Actor) -> str:
        actor.page.goto("/cart")
        return actor.page.get_by_test_id("cart-total").text_content()


# Clear, maintainable test code
def test_user_adds_product_to_cart(page: Page):
    user = Actor(page)
    user.attempts_to(
        Login("user@test.com", "password"),
        AddToCart("prod_123"),
    )
    total = user.asks(CartTotal())
    assert total == "$29.99"
```

## Keyword-Driven Testing

```python
from playwright.sync_api import Page, expect
from typing import Any


class KeywordEngine:
    """Execute tests from keyword-driven data."""
    def __init__(self, page: Page):
        self.page = page
        self.keywords = {
            "navigate": self._navigate,
            "click": self._click,
            "fill": self._fill,
            "verify_visible": self._verify_visible,
            "verify_url": self._verify_url,
        }

    def _navigate(self, url: str):
        self.page.goto(url)

    def _click(self, role: str, name: str):
        self.page.get_by_role(role, name=name).click()

    def _fill(self, label: str, value: str):
        self.page.get_by_label(label).fill(value)

    def _verify_visible(self, text: str):
        expect(self.page.get_by_text(text)).to_be_visible()

    def _verify_url(self, pattern: str):
        expect(self.page).to_have_url(pattern)

    def execute(self, steps: list[dict[str, Any]]):
        for step in steps:
            keyword = step["keyword"]
            args = step.get("args", [])
            self.keywords[keyword](*args)


# Data drives execution - ideal for non-technical authors
LOGIN_STEPS = [
    {"keyword": "navigate", "args": ["/login"]},
    {"keyword": "fill", "args": ["Email", "user@test.com"]},
    {"keyword": "fill", "args": ["Password", "SecurePass123!"]},
    {"keyword": "click", "args": ["button", "Login"]},
    {"keyword": "verify_url", "args": [r".*dashboard"]},
]


def test_login_via_keywords(page: Page):
    engine = KeywordEngine(page)
    engine.execute(LOGIN_STEPS)
```

## Self-Healing Locators

```python
from playwright.sync_api import Page, Locator


def find_element(page: Page, strategies: list[str]) -> Locator:
    """Multi-strategy finder with automatic fallback."""
    for selector in strategies:
        locator = page.locator(selector)
        if locator.count() > 0:
            return locator
    raise ValueError(f"Element not found with strategies: {strategies}")


# Usage: tries best -> good -> fallback
def test_submit_with_resilient_locator(page: Page):
    page.goto("/form")

    submit = find_element(page, [
        '[data-testid="submit"]',        # Best: stable test ID
        'button:has-text("Submit")',      # Good: semantic
        "button.primary",                 # Fallback: CSS
    ])
    submit.click()
```

## Retry and Error Recovery

```python
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


def click_with_recovery(page: Page, selector: str, retries: int = 3):
    """Auto-retry with page reload on failure."""
    for attempt in range(retries):
        try:
            page.click(selector, timeout=5000)
            return
        except PlaywrightTimeout:
            if attempt == retries - 1:
                raise
            page.reload()
            page.wait_for_load_state("networkidle")


def retry_with_backoff(fn, retries: int = 3):
    """Exponential backoff for flaky operations."""
    for attempt in range(retries):
        try:
            return fn()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## Parallel and Distributed Execution

```ini
# pytest.ini
[pytest]
addopts = -n auto --dist loadscope

# -n auto: use all CPU cores (pytest-xdist)
# --dist loadscope: group tests by module for isolation
```

```yaml
# GitHub Actions: distribute across 4 shards
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements-test.txt
      - run: playwright install --with-deps

      - run: pytest tests/e2e/ --shard ${{ matrix.shard }}/4
        env:
          CI: true

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: report-${{ matrix.shard }}
          path: test-results/
```

## Test Data Factories

```python
import factory
from faker import Faker
from app.models import User, Product, Order

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyFunction(fake.email)
    name = factory.LazyFunction(fake.name)
    role = "user"


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.word)
    price = factory.LazyFunction(lambda: round(fake.pyfloat(min_value=1, max_value=999), 2))


# Seed via API in E2E tests
def seed_test_data(page):
    users = [{"email": u.email, "name": u.name} for u in UserFactory.build_batch(10)]
    page.request.post("/api/test/seed", data={"users": users})
```

## Custom pytest Reporter

```python
# conftest.py
import pytest
import json
from datetime import datetime


class MetricsCollector:
    def __init__(self):
        self.results = []

    def add(self, name: str, duration: float, status: str, retries: int = 0):
        self.results.append({
            "name": name,
            "duration_ms": round(duration * 1000, 2),
            "status": status,
            "retries": retries,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def save(self, path: str = "test-metrics.json"):
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)


@pytest.fixture(scope="session")
def metrics():
    collector = MetricsCollector()
    yield collector
    collector.save()
```

## Automation Strategy

### ROI Calculation

```python
def calculate_automation_roi(
    manual_time_per_run_min: int,
    runs_per_sprint: int,
    automation_dev_hours: int,
    maintenance_hours_per_sprint: float,
) -> dict:
    time_saved_per_sprint = (manual_time_per_run_min * runs_per_sprint) / 60
    net_savings_per_sprint = time_saved_per_sprint - maintenance_hours_per_sprint
    break_even_sprints = automation_dev_hours / net_savings_per_sprint if net_savings_per_sprint > 0 else float("inf")
    annual_savings = net_savings_per_sprint * 26 - automation_dev_hours

    return {
        "break_even_sprints": round(break_even_sprints, 1),
        "annual_savings_hours": round(annual_savings, 1),
        "roi_percent": round((annual_savings / automation_dev_hours) * 100, 1) if automation_dev_hours > 0 else 0,
    }

# Example: 30min manual test, 10 runs/sprint, 16h to automate, 1h maintenance
# Result: Break-even in ~4 sprints, save ~100 hours/year
```

## Quick Reference

| Pattern | Best For | Complexity |
|---------|----------|-----------|
| Page Object | Reusable components | Medium |
| Screenplay | Complex workflows | High |
| Keyword-Driven | Non-tech testers | Low |
| Self-Healing | Unstable UIs | Medium |

| Scaling | Use Case |
|---------|----------|
| pytest-xdist (`-n auto`) | Parallel on one machine |
| Sharding (CI matrix) | Distribute across runners |
| `--dist loadscope` | Group by module |

| Tool | Category |
|------|----------|
| Playwright (pytest) | Web E2E |
| Locust | Load/Performance |
| pytest + httpx | API Integration |
| factory_boy | Test data |
