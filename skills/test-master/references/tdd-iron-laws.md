# TDD Iron Laws

---

## The Fundamental Principle

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

This is non-negotiable. If you wrote production code before writing a failing test, delete it and start over. No exceptions.

---

## The Three Iron Laws

### Iron Law 1: The Fundamental Rule

> "You shall not write any production code unless it is to make a failing test pass."

Every line of production code must have a corresponding test that:
1. Was written first
2. Was observed to fail
3. Now passes because of that code

### Iron Law 2: Proof Through Observation

> "If you didn't watch the test fail, you don't know if it tests the right thing."

Mandatory verification steps:
- Write the test
- Run it and **observe the failure**
- Verify the failure message is meaningful
- Only then implement the fix

A test you've never seen fail proves nothing.

### Iron Law 3: The Final Rule

> "Production code exists -> A test exists that failed first. Otherwise -> It's not TDD."

There is no middle ground. Code written without a prior failing test is not test-driven development, regardless of how many tests exist afterward.

---

## The RED-GREEN-REFACTOR Cycle

### RED: Write One Minimal Failing Test

```python
# Start with the smallest possible failing test
import polars as pl

def test_enrich_adds_customer_name():
    orders = pl.DataFrame({"order_id": [1], "customer_id": [101], "amount": [50.0]})
    customers = pl.DataFrame({"customer_id": [101], "name": ["Alice"]})

    result = enrich_orders(orders, customers)

    assert "name" in result.columns
    assert result["name"].to_list() == ["Alice"]
# Run: FAIL - NameError: name 'enrich_orders' is not defined
```

**Requirements:**
- One test at a time
- Minimal scope
- Clear failure message
- Observe the red

### GREEN: Implement Simplest Passing Code

```python
# Write only enough code to pass this specific test
import polars as pl

def enrich_orders(orders: pl.DataFrame, customers: pl.DataFrame) -> pl.DataFrame:
    return orders.join(customers, on="customer_id", how="left")
# Run: PASS
```

**Requirements:**
- Simplest possible implementation
- No extra features
- No optimization
- Just make it pass

### REFACTOR: Improve While Keeping Tests Green

```python
# Now improve the code while tests stay green
def enrich_orders(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    join_key: str = "customer_id",
) -> pl.DataFrame:
    return orders.join(
        customers.unique(subset=[join_key]),
        on=join_key,
        how="left",
    )
# Run: PASS (still)
```

**Requirements:**
- Tests must stay green
- Remove duplication
- Improve clarity
- No new functionality

---

## Common Rationalizations to Reject

| Rationalization | Why It's Wrong |
|-----------------|----------------|
| "I can manually check the CSV output" | Manual checks don't prevent regression |
| "I'll write tests after the pipeline works" | You'll skip edge cases (nulls, dupes, empty files) |
| "This join is too simple to test" | Join keys change; tests document expectations |
| "I've already written the transform, can't delete it" | Sunk cost fallacy; delete it |
| "The data is clean, no need to test nulls" | Production data is never as clean as you think |
| "We're in a hurry" | A wrong batch output costs more than TDD |

---

## Practical Application

### Building a Transform with TDD

```python
# 1. RED: Write failing test for simplest behavior
def test_normalize_column_names_lowercases():
    df = pl.DataFrame({"Order ID": [1], "Customer Name": ["Alice"]})
    result = normalize_columns(df)
    assert result.columns == ["order_id", "customer_name"]
# Run: FAIL - NameError

# 2. GREEN: Implement minimal passing code
def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename({col: col.lower().replace(" ", "_") for col in df.columns})
# Run: PASS

# 3. RED: Add next failing test
def test_normalize_handles_special_characters():
    df = pl.DataFrame({"Order (ID)": [1], "Amount ($)": [50.0]})
    result = normalize_columns(df)
    assert result.columns == ["order_id", "amount"]
# Run: FAIL - got ["order_(id)", "amount_($)"]

# 4. GREEN: Extend to pass both tests
import re

def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    def clean(name: str) -> str:
        name = name.lower().replace(" ", "_")
        name = re.sub(r"[^a-z0-9_]", "", name)
        return name.strip("_")
    return df.rename({col: clean(col) for col in df.columns})
# Run: PASS
```

### Building a Validation with TDD

```python
# 1. RED: Simplest validation
def test_validate_rejects_empty_dataframe():
    df = pl.DataFrame({"id": pl.Series([], dtype=pl.Int64)})
    with pytest.raises(ValueError, match="empty"):
        validate_input(df)

# 2. GREEN
def validate_input(df: pl.DataFrame) -> None:
    if df.shape[0] == 0:
        raise ValueError("Input DataFrame is empty")

# 3. RED: Next requirement
def test_validate_rejects_missing_required_columns():
    df = pl.DataFrame({"id": [1], "extra": [2]})
    with pytest.raises(ValueError, match="amount"):
        validate_input(df, required=["id", "amount"])

# 4. GREEN
def validate_input(
    df: pl.DataFrame,
    required: list[str] | None = None,
) -> None:
    if df.shape[0] == 0:
        raise ValueError("Input DataFrame is empty")
    if required:
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

# 5. RED: Add null check
def test_validate_rejects_nulls_in_required_columns():
    df = pl.DataFrame({"id": [1, None, 3], "amount": [10.0, 20.0, 30.0]})
    with pytest.raises(ValueError, match="null.*id"):
        validate_input(df, required=["id", "amount"], no_nulls=["id"])

# 6. GREEN
def validate_input(
    df: pl.DataFrame,
    required: list[str] | None = None,
    no_nulls: list[str] | None = None,
) -> None:
    if df.shape[0] == 0:
        raise ValueError("Input DataFrame is empty")
    if required:
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    if no_nulls:
        for col in no_nulls:
            if df[col].null_count() > 0:
                raise ValueError(f"Column '{col}' contains {df[col].null_count()} null values")
```

### Fixing a Bug in a Transform

```python
# 1. RED: Write test that exposes the bug
def test_enrich_handles_null_join_keys():
    orders = pl.DataFrame({
        "order_id": [1, 2],
        "customer_id": [101, None],
        "amount": [50.0, 75.0],
    })
    customers = pl.DataFrame({"customer_id": [101], "name": ["Alice"]})

    result = enrich_orders(orders, customers)
    assert result.shape[0] == 2  # Both rows preserved
    assert result.filter(pl.col("customer_id").is_null())["name"].to_list() == [None]
# Run: FAIL - rows with null key were dropped

# 2. GREEN: Fix the bug
def enrich_orders(orders, customers):
    return orders.join(customers, on="customer_id", how="left")
    # Changed from "inner" to "left" join
# Run: PASS

# Bug is now fixed AND protected against regression
```

---

## Verification Checklist

Before claiming any pipeline code is complete:

- [ ] Every transform function has corresponding tests
- [ ] Each test was written before its implementation
- [ ] Each test was observed to fail first
- [ ] Tests verify output DataFrames, not implementation details
- [ ] Refactoring kept all tests green
- [ ] Edge cases tested: empty input, nulls, duplicates, missing keys
- [ ] No production code exists without a test

---

*Content adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent (@obra), MIT License.*
