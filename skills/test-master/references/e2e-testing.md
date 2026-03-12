# E2E Testing — Full Pipeline

## Complete Pipeline Test

```python
import subprocess
import pytest
import polars as pl
from pathlib import Path


class TestFullPipeline:
    """Test the entire batch job: input files -> CLI -> output files."""

    @pytest.fixture
    def pipeline_data(self, tmp_path):
        """Set up a realistic multi-file input scenario."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Main transaction data
        pl.DataFrame({
            "txn_id": list(range(1, 11)),
            "customer_id": [101, 102, 103, 101, 102, 103, 104, 105, 101, 102],
            "product_id": ["P1", "P2", "P3", "P1", "P2", "P3", "P1", "P2", "P3", "P1"],
            "quantity": [2, 1, 5, 3, 2, 1, 4, 2, 3, 1],
            "date": ["2024-01-01"] * 5 + ["2024-01-02"] * 5,
        }).write_csv(input_dir / "transactions.csv")

        # Customer lookup
        pl.DataFrame({
            "customer_id": [101, 102, 103, 104, 105],
            "name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
            "tier": ["premium", "standard", "premium", "standard", "premium"],
        }).write_csv(input_dir / "customers.csv")

        # Product lookup
        pl.DataFrame({
            "product_id": ["P1", "P2", "P3"],
            "product_name": ["Widget", "Gadget", "Gizmo"],
            "unit_price": [10.0, 25.0, 15.0],
        }).write_csv(input_dir / "products.csv")

        return {"input": input_dir, "output": output_dir}

    def run_pipeline(self, pipeline_data, extra_args=None):
        """Helper to invoke the CLI."""
        cmd = [
            "python", "-m", "app.cli",
            "--transactions", str(pipeline_data["input"] / "transactions.csv"),
            "--customers", str(pipeline_data["input"] / "customers.csv"),
            "--products", str(pipeline_data["input"] / "products.csv"),
            "--output-dir", str(pipeline_data["output"]),
        ]
        if extra_args:
            cmd.extend(extra_args)

        return subprocess.run(cmd, capture_output=True, text=True)

    def test_pipeline_succeeds(self, pipeline_data):
        result = self.run_pipeline(pipeline_data)
        assert result.returncode == 0, f"Pipeline failed:\n{result.stderr}"

    def test_output_file_exists(self, pipeline_data):
        self.run_pipeline(pipeline_data)

        output_files = list(pipeline_data["output"].glob("*.parquet"))
        assert len(output_files) > 0, "No output files produced"

    def test_output_has_enriched_columns(self, pipeline_data):
        self.run_pipeline(pipeline_data)

        result = pl.read_parquet(pipeline_data["output"] / "enriched_transactions.parquet")

        # Verify all lookup columns are present
        assert "name" in result.columns, "Customer name not enriched"
        assert "product_name" in result.columns, "Product name not enriched"
        assert "unit_price" in result.columns, "Unit price not enriched"

    def test_output_row_count_matches_input(self, pipeline_data):
        self.run_pipeline(pipeline_data)

        input_df = pl.read_csv(pipeline_data["input"] / "transactions.csv")
        output_df = pl.read_parquet(pipeline_data["output"] / "enriched_transactions.parquet")

        assert output_df.shape[0] == input_df.shape[0], (
            f"Row count mismatch: input={input_df.shape[0]}, output={output_df.shape[0]}"
        )

    def test_output_line_totals_are_correct(self, pipeline_data):
        self.run_pipeline(pipeline_data)

        result = pl.read_parquet(pipeline_data["output"] / "enriched_transactions.parquet")

        # txn_id=1: quantity=2, product=P1 (unit_price=10.0) -> total=20.0
        row = result.filter(pl.col("txn_id") == 1)
        assert row["line_total"].to_list() == [20.0]

        # txn_id=3: quantity=5, product=P3 (unit_price=15.0) -> total=75.0
        row = result.filter(pl.col("txn_id") == 3)
        assert row["line_total"].to_list() == [75.0]

    def test_output_format_csv(self, pipeline_data):
        self.run_pipeline(pipeline_data, extra_args=["--output-format", "csv"])

        output_files = list(pipeline_data["output"].glob("*.csv"))
        assert len(output_files) > 0

        result = pl.read_csv(output_files[0])
        assert result.shape[0] > 0
```

## Testing with Multiple Lookup Tables

```python
class TestMultiLookupPipeline:
    """Verify enrichment from multiple reference files."""

    @pytest.fixture
    def data_with_regions(self, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 103],
            "store_id": ["S1", "S2", "S1"],
            "amount": [100.0, 200.0, 300.0],
        }).write_csv(input_dir / "orders.csv")

        pl.DataFrame({
            "customer_id": [101, 102, 103],
            "name": ["Alice", "Bob", "Carol"],
        }).write_csv(input_dir / "customers.csv")

        pl.DataFrame({
            "store_id": ["S1", "S2"],
            "store_name": ["Downtown", "Airport"],
            "region": ["East", "West"],
        }).write_csv(input_dir / "stores.csv")

        return {"input": input_dir, "output": output_dir}

    def test_enriches_with_both_customer_and_store(self, data_with_regions):
        from app.pipeline import run_pipeline

        run_pipeline(
            orders_path=data_with_regions["input"] / "orders.csv",
            customers_path=data_with_regions["input"] / "customers.csv",
            stores_path=data_with_regions["input"] / "stores.csv",
            output_path=data_with_regions["output"] / "result.parquet",
        )

        result = pl.read_parquet(data_with_regions["output"] / "result.parquet")

        assert "name" in result.columns
        assert "store_name" in result.columns
        assert "region" in result.columns
        assert result.shape[0] == 3
```

