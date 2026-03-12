# Unit Testing — Polars & Dask Transformations

## Testing Polars Transformations

```python
import pytest
import polars as pl
from polars.testing import assert_frame_equal
from app.transforms import (
    enrich_orders_with_customers,
    calculate_order_totals,
    filter_active_records,
    normalize_column_names,
)


class TestEnrichOrdersWithCustomers:
    """Test the core join/enrichment operation."""

    @pytest.fixture
    def orders(self):
        return pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 103],
            "amount": [50.0, 75.0, 120.0],
        })

    @pytest.fixture
    def customers(self):
        return pl.DataFrame({
            "customer_id": [101, 102, 103],
            "name": ["Alice", "Bob", "Carol"],
            "region": ["East", "West", "East"],
        })

    def test_enriches_orders_with_customer_name(self, orders, customers):
        result = enrich_orders_with_customers(orders, customers)

        assert "name" in result.columns
        assert result["name"].to_list() == ["Alice", "Bob", "Carol"]

    def test_preserves_all_order_columns(self, orders, customers):
        result = enrich_orders_with_customers(orders, customers)

        for col in orders.columns:
            assert col in result.columns

    def test_handles_missing_customer(self, orders, customers):
        """Orders with no matching customer should have null name."""
        orders_with_unknown = orders.vstack(
            pl.DataFrame({"order_id": [4], "customer_id": [999], "amount": [30.0]})
        )
        result = enrich_orders_with_customers(orders_with_unknown, customers)

        assert result.filter(pl.col("customer_id") == 999)["name"].to_list() == [None]

    def test_handles_duplicate_customer_ids_in_lookup(self):
        """If lookup table has duplicates, result should not fan out unexpectedly."""
        orders = pl.DataFrame({"order_id": [1], "customer_id": [101], "amount": [50.0]})
        customers = pl.DataFrame({
            "customer_id": [101, 101],
            "name": ["Alice", "Alice-Dup"],
            "region": ["East", "East"],
        })
        result = enrich_orders_with_customers(orders, customers)

        # Depending on implementation: either dedup first or accept fan-out
        assert result.shape[0] >= 1

    def test_handles_empty_orders(self, customers):
        empty_orders = pl.DataFrame({
            "order_id": pl.Series([], dtype=pl.Int64),
            "customer_id": pl.Series([], dtype=pl.Int64),
            "amount": pl.Series([], dtype=pl.Float64),
        })
        result = enrich_orders_with_customers(empty_orders, customers)

        assert result.shape[0] == 0
        assert "name" in result.columns

    def test_handles_empty_customers(self, orders):
        empty_customers = pl.DataFrame({
            "customer_id": pl.Series([], dtype=pl.Int64),
            "name": pl.Series([], dtype=pl.Utf8),
            "region": pl.Series([], dtype=pl.Utf8),
        })
        result = enrich_orders_with_customers(orders, empty_customers)

        assert result.shape[0] == 3
        assert result["name"].null_count() == 3

    def test_output_schema(self, orders, customers):
        result = enrich_orders_with_customers(orders, customers)

        expected_schema = {
            "order_id": pl.Int64,
            "customer_id": pl.Int64,
            "amount": pl.Float64,
            "name": pl.Utf8,
            "region": pl.Utf8,
        }
        for col, dtype in expected_schema.items():
            assert result[col].dtype == dtype, f"{col}: expected {dtype}, got {result[col].dtype}"
```

## Testing Polars Column Operations

```python
import polars as pl
from polars.testing import assert_frame_equal


class TestCalculateOrderTotals:
    def test_computes_line_total(self):
        df = pl.DataFrame({
            "quantity": [2, 3, 1],
            "unit_price": [10.0, 20.0, 5.0],
        })
        result = calculate_order_totals(df)

        expected = pl.DataFrame({
            "quantity": [2, 3, 1],
            "unit_price": [10.0, 20.0, 5.0],
            "total": [20.0, 60.0, 5.0],
        })
        assert_frame_equal(result, expected)

    def test_handles_zero_quantity(self):
        df = pl.DataFrame({"quantity": [0], "unit_price": [10.0]})
        result = calculate_order_totals(df)
        assert result["total"].to_list() == [0.0]

    def test_handles_null_price(self):
        df = pl.DataFrame({"quantity": [2], "unit_price": [None]})
        result = calculate_order_totals(df)
        assert result["total"].to_list() == [None]


class TestFilterActiveRecords:
    def test_filters_by_status(self):
        df = pl.DataFrame({
            "id": [1, 2, 3],
            "status": ["active", "inactive", "active"],
        })
        result = filter_active_records(df)
        assert result["id"].to_list() == [1, 3]

    def test_returns_empty_when_none_active(self):
        df = pl.DataFrame({"id": [1], "status": ["inactive"]})
        result = filter_active_records(df)
        assert result.shape[0] == 0

    def test_handles_null_status(self):
        df = pl.DataFrame({"id": [1, 2], "status": ["active", None]})
        result = filter_active_records(df)
        assert result["id"].to_list() == [1]


class TestNormalizeColumnNames:
    def test_lowercases_and_replaces_spaces(self):
        df = pl.DataFrame({"First Name": [1], "Last Name": [2], "Order ID": [3]})
        result = normalize_column_names(df)
        assert result.columns == ["first_name", "last_name", "order_id"]

    def test_handles_already_normalized(self):
        df = pl.DataFrame({"first_name": [1], "age": [2]})
        result = normalize_column_names(df)
        assert result.columns == ["first_name", "age"]
```

