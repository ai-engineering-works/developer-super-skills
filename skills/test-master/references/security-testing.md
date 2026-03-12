# Data Quality & Validation Testing

## Schema Validation

```python
import pytest
import polars as pl
from app.validation import validate_schema, SchemaError


class TestSchemaValidation:
    """Verify input data matches expected schema before processing."""

    def test_valid_schema_passes(self):
        df = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 103],
            "amount": [50.0, 75.0, 120.0],
        })
        expected_schema = {
            "order_id": pl.Int64,
            "customer_id": pl.Int64,
            "amount": pl.Float64,
        }

        # Should not raise
        validate_schema(df, expected_schema)

    def test_missing_column_raises(self):
        df = pl.DataFrame({"order_id": [1], "amount": [50.0]})
        expected_schema = {
            "order_id": pl.Int64,
            "customer_id": pl.Int64,
            "amount": pl.Float64,
        }

        with pytest.raises(SchemaError, match="customer_id"):
            validate_schema(df, expected_schema)

    def test_wrong_dtype_raises(self):
        df = pl.DataFrame({
            "order_id": ["one", "two"],  # String instead of Int
            "amount": [50.0, 75.0],
        })
        expected_schema = {"order_id": pl.Int64, "amount": pl.Float64}

        with pytest.raises(SchemaError, match="order_id.*expected Int64.*got Utf8"):
            validate_schema(df, expected_schema)

    def test_extra_columns_are_tolerated(self):
        df = pl.DataFrame({
            "order_id": [1],
            "amount": [50.0],
            "extra_col": ["ignored"],
        })
        expected_schema = {"order_id": pl.Int64, "amount": pl.Float64}

        # Extra columns should not cause an error
        validate_schema(df, expected_schema)

    def test_empty_dataframe_with_correct_schema_passes(self):
        df = pl.DataFrame({
            "order_id": pl.Series([], dtype=pl.Int64),
            "amount": pl.Series([], dtype=pl.Float64),
        })
        expected_schema = {"order_id": pl.Int64, "amount": pl.Float64}

        validate_schema(df, expected_schema)
```

## Null and Completeness Checks

```python
import polars as pl
import pytest


class TestNullHandling:
    """Verify pipeline handles nulls correctly."""

    def test_required_columns_have_no_nulls(self):
        df = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, None, 103],
            "amount": [50.0, 75.0, 120.0],
        })

        required_cols = ["order_id", "amount"]
        for col in required_cols:
            null_count = df[col].null_count()
            assert null_count == 0, f"{col} has {null_count} null values"

    def test_nullable_columns_are_documented(self):
        """After left join, enrichment columns may have nulls."""
        from app.transforms import enrich_orders_with_customers

        orders = pl.DataFrame({
            "order_id": [1, 2],
            "customer_id": [101, 999],  # 999 not in customers
            "amount": [50.0, 75.0],
        })
        customers = pl.DataFrame({
            "customer_id": [101],
            "name": ["Alice"],
        })

        result = enrich_orders_with_customers(orders, customers)

        # name is nullable after left join
        assert result["name"].null_count() == 1
        # order_id should never be null
        assert result["order_id"].null_count() == 0

    def test_null_percentage_within_threshold(self):
        """Flag columns with excessive nulls."""
        df = pl.DataFrame({
            "id": list(range(100)),
            "value": [None if i % 5 == 0 else float(i) for i in range(100)],
        })

        null_pct = df["value"].null_count() / df.shape[0] * 100
        assert null_pct < 25, f"Column 'value' is {null_pct:.1f}% null (threshold: 25%)"

    @pytest.mark.parametrize("col", ["order_id", "customer_id", "amount"])
    def test_primary_columns_are_complete(self, col):
        from app.io import read_input_file

        # Simulate reading a real file
        df = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 103],
            "amount": [50.0, 75.0, 120.0],
        })

        assert df[col].null_count() == 0, f"Required column '{col}' contains nulls"
```