## Edge Case Tests

```python
class TestPipelineEdgeCases:

    def test_handles_empty_input_file(self, tmp_path):
        """Pipeline should produce empty output, not crash."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Empty transactions (header only)
        (input_dir / "transactions.csv").write_text("txn_id,customer_id,amount\n")
        pl.DataFrame({
            "customer_id": [101],
            "name": ["Alice"],
        }).write_csv(input_dir / "customers.csv")

        result = subprocess.run(
            ["python", "-m", "app.cli",
             "--transactions", str(input_dir / "transactions.csv"),
             "--customers", str(input_dir / "customers.csv"),
             "--output", str(output_dir / "result.parquet")],
            capture_output=True, text=True,
        )

        assert result.returncode == 0
        output = pl.read_parquet(output_dir / "result.parquet")
        assert output.shape[0] == 0

    def test_handles_unicode_in_data(self, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        pl.DataFrame({
            "id": [1, 2],
            "name": ["Rene", "Bjork"],
        }).write_csv(input_dir / "data.csv")

        reloaded = pl.read_csv(input_dir / "data.csv")
        assert reloaded["name"].to_list() == ["Rene", "Bjork"]

    def test_handles_null_join_keys(self, tmp_path):
        """Rows with null join keys should survive but have null enrichment."""
        from app.transforms import enrich_orders_with_customers

        orders = pl.DataFrame({
            "order_id": [1, 2],
            "customer_id": [101, None],
            "amount": [50.0, 75.0],
        })
        customers = pl.DataFrame({
            "customer_id": [101],
            "name": ["Alice"],
        })

        result = enrich_orders_with_customers(orders, customers)
        assert result.shape[0] == 2
        assert result.filter(pl.col("customer_id").is_null())["name"].to_list() == [None]

    def test_handles_duplicate_keys_in_main_data(self):
        from app.transforms import enrich_orders_with_customers

        orders = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 101, 101],
            "amount": [10.0, 20.0, 30.0],
        })
        customers = pl.DataFrame({
            "customer_id": [101],
            "name": ["Alice"],
        })

        result = enrich_orders_with_customers(orders, customers)
        assert result.shape[0] == 3
        assert result["name"].to_list() == ["Alice", "Alice", "Alice"]

    def test_handles_extra_columns_in_input(self, tmp_path):
        """Pipeline should tolerate extra columns it doesn't need."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        pl.DataFrame({
            "order_id": [1],
            "customer_id": [101],
            "amount": [50.0],
            "extra_col": ["ignored"],
            "another_extra": [999],
        }).write_csv(input_dir / "orders.csv")

        pl.DataFrame({
            "customer_id": [101],
            "name": ["Alice"],
        }).write_csv(input_dir / "customers.csv")

        from app.pipeline import run_pipeline
        output_path = tmp_path / "result.parquet"
        run_pipeline(
            orders_path=input_dir / "orders.csv",
            customers_path=input_dir / "customers.csv",
            output_path=output_path,
        )

        result = pl.read_parquet(output_path)
        assert result.shape[0] == 1
```

## Snapshot Testing for Output Files

```python
import polars as pl
from polars.testing import assert_frame_equal


class TestOutputSnapshot:
    """Compare pipeline output against known-good snapshots."""

    def test_output_matches_golden_file(self, tmp_path):
        from app.pipeline import run_pipeline

        # Prepare inputs
        orders = pl.DataFrame({
            "order_id": [1, 2],
            "customer_id": [101, 102],
            "amount": [50.0, 75.0],
        })
        customers = pl.DataFrame({
            "customer_id": [101, 102],
            "name": ["Alice", "Bob"],
        })
        orders.write_csv(tmp_path / "orders.csv")
        customers.write_csv(tmp_path / "customers.csv")

        output_path = tmp_path / "result.parquet"
        run_pipeline(
            orders_path=tmp_path / "orders.csv",
            customers_path=tmp_path / "customers.csv",
            output_path=output_path,
        )

        result = pl.read_parquet(output_path)

        expected = pl.DataFrame({
            "order_id": [1, 2],
            "customer_id": [101, 102],
            "amount": [50.0, 75.0],
            "name": ["Alice", "Bob"],
        })

        assert_frame_equal(
            result.sort("order_id"),
            expected.sort("order_id"),
        )
```

## Quick Reference

| Test Type | What It Verifies |
|-----------|-----------------|
| Pipeline exit code | CLI runs without errors |
| Output file exists | Files are written to correct path |
| Output schema | Enriched columns are present |
| Row count | No rows lost or duplicated in joins |
| Computed values | Calculated fields are correct |
| Edge cases | Empty files, nulls, duplicates, unicode |
| Snapshot | Output matches known-good baseline |

| Edge Case | Why It Matters |
|-----------|----------------|
| Empty input file | Pipeline should not crash |
| Null join keys | Rows survive with null enrichment |
| Duplicate keys in main data | Join should not drop/fan-out |
| Missing lookup entries | Left join yields nulls |
| Extra columns | Pipeline tolerates schema drift |
