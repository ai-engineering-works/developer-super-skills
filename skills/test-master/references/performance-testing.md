# Performance Testing — Large Files & Scaling

## Generating Large Test Data

```python
import pytest
import polars as pl
import numpy as np
from pathlib import Path


@pytest.fixture(scope="module")
def large_orders(tmp_path_factory) -> Path:
    """Generate a 1M-row orders CSV for performance tests."""
    tmp = tmp_path_factory.mktemp("perf")
    path = tmp / "orders_1m.csv"

    n = 1_000_000
    df = pl.DataFrame({
        "order_id": list(range(n)),
        "customer_id": np.random.randint(1, 100_001, size=n).tolist(),
        "product_id": [f"P{i % 500 + 1}" for i in range(n)],
        "quantity": np.random.randint(1, 20, size=n).tolist(),
        "amount": np.round(np.random.uniform(1.0, 1000.0, size=n), 2).tolist(),
    })
    df.write_csv(path)
    return path


@pytest.fixture(scope="module")
def large_customers(tmp_path_factory) -> Path:
    """Generate a 100K-row customer lookup CSV."""
    tmp = tmp_path_factory.mktemp("perf")
    path = tmp / "customers_100k.csv"

    n = 100_000
    df = pl.DataFrame({
        "customer_id": list(range(1, n + 1)),
        "name": [f"Customer_{i}" for i in range(1, n + 1)],
        "tier": [["standard", "premium", "enterprise"][i % 3] for i in range(n)],
        "region": [["East", "West", "Central", "North"][i % 4] for i in range(n)],
    })
    df.write_csv(path)
    return path
```

## Wall-Clock Performance Tests

```python
import time
import polars as pl


class TestPolarsPerformance:
    """Verify transformations complete within time budgets."""

    def test_read_1m_csv_under_5_seconds(self, large_orders):
        start = time.perf_counter()
        df = pl.read_csv(large_orders)
        elapsed = time.perf_counter() - start

        assert df.shape[0] == 1_000_000
        assert elapsed < 5.0, f"CSV read took {elapsed:.2f}s (budget: 5s)"

    def test_join_1m_orders_with_100k_customers(self, large_orders, large_customers):
        orders = pl.read_csv(large_orders)
        customers = pl.read_csv(large_customers)

        start = time.perf_counter()
        result = orders.join(customers, on="customer_id", how="left")
        elapsed = time.perf_counter() - start

        assert result.shape[0] == 1_000_000
        assert "name" in result.columns
        assert elapsed < 3.0, f"Join took {elapsed:.2f}s (budget: 3s)"

    def test_groupby_aggregation_under_2_seconds(self, large_orders):
        orders = pl.read_csv(large_orders)

        start = time.perf_counter()
        result = orders.group_by("product_id").agg([
            pl.col("amount").sum().alias("total_amount"),
            pl.col("quantity").sum().alias("total_quantity"),
            pl.col("order_id").count().alias("order_count"),
        ])
        elapsed = time.perf_counter() - start

        assert result.shape[0] == 500
        assert elapsed < 2.0, f"Aggregation took {elapsed:.2f}s (budget: 2s)"

    def test_parquet_write_and_read_roundtrip(self, large_orders, tmp_path):
        orders = pl.read_csv(large_orders)
        parquet_path = tmp_path / "orders.parquet"

        start = time.perf_counter()
        orders.write_parquet(parquet_path)
        write_time = time.perf_counter() - start

        start = time.perf_counter()
        reloaded = pl.read_parquet(parquet_path)
        read_time = time.perf_counter() - start

        assert reloaded.shape[0] == 1_000_000
        assert write_time < 3.0, f"Parquet write took {write_time:.2f}s"
        assert read_time < 1.0, f"Parquet read took {read_time:.2f}s"
```

## Memory Usage Tests

```python
import tracemalloc
import polars as pl


class TestMemoryUsage:
    """Ensure transformations don't use excessive memory."""

    def test_join_memory_stays_under_500mb(self, large_orders, large_customers):
        tracemalloc.start()

        orders = pl.read_csv(large_orders)
        customers = pl.read_csv(large_customers)
        result = orders.join(customers, on="customer_id", how="left")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        assert peak_mb < 500, f"Peak memory: {peak_mb:.1f}MB (budget: 500MB)"
        assert result.shape[0] == 1_000_000

    def test_lazy_evaluation_reduces_memory(self, large_orders, large_customers):
        """Lazy mode should use less memory than eager mode."""
        tracemalloc.start()

        orders = pl.scan_csv(large_orders)
        customers = pl.scan_csv(large_customers)
        result = (
            orders
            .join(customers, on="customer_id", how="left")
            .filter(pl.col("amount") > 500)
            .collect()
        )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        # Lazy mode should push filters down, using less memory
        assert peak_mb < 300, f"Peak memory: {peak_mb:.1f}MB (budget: 300MB)"

    def test_streaming_mode_handles_very_large_files(self, tmp_path):
        """Polars streaming should handle files larger than RAM."""
        # Create a moderately large test file
        path = tmp_path / "big.parquet"
        n = 2_000_000
        df = pl.DataFrame({
            "id": list(range(n)),
            "value": [float(i) for i in range(n)],
        })
        df.write_parquet(path)

        tracemalloc.start()
        result = (
            pl.scan_parquet(path)
            .filter(pl.col("value") > n / 2)
            .select(pl.col("value").sum())
            .collect(streaming=True)
        )
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert result.shape == (1, 1)
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 200, f"Streaming peak: {peak_mb:.1f}MB"
```

