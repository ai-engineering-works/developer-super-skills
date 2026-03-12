# Test Reports

## Test Report Template

```markdown
# Test Report: {Feature Name}

**Date**: YYYY-MM-DD
**Tester**: {Name}
**Version**: {App Version}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | X |
| Passed | X |
| Failed | X |
| Skipped | X |
| Coverage | X% |

## Test Scope

- [x] Unit tests (pytest)
- [x] Integration tests (httpx)
- [x] E2E tests (Playwright)
- [ ] Performance tests (Locust)
- [ ] Security tests

## Findings

### [CRITICAL] {Issue Title}
- **Location**: src/api/users.py:45
- **Steps to Reproduce**:
  1. Send POST to /api/users without auth
  2. Request succeeds with 201
- **Expected**: 401 Unauthorized
- **Actual**: 201 Created
- **Impact**: Unauthorized user creation
- **Fix**: Add auth middleware

### [HIGH] {Issue Title}
- **Location**: src/services/orders.py:123
- **Description**: N+1 query in order list
- **Impact**: 3s response time with 100 orders
- **Fix**: Add eager loading with `joinedload()`

### [MEDIUM] {Issue Title}
- **Details**: ...

### [LOW] {Issue Title}
- **Details**: ...

## Coverage Analysis

| Module | Lines | Branches | Functions |
|--------|-------|----------|-----------|
| api/ | 85% | 78% | 90% |
| services/ | 92% | 85% | 95% |
| utils/ | 100% | 100% | 100% |

### Coverage Gaps
- `src/api/admin.py` - 0% (no tests)
- `src/services/payment.py:45-60` - Error handling untested

## Recommendations

1. **Immediate**: Add auth middleware to admin routes
2. **High Priority**: Optimize order queries
3. **Medium Priority**: Add tests for payment error handling
4. **Low Priority**: Increase branch coverage in api/

## Performance Results

| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| GET /users | 45ms | 120ms | 250ms |
| POST /orders | 150ms | 400ms | 800ms |

## Sign-off

- [ ] All critical issues addressed
- [ ] Coverage meets threshold (80%)
- [ ] Performance meets SLA
```

## Generating Reports with pytest

```python
# pytest.ini or pyproject.toml
# [tool.pytest.ini_options]
# addopts = "--cov=app --cov-report=html --cov-report=term-missing --junitxml=report.xml"
```

```python
# conftest.py - Custom report generation
import pytest
import json
from datetime import datetime
from pathlib import Path


class TestReport:
    def __init__(self):
        self.results: list[dict] = []
        self.start_time = datetime.utcnow()

    def add_result(self, nodeid: str, outcome: str, duration: float, message: str = ""):
        self.results.append({
            "test": nodeid,
            "outcome": outcome,
            "duration_ms": round(duration * 1000, 2),
            "message": message,
        })

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["outcome"] == "passed")
        failed = sum(1 for r in self.results if r["outcome"] == "failed")
        skipped = sum(1 for r in self.results if r["outcome"] == "skipped")
        total_duration = sum(r["duration_ms"] for r in self.results)

        return {
            "date": self.start_time.isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "N/A",
            "total_duration_ms": round(total_duration, 2),
            "failures": [r for r in self.results if r["outcome"] == "failed"],
        }

    def save(self, path: str = "test-report.json"):
        report = {**self.summary(), "details": self.results}
        Path(path).write_text(json.dumps(report, indent=2))


@pytest.fixture(scope="session")
def test_report():
    report = TestReport()
    yield report
    report.save()
```

## Coverage Analysis Script

```python
# scripts/coverage_check.py
"""Check coverage meets thresholds and report gaps."""
import json
import sys
from pathlib import Path


def check_coverage(report_path: str = "coverage.json", threshold: float = 80.0) -> bool:
    data = json.loads(Path(report_path).read_text())
    totals = data["totals"]

    line_coverage = totals["percent_covered"]
    print(f"Line coverage: {line_coverage:.1f}% (threshold: {threshold}%)")

    # Find uncovered modules
    gaps = []
    for filepath, file_data in data["files"].items():
        file_coverage = file_data["summary"]["percent_covered"]
        if file_coverage < threshold:
            missing = file_data["summary"]["missing_lines"]
            gaps.append({
                "file": filepath,
                "coverage": f"{file_coverage:.1f}%",
                "missing_lines": missing,
            })

    if gaps:
        print(f"\nCoverage gaps ({len(gaps)} files below {threshold}%):")
        for gap in sorted(gaps, key=lambda g: float(g["coverage"].rstrip("%"))):
            print(f"  {gap['file']}: {gap['coverage']} ({gap['missing_lines']} lines uncovered)")

    return line_coverage >= threshold


if __name__ == "__main__":
    # Generate: pytest --cov=app --cov-report=json
    success = check_coverage()
    sys.exit(0 if success else 1)
```

## CI Report Integration

```yaml
# GitHub Actions - test reporting
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements-test.txt

      - name: Run tests with coverage
        run: |
          pytest \
            --cov=app \
            --cov-report=html \
            --cov-report=json \
            --cov-report=term-missing \
            --junitxml=junit-report.xml \
            -v

      - name: Check coverage threshold
        run: python scripts/coverage_check.py

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: htmlcov/

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: junit-report.xml
```

## Severity Definitions

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | Security vulnerability, data loss, system crash |
| **HIGH** | Major functionality broken, severe performance |
| **MEDIUM** | Feature partially working, workaround exists |
| **LOW** | Minor issue, cosmetic, edge case |

## Quick Reference

| Section | Content |
|---------|---------|
| Summary | High-level metrics |
| Findings | Issues by severity |
| Coverage | Code coverage analysis |
| Recommendations | Prioritized actions |
| Sign-off | Approval criteria |