## Duplicate Detection

```python
import polars as pl
import pytest


class TestDuplicateDetection:

    def test_no_duplicate_primary_keys(self):
        df = pl.DataFrame({
            "order_id": [1, 2, 3, 2],  # duplicate!
            "amount": [50.0, 75.0, 120.0, 75.0],
        })

        dup_count = df.shape[0] - df.select("order_id").unique().shape[0]
        assert dup_count == 0, f"Found {dup_count} duplicate order_id values"

    def test_deduplicate_preserves_first_occurrence(self):
        from app.transforms import deduplicate_by_key

        df = pl.DataFrame({
            "order_id": [1, 2, 2, 3],
            "amount": [50.0, 75.0, 80.0, 120.0],
            "timestamp": [1, 2, 3, 4],
        })

        result = deduplicate_by_key(df, key="order_id", sort_by="timestamp")

        assert result.shape[0] == 3
        # Should keep earliest timestamp for id=2
        row = result.filter(pl.col("order_id") == 2)
        assert row["amount"].to_list() == [75.0]

    def test_lookup_table_has_unique_keys(self):
        customers = pl.DataFrame({
            "customer_id": [101, 102, 103, 101],  # duplicate!
            "name": ["Alice", "Bob", "Carol", "Alice-2"],
        })

        unique_count = customers.select("customer_id").unique().shape[0]
        assert unique_count == customers.shape[0], (
            f"Lookup table has {customers.shape[0] - unique_count} duplicate keys"
        )

    def test_full_row_duplicates_detected(self):
        df = pl.DataFrame({
            "id": [1, 2, 3, 2],
            "value": [10, 20, 30, 20],
        })

        original_count = df.shape[0]
        unique_count = df.unique().shape[0]
        dup_count = original_count - unique_count

        assert dup_count == 0, f"Found {dup_count} exact duplicate rows"
```

## Data Range and Business Rule Validation

```python
import polars as pl
import pytest


class TestBusinessRules:
    """Validate data against business constraints."""

    def test_amounts_are_positive(self):
        df = pl.DataFrame({"amount": [50.0, -10.0, 75.0, 0.0]})

        negatives = df.filter(pl.col("amount") < 0)
        assert negatives.shape[0] == 0, (
            f"Found {negatives.shape[0]} negative amounts: {negatives['amount'].to_list()}"
        )

    def test_quantities_are_integers_above_zero(self):
        df = pl.DataFrame({"quantity": [1, 2, 0, 5]})

        invalid = df.filter(pl.col("quantity") <= 0)
        assert invalid.shape[0] == 0, f"Found {invalid.shape[0]} non-positive quantities"

    def test_dates_are_within_expected_range(self):
        from datetime import date

        df = pl.DataFrame({
            "order_date": ["2024-01-01", "2024-06-15", "2020-01-01", "2024-12-31"],
        }).with_columns(pl.col("order_date").str.to_date())

        min_date = date(2024, 1, 1)
        max_date = date(2024, 12, 31)

        out_of_range = df.filter(
            (pl.col("order_date") < min_date) | (pl.col("order_date") > max_date)
        )
        assert out_of_range.shape[0] == 0, (
            f"Found {out_of_range.shape[0]} dates outside {min_date} to {max_date}"
        )

    def test_customer_tiers_are_valid(self):
        valid_tiers = {"standard", "premium", "enterprise"}
        df = pl.DataFrame({"tier": ["standard", "premium", "invalid", "enterprise"]})

        invalid = df.filter(~pl.col("tier").is_in(list(valid_tiers)))
        assert invalid.shape[0] == 0, (
            f"Invalid tiers found: {invalid['tier'].to_list()}"
        )

    def test_email_format_is_valid(self):
        df = pl.DataFrame({
            "email": ["alice@example.com", "bob@test.com", "invalid", "carol@.com"],
        })

        invalid = df.filter(~pl.col("email").str.contains(r"^[^@]+@[^@]+\.[^@]+$"))
        assert invalid.shape[0] == 0, (
            f"Invalid emails: {invalid['email'].to_list()}"
        )
```