## Dask Scaling Tests

```python
import pytest
import dask.dataframe as dd
import pandas as pd
import numpy as np
import time


class TestDaskScaling:
    """Test Dask performance with partitioned data."""

    @pytest.fixture
    def dask_large_orders(self, tmp_path):
        """Create partitioned Parquet files for Dask."""
        n = 1_000_000
        pdf = pd.DataFrame({
            "order_id": range(n),
            "customer_id": np.random.randint(1, 100_001, size=n),
            "amount": np.round(np.random.uniform(1.0, 1000.0, size=n), 2),
        })
        path = tmp_path / "orders_partitioned"
        ddf = dd.from_pandas(pdf, npartitions=10)
        ddf.to_parquet(str(path))
        return path

    @pytest.fixture
    def dask_customers(self):
        pdf = pd.DataFrame({
            "customer_id": range(1, 100_001),
            "name": [f"Customer_{i}" for i in range(1, 100_001)],
        })
        return dd.from_pandas(pdf, npartitions=2)

    def test_dask_join_completes_within_budget(self, dask_large_orders, dask_customers):
        orders = dd.read_parquet(str(dask_large_orders))

        start = time.perf_counter()
        result = orders.merge(dask_customers.compute(), on="customer_id", how="left")
        computed = result.compute()
        elapsed = time.perf_counter() - start

        assert len(computed) == 1_000_000
        assert elapsed < 15.0, f"Dask join took {elapsed:.2f}s (budget: 15s)"

    def test_dask_scales_with_partitions(self, tmp_path):
        """More partitions should not degrade performance significantly."""
        n = 500_000
        pdf = pd.DataFrame({
            "id": range(n),
            "value": np.random.uniform(0, 100, size=n),
        })

        times = {}
        for npartitions in [2, 8, 16]:
            ddf = dd.from_pandas(pdf, npartitions=npartitions)
            start = time.perf_counter()
            ddf.groupby("id").value.sum().compute()
            times[npartitions] = time.perf_counter() - start

        # 16 partitions should not be more than 3x slower than 2
        assert times[16] < times[2] * 3, f"Scaling issue: 2p={times[2]:.2f}s, 16p={times[16]:.2f}s"
```

## Full Pipeline Performance Test

```python
import subprocess
import time


class TestPipelinePerformance:
    """End-to-end pipeline timing."""

    def test_full_pipeline_under_30_seconds(self, large_orders, large_customers, tmp_path):
        output = tmp_path / "result.parquet"

        start = time.perf_counter()
        result = subprocess.run(
            [
                "python", "-m", "app.cli",
                "--orders", str(large_orders),
                "--customers", str(large_customers),
                "--output", str(output),
            ],
            capture_output=True,
            text=True,
        )
        elapsed = time.perf_counter() - start

        assert result.returncode == 0, f"Pipeline failed:\n{result.stderr}"
        assert output.exists()
        assert elapsed < 30.0, f"Pipeline took {elapsed:.2f}s (budget: 30s)"

    def test_parquet_input_faster_than_csv(self, large_orders, large_customers, tmp_path):
        """Verify Parquet input path is faster than CSV."""
        # Convert inputs to Parquet
        orders_pq = tmp_path / "orders.parquet"
        customers_pq = tmp_path / "customers.parquet"
        pl.read_csv(large_orders).write_parquet(orders_pq)
        pl.read_csv(large_customers).write_parquet(customers_pq)

        # Time CSV path
        start = time.perf_counter()
        subprocess.run(
            ["python", "-m", "app.cli",
             "--orders", str(large_orders),
             "--customers", str(large_customers),
             "--output", str(tmp_path / "out_csv.parquet")],
            check=True, capture_output=True,
        )
        csv_time = time.perf_counter() - start

        # Time Parquet path
        start = time.perf_counter()
        subprocess.run(
            ["python", "-m", "app.cli",
             "--orders", str(orders_pq),
             "--customers", str(customers_pq),
             "--output", str(tmp_path / "out_pq.parquet")],
            check=True, capture_output=True,
        )
        parquet_time = time.perf_counter() - start

        assert parquet_time < csv_time, (
            f"Parquet ({parquet_time:.2f}s) should be faster than CSV ({csv_time:.2f}s)"
        )
```

## pytest Markers for Performance Tests

```ini
# pytest.ini
[pytest]
markers =
    perf: Performance tests (deselect with '-m "not perf"')
    slow: Tests that take >10 seconds
```

```python
# Usage
@pytest.mark.perf
@pytest.mark.slow
def test_large_file_join(large_orders, large_customers):
    ...

# Run only perf tests:   pytest -m perf
# Skip perf tests:       pytest -m "not perf"
```

## Quick Reference

| Metric | How to Measure | Budget |
|--------|---------------|--------|
| Read time | `time.perf_counter()` around `pl.read_csv()` | CSV: <5s/1M rows |
| Join time | Timer around `.join()` / `.merge()` | <3s for 1M x 100K |
| Memory peak | `tracemalloc.get_traced_memory()` | <500MB for 1M rows |
| Write time | Timer around `.write_parquet()` | <3s/1M rows |
| Pipeline total | Timer around `subprocess.run()` | <30s for 1M rows |

| Optimization | When to Use |
|--------------|-------------|
| `pl.scan_csv()` (lazy) | Filter before collecting |
| `.collect(streaming=True)` | Files larger than RAM |
| Parquet over CSV | Faster reads, type preservation |
| Dask partitioning | Multi-core parallel processing |
| `scope="module"` fixtures | Reuse large test data across tests |
