---
name: test-master
description: Generates test files for Python CLI batch-processing applications that use Polars and Dask to load large CSV/Parquet files, perform DataFrame joins and enrichment lookups, and produce output files. Use when writing unit tests for data transformations; testing argparse CLI invocation; validating DataFrame joins, enrichment, and aggregation logic; testing large-file handling and memory efficiency; verifying output file correctness; building data-quality checks; or working on batch-pipeline CI/CD, test fixtures for tabular data, and data-pipeline regression testing.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "2.0.0"
  domain: quality
  triggers: test, testing, pytest, polars, dask, batch job, CLI, argparse, CSV, parquet, dataframe, join, lookup, enrichment, data pipeline, ETL, data quality, large files, coverage, regression, test fixtures, data validation
  role: specialist
  scope: testing
  output-format: code
  related-skills: fullstack-guardian, devops-engineer
---

# Test Master

Testing specialist for Python CLI batch-processing applications that use Polars and Dask to load, join, enrich, and output large tabular datasets.

## Core Workflow

1. **Define scope** — Identify which pipeline stages need tests (ingestion, transformation, join/enrichment, output)
2. **Create fixtures** — Build small, representative CSV/Parquet test data that exercises happy paths and edge cases
3. **Write tests** — Implement tests for each stage with concrete DataFrame assertions (see example below)
4. **Execute** — Run tests with `pytest`; verify output files match expected schemas and row counts
   - If tests fail: check column names, dtypes, join keys, and null handling first
   - If tests are flaky: isolate file-system state; use `tmp_path` fixtures for all I/O
5. **Report** — Document coverage gaps, data-quality findings, and performance baselines

## Quick-Start Example

A minimal pytest test for a Polars enrichment join:

```python
import polars as pl
from app.transforms import enrich_orders_with_customers


def test_enrich_orders_adds_customer_name():
    orders = pl.DataFrame({
        "order_id": [1, 2, 3],
        "customer_id": [101, 102, 101],
        "amount": [50.0, 75.0, 120.0],
    })
    customers = pl.DataFrame({
        "customer_id": [101, 102],
        "name": ["Alice", "Bob"],
    })

    result = enrich_orders_with_customers(orders, customers)

    assert result.columns == ["order_id", "customer_id", "amount", "name"]
    assert result["name"].to_list() == ["Alice", "Bob", "Alice"]
    assert result.shape == (3, 4)
```

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Unit Testing | `references/unit-testing.md` | Testing Polars/Dask transforms, joins, enrichment |
| Integration | `references/integration-testing.md` | argparse CLI invocation, file I/O, subprocess |
| E2E Pipeline | `references/e2e-testing.md` | Full pipeline: input files to output files |
| Performance | `references/performance-testing.md` | Large file handling, memory, Dask scaling |
| Data Quality | `references/security-testing.md` | Schema validation, null checks, dedup, data integrity |
| Reports | `references/test-reports.md` | Pipeline test reports, data-quality reports |
| QA Methodology | `references/qa-methodology.md` | Data pipeline QA, regression strategy, coverage |
| Test Fixtures | `references/automation-frameworks.md` | Generating test CSV/Parquet, factories, CI/CD |
| TDD Iron Laws | `references/tdd-iron-laws.md` | TDD with data transformation examples |
| Anti-Patterns | `references/testing-anti-patterns.md` | Data pipeline testing mistakes |

## Constraints

**MUST DO**
- Test joins with matching rows, non-matching rows, and duplicate keys
- Use `tmp_path` for all file I/O — never write to fixed paths
- Assert DataFrame schemas (column names + dtypes), not just row counts
- Test with empty DataFrames, single-row inputs, and null values
- Verify output files are valid CSV/Parquet with expected schemas

**MUST NOT**
- Use production data in tests — generate synthetic fixtures
- Rely on file ordering — sort results before comparison
- Skip null/missing-key handling — batch jobs encounter dirty data
- Create tests that depend on working directory or absolute paths
- Test only the happy path — test missing files, bad schemas, corrupt data

## Output Templates

When creating test plans for batch pipelines, provide:
1. Pipeline stages and data flow diagram
2. Test cases per stage (ingestion, transform, join, output)
3. Edge cases: nulls, duplicates, missing keys, empty files, schema drift
4. Coverage analysis of transformation logic
5. Performance baselines (file size, memory, wall-clock time)