## Referential Integrity

```python
import polars as pl


class TestReferentialIntegrity:
    """Verify join keys exist in lookup tables."""

    def test_all_customer_ids_exist_in_lookup(self):
        orders = pl.DataFrame({"customer_id": [101, 102, 103, 999]})
        customers = pl.DataFrame({"customer_id": [101, 102, 103]})

        order_ids = set(orders["customer_id"].to_list())
        customer_ids = set(customers["customer_id"].to_list())
        orphans = order_ids - customer_ids

        assert len(orphans) == 0, f"Orphan customer_ids with no lookup entry: {orphans}"

    def test_enrichment_coverage_percentage(self):
        """Track what percentage of rows get enriched."""
        from app.transforms import enrich_orders_with_customers

        orders = pl.DataFrame({
            "order_id": list(range(100)),
            "customer_id": [i % 12 for i in range(100)],  # ids 0-11
            "amount": [10.0] * 100,
        })
        customers = pl.DataFrame({
            "customer_id": list(range(1, 11)),  # ids 1-10, missing 0 and 11
            "name": [f"Customer_{i}" for i in range(1, 11)],
        })

        result = enrich_orders_with_customers(orders, customers)

        enriched_count = result.filter(pl.col("name").is_not_null()).shape[0]
        coverage = enriched_count / result.shape[0] * 100

        assert coverage > 80, f"Enrichment coverage: {coverage:.1f}% (threshold: 80%)"

    def test_no_fan_out_from_join(self):
        """Join should not create more rows than the main table."""
        orders = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 103],
        })
        customers = pl.DataFrame({
            "customer_id": [101, 102, 103],
            "name": ["Alice", "Bob", "Carol"],
        })

        from app.transforms import enrich_orders_with_customers
        result = enrich_orders_with_customers(orders, customers)

        assert result.shape[0] == orders.shape[0], (
            f"Row fan-out: input={orders.shape[0]}, output={result.shape[0]}"
        )
```

## Data Quality Report

```python
import polars as pl
from dataclasses import dataclass, field


@dataclass
class DataQualityReport:
    total_rows: int = 0
    null_counts: dict = field(default_factory=dict)
    duplicate_keys: int = 0
    schema_errors: list = field(default_factory=list)
    business_rule_violations: list = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return (
            self.duplicate_keys == 0
            and len(self.schema_errors) == 0
            and len(self.business_rule_violations) == 0
        )


def assess_quality(df: pl.DataFrame, primary_key: str) -> DataQualityReport:
    report = DataQualityReport(total_rows=df.shape[0])

    # Null analysis
    for col in df.columns:
        null_count = df[col].null_count()
        if null_count > 0:
            report.null_counts[col] = null_count

    # Duplicate check
    report.duplicate_keys = df.shape[0] - df.select(primary_key).unique().shape[0]

    return report


# Usage in tests
def test_input_data_quality():
    df = pl.DataFrame({
        "order_id": [1, 2, 3],
        "amount": [50.0, None, 120.0],
    })

    report = assess_quality(df, primary_key="order_id")

    assert report.is_clean, f"Quality issues: nulls={report.null_counts}, dups={report.duplicate_keys}"
```

## Quick Reference

| Check | What It Catches |
|-------|----------------|
| Schema validation | Missing columns, wrong dtypes |
| Null checks | Unexpected nulls in required fields |
| Duplicate detection | Duplicate primary keys, full-row dupes |
| Range validation | Negative amounts, future dates, invalid enums |
| Referential integrity | Orphan foreign keys, missing lookup entries |
| Fan-out detection | Joins creating more rows than expected |
| Completeness | Coverage percentage of enrichment |