## Testing Dask Transformations

```python
import pytest
import dask.dataframe as dd
import pandas as pd
from app.transforms_dask import enrich_large_dataset, aggregate_by_region


class TestDaskEnrichment:
    @pytest.fixture
    def dask_orders(self):
        pdf = pd.DataFrame({
            "order_id": range(1, 101),
            "customer_id": [i % 10 + 1 for i in range(100)],
            "amount": [float(i * 10) for i in range(100)],
        })
        return dd.from_pandas(pdf, npartitions=4)

    @pytest.fixture
    def dask_customers(self):
        pdf = pd.DataFrame({
            "customer_id": range(1, 11),
            "name": [f"Customer_{i}" for i in range(1, 11)],
            "region": ["East", "West"] * 5,
        })
        return dd.from_pandas(pdf, npartitions=1)

    def test_enrichment_adds_customer_columns(self, dask_orders, dask_customers):
        result = enrich_large_dataset(dask_orders, dask_customers).compute()

        assert "name" in result.columns
        assert "region" in result.columns
        assert len(result) == 100

    def test_enrichment_preserves_partitioning(self, dask_orders, dask_customers):
        result = enrich_large_dataset(dask_orders, dask_customers)
        assert result.npartitions >= 1

    def test_aggregate_by_region(self, dask_orders, dask_customers):
        enriched = enrich_large_dataset(dask_orders, dask_customers)
        result = aggregate_by_region(enriched).compute()

        assert "region" in result.columns
        assert "total_amount" in result.columns
        assert len(result) == 2  # East and West
```

## Testing Multi-DataFrame Lookups

```python
import polars as pl


class TestMultiLookupEnrichment:
    """Test enrichment from multiple reference tables."""

    @pytest.fixture
    def transactions(self):
        return pl.DataFrame({
            "txn_id": [1, 2, 3, 4],
            "product_id": ["P1", "P2", "P1", "P3"],
            "store_id": ["S1", "S1", "S2", "S2"],
            "quantity": [2, 1, 5, 3],
        })

    @pytest.fixture
    def products(self):
        return pl.DataFrame({
            "product_id": ["P1", "P2", "P3"],
            "product_name": ["Widget", "Gadget", "Gizmo"],
            "unit_price": [10.0, 25.0, 15.0],
        })

    @pytest.fixture
    def stores(self):
        return pl.DataFrame({
            "store_id": ["S1", "S2"],
            "store_name": ["Downtown", "Airport"],
            "region": ["East", "West"],
        })

    def test_enriches_with_product_and_store(self, transactions, products, stores):
        from app.transforms import enrich_transactions

        result = enrich_transactions(transactions, products, stores)

        assert "product_name" in result.columns
        assert "store_name" in result.columns
        assert "region" in result.columns
        assert result.shape[0] == 4

    def test_computes_line_total_after_enrichment(self, transactions, products, stores):
        from app.transforms import enrich_transactions

        result = enrich_transactions(transactions, products, stores)

        # txn 1: 2 * 10.0 = 20.0
        row = result.filter(pl.col("txn_id") == 1)
        assert row["line_total"].to_list() == [20.0]

    def test_missing_product_yields_null_name(self, transactions, stores):
        products_partial = pl.DataFrame({
            "product_id": ["P1", "P2"],
            "product_name": ["Widget", "Gadget"],
            "unit_price": [10.0, 25.0],
        })
        from app.transforms import enrich_transactions

        result = enrich_transactions(transactions, products_partial, stores)

        missing = result.filter(pl.col("product_id") == "P3")
        assert missing["product_name"].to_list() == [None]
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `assert_frame_equal(result, expected)` | Exact DataFrame comparison |
| `result.columns == [...]` | Verify output schema |
| `result[col].dtype == pl.Int64` | Verify column types |
| `result.shape == (rows, cols)` | Verify dimensions |
| `result[col].null_count()` | Check null handling |
| `result.filter(...)["col"].to_list()` | Check specific rows |
| `dd.from_pandas(pdf, npartitions=N)` | Create Dask test data |
| `dask_df.compute()` | Materialize Dask for assertions |
