# QA Methodology

## Manual Testing Types

### Exploratory Testing
```markdown
**Charter**: Explore {feature} with focus on {aspect}
**Duration**: 60-90 min
**Mission**: Find defects in {specific functionality}

Test Ideas:
- Boundary conditions & edge cases
- Error handling & recovery
- User workflow variations
- Integration points

Findings:
1. [HIGH] {Issue + impact}
2. [MED] {Issue + impact}

Coverage: {Areas explored} | Risks: {Identified risks}
```

### Usability Testing
```markdown
**Task**: Can users complete {action} intuitively?
**Metrics**: Time to complete, errors made, satisfaction (1-5)
**Success**: 80% complete without help in <5 min

Observations:
- Navigation confusing at {step}
- Users expect {A} but get {B}
- Positive: {feature feedback}
```

### Accessibility Testing (WCAG 2.1 AA)

```python
from playwright.sync_api import Page, expect


def test_keyboard_navigation(page: Page):
    page.goto("/")
    page.keyboard.press("Tab")

    active_tag = page.evaluate("document.activeElement?.tagName")
    assert active_tag in ("A", "BUTTON", "INPUT"), f"Unexpected focus on {active_tag}"


def test_buttons_have_aria_labels(page: Page):
    page.goto("/")
    buttons = page.get_by_role("button").all()

    for button in buttons:
        text = button.text_content() or ""
        aria_label = button.get_attribute("aria-label") or ""
        assert text.strip() or aria_label.strip(), "Button has no accessible name"


def test_no_accessibility_violations(page: Page):
    """Run axe-core accessibility audit."""
    page.goto("/")

    # Inject and run axe-core
    violations = page.evaluate("""
        async () => {
            await new Promise(r => {
                const s = document.createElement('script');
                s.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js';
                s.onload = r;
                document.head.appendChild(s);
            });
            const results = await axe.run();
            return results.violations;
        }
    """)
    assert len(violations) == 0, f"Accessibility violations: {violations}"


def test_images_have_alt_text(page: Page):
    page.goto("/")
    images = page.locator("img").all()

    for img in images:
        alt = img.get_attribute("alt")
        assert alt is not None and alt.strip(), "Image missing alt text"
```

### Localization Testing
```markdown
**Test**: {Feature} in {language/locale}
- [ ] Text displays without truncation
- [ ] Date/time/currency formats correct
- [ ] Right-to-left layout (Arabic, Hebrew)
- [ ] Character encoding UTF-8
- [ ] Sort order respects locale
```

### Compatibility Matrix
```markdown
| Browser | Version | OS | Status |
|---------|---------|----|----- --|
| Chrome | Latest | Win/Mac | Pass |
| Firefox | Latest | Win/Mac | Pass |
| Safari | Latest | macOS/iOS | Pass |
| Edge | Latest | Windows | Pass |
```

## Test Design Techniques

### Pairwise Testing

```python
import pytest
from itertools import product


# Generate pairwise combinations efficiently
BROWSERS = ["chrome", "firefox", "safari"]
OS_LIST = ["windows", "mac", "linux"]
LANGUAGES = ["en", "es", "fr"]


# Pairwise subset covering all pairs with minimal tests
PAIRWISE_TESTS = [
    {"browser": "chrome", "os": "windows", "lang": "en"},
    {"browser": "firefox", "os": "mac", "lang": "es"},
    {"browser": "safari", "os": "linux", "lang": "fr"},
    {"browser": "chrome", "os": "mac", "lang": "fr"},
    {"browser": "firefox", "os": "linux", "lang": "en"},
    {"browser": "safari", "os": "windows", "lang": "es"},
]


@pytest.mark.parametrize("config", PAIRWISE_TESTS, ids=lambda c: f"{c['browser']}-{c['os']}-{c['lang']}")
def test_compatibility(config):
    """Run tests across pairwise parameter combinations."""
    assert config["browser"] in BROWSERS
    # ... actual test logic
```

### Risk-Based Testing
```markdown
| Risk | Probability | Impact | Priority | Test Effort |
|------|-------------|--------|----------|-------------|
| Critical | High | High | P0 | Exhaustive |
| High | Med-High | High | P1 | Comprehensive |
| Medium | Low-Med | Med | P2 | Standard |
| Low | Low | Low | P3 | Smoke only |
```

### Boundary Value Analysis

```python
import pytest


@pytest.mark.parametrize("age, expected_valid", [
    (-1, False),     # below minimum
    (0, True),       # minimum boundary
    (1, True),       # just above minimum
    (149, True),     # just below maximum
    (150, True),     # maximum boundary
    (151, False),    # above maximum
])
def test_age_validation_boundaries(age, expected_valid):
    result = validate_age(age)
    assert result == expected_valid


@pytest.mark.parametrize("length, expected_valid", [
    (0, False),      # empty
    (1, True),       # minimum
    (255, True),     # max boundary
    (256, False),    # over max
])
def test_username_length_boundaries(length, expected_valid):
    username = "a" * length
    assert validate_username(username) == expected_valid
```

## Defect Management

### Root Cause Analysis (5 Whys)
```markdown
1. Why did defect occur? {User input not validated}
2. Why wasn't it validated? {Validation logic missing}
3. Why was it missing? {Requirement unclear}
4. Why was requirement unclear? {Acceptance criteria incomplete}
5. Why incomplete? {No QA review in planning}

**Root Cause**: QA not involved in requirements phase
**Prevention**: Add QA to all planning meetings
```

### Defect Report Template
```markdown
## [CRITICAL] {Defect Title}

**Steps to Reproduce**:
1. {Step 1}
2. {Step 2}

**Expected**: {Should happen}
**Actual**: {Actually happens}
**Impact**: {Business/user impact}
**Root Cause**: {Why it happened}
**Fix**: {Recommended solution}
```

## Quality Metrics

### Key Calculations

```python
def calculate_quality_metrics(
    defects_in_testing: int,
    defects_in_prod: int,
    defects_found_by_tests: int,
) -> dict:
    total_defects = defects_in_testing + defects_in_prod

    # Defect Removal Efficiency (target: >95%)
    dre = (defects_in_testing / total_defects * 100) if total_defects > 0 else 100

    # Defect Leakage (target: <5%)
    leakage = (defects_in_prod / total_defects * 100) if total_defects > 0 else 0

    # Test Effectiveness (target: >90%)
    effectiveness = (defects_found_by_tests / total_defects * 100) if total_defects > 0 else 100

    return {
        "dre": round(dre, 1),
        "leakage": round(leakage, 1),
        "effectiveness": round(effectiveness, 1),
    }


def calculate_automation_roi(
    time_saved_hours: float,
    maintenance_cost_hours: float,
    development_cost_hours: float,
) -> float:
    return (time_saved_hours - maintenance_cost_hours - development_cost_hours) / development_cost_hours
```

### Quality Dashboard
```markdown
| Metric | Target | Actual | Trend | Status |
|--------|--------|--------|-------|--------|
| Coverage | >80% | 87% | Up | Pass |
| Defect Leakage | <5% | 3% | Down | Pass |
| Automation | >70% | 68% | Up | Warn |
| Critical Defects | 0 | 0 | Steady | Pass |
| MTTR | <48h | 36h | Down | Pass |
```

## Continuous Testing & Shift-Left

### Shift-Left Activities
```markdown
**Early Testing**:
- Review requirements for testability
- Create test cases during design
- TDD: unit tests with code
- Automated tests in CI pipeline
- Static analysis on commit
- Security scanning pre-merge

**Benefits**: 10x cheaper defect fixes, faster feedback
```

### Feedback Cycle Targets

```python
FEEDBACK_TARGETS = {
    "unit_tests": "< 5 min",       # On save
    "integration": "< 15 min",     # On commit
    "e2e": "< 30 min",             # On PR
    "regression": "< 2 hours",     # Nightly
}
```

## Quality Advocacy

### Quality Gates
```markdown
## Production Release Gate

**Must Pass (Blockers)**:
- [ ] Zero critical defects
- [ ] Coverage >80%
- [ ] All P0/P1 tests passing
- [ ] Performance SLA met
- [ ] Security scan clean
- [ ] Accessibility WCAG AA

**Decision**: GO | NO-GO | GO with exceptions
```

## Test Planning

### Test Plan Template
```markdown
## Test Plan: {Feature}

**Scope**: {What to test}
**Types**: Unit, Integration, E2E, Perf, Security
**Resources**: {Team allocation}
**Dependencies**: {Prerequisites}
**Schedule**: {Timeline}
**Entry Criteria**: {Start conditions}
**Exit Criteria**: {Completion conditions}
**Risks**: {Identified risks + mitigation}
```

### Environment Strategy
```markdown
| Env | Purpose | Data | Refresh | Access |
|-----|---------|------|---------|--------|
| Dev | Development | Synthetic | On-demand | All |
| Test | QA testing | Test data | Daily | QA |
| Stage | Pre-prod | Prod-like | Weekly | Limited |
| Prod | Live | Real | N/A | Ops |
```

## Quick Reference

| Testing Type | When | Duration |
|--------------|------|----------|
| Exploratory | New features | 60-120 min |
| Usability | UI changes | 2-4 hours |
| Accessibility | Every release | 1-2 hours |
| Localization | Multi-region | 1 day/locale |

| Metric | Excellent | Good | Needs Work |
|--------|-----------|------|------------|
| Coverage | >90% | 70-90% | <70% |
| Leakage | <2% | 2-5% | >5% |
| Automation | >80% | 60-80% | <60% |
| MTTR | <24h | 24-48h | >48h |
