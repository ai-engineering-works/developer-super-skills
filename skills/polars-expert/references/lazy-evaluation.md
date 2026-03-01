# Lazy Evaluation in Polars

Lazy evaluation is Polars' most powerful feature, enabling automatic query optimization and significant performance gains.

## Core Concepts

### LazyFrame vs DataFrame

```python
import polars as pl

# Eager (DataFrame) - executes immediately
df_eager = pl.read_csv("data.csv")
result = df_eager.filter(pl.col("a") > 0).groupby("b").agg(pl.sum("c"))
# Execution path: read → filter → groupby → sum

# Lazy (LazyFrame) - builds plan first
df_lazy = pl.scan_csv("data.csv")
result = (df_lazy
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .collect())
# Execution plan may be: read only needed columns → filter → groupby → sum
```

### Why Use Lazy Evaluation?

1. **Query Optimization**: Polars rewrites your query for efficiency
2. **Predicate Pushdown**: Filter before reading data
3. **Projection Pushdown**: Read only needed columns
4. **Parallelization**: Better multi-threading opportunities
5. **Memory Efficiency**: Process data in streaming mode

## Lazy API

### Reading Data Lazily

```python
# CSV
lazy_df = pl.scan_csv("large_file.csv")
lazy_df = pl.scan_csv("data/*.csv")  # Multiple files

# Parquet (recommended)
lazy_df = pl.scan_parquet("data.parquet")

# JSON
lazy_df = pl.scan_ndjson("data.jsonl")

# IPC/Arrow
lazy_df = pl.scan_ipc("data.arrow")
```

### Building Lazy Queries

```python
# Build complex query
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .select(["id", "category", "value"])
    .filter(pl.col("value") > 100)
    .groupby("category")
    .agg([
        pl.col("value").sum().alias("total"),
        pl.col("value").mean().alias("average"),
        pl.col("id").n_unique().alias("count")
    ])
    .sort("total", descending=True)
    .collect())
```

### Chaining Operations

```python
# Method chaining (idiomatic)
result = (lazy_df
    .filter(pl.col("active") == True)
    .with_columns([
        (pl.col("value") * 1.1).alias("adjusted")
    ])
    .groupby("category")
    .agg(pl.sum("adjusted"))
    .collect())

# Each step adds to the query plan, no execution yet
```

## Query Optimization

### Predicate Pushdown

```python
# Before optimization (what you write)
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("status") == "active")
    .select(["id", "value"])
    .collect())

# After optimization (what executes)
# Only reads "id", "value", "status" columns
# Filters rows while reading (for Parquet statistics)
# Significantly less I/O
```

### Projection Pushdown

```python
# You only need 2 columns
result = (pl.scan_parquet("huge.parquet")
    .select(["id", "name"])
    .filter(pl.col("id") == 123)
    .collect())

# Polars optimization:
# - Only reads "id" and "name" columns
# - Other 98 columns are never loaded
# - Huge memory savings
```

### Combined Optimization

```python
# Complex query with multiple optimizations
result = (pl.scan_parquet("sales_data.parquet")
    .filter(
        (pl.col("date") >= "2024-01-01") &
        (pl.col("date") < "2024-02-01") &
        (pl.col("status") == "completed")
    )
    .select([
        "product_id",
        "quantity",
        "price"
    ])
    .with_columns([
        (pl.col("quantity") * pl.col("price")).alias("total")
    ])
    .groupby("product_id")
    .agg([
        pl.sum("total").alias("revenue"),
        pl.sum("quantity").alias("units_sold")
    ])
    .filter(pl.col("revenue") > 1000)
    .collect())

# Optimizations applied:
# 1. Only read needed columns (projection pushdown)
# 2. Filter by date range using Parquet statistics (predicate pushdown)
# 3. Filter by status before aggregation
# 4. Combine multiple filter operations
# 5. Eliminate unnecessary intermediate allocations
```

## Inspecting Query Plans

### Show Plan

```python
# See optimized plan
lazy_df = pl.scan_parquet("data.parquet")
plan = lazy_df.filter(pl.col("value") > 100).groupby("category").agg(pl.sum("value"))

print(plan.describe_optimized_plan())
# Output:
# df <- PROJECT */3 COLUMNS
# df <- FILTER col("value") > 100.0
# df <- PARQUET READ data.parquet
#   PROJECT 3/12 COLUMNS
#   STATISTICS ESTIMATION: row Group 0 skipped
# END PLAN
```

### Explain Plan

```python
# Detailed explanation
print(plan.explain())
```

### Graph Visualization

```python
# Visualize as graph (requires graphviz)
plan.show_graph()
```

## Advanced Patterns

### Common Table Expressions (CTEs)

```python
# Define CTEs
cte1 = pl.scan_parquet("data1.parquet").groupby("id").agg(pl.sum("value"))
cte2 = pl.scan_parquet("data2.parquet").filter(pl.col("active") == True)

# Use CTEs multiple times
result1 = cte1.join(cte2, on="id").collect()
result2 = cte1.filter(pl.col("sum") > 100).collect()
```

### Conditional Execution

```python
# Build query based on conditions
lazy_df = pl.scan_parquet("data.parquet")

if filter_by_date:
    lazy_df = lazy_df.filter(pl.col("date") >= start_date)

if specific_category:
    lazy_df = lazy_df.filter(pl.col("category") == specific_category)

result = lazy_df.groupby("id").agg(pl.sum("value")).collect()
```

### Dynamic Column Selection

```python
# Select columns dynamically
columns_to_select = ["id", "name", "value"]
additional_filter = True

query = pl.scan_parquet("data.parquet").select(columns_to_select)

if additional_filter:
    query = query.filter(pl.col("value") > 100)

result = query.collect()
```

## Streaming Execution

### Out-of-Core Processing

```python
# Process data larger than RAM
result = (pl.scan_parquet("huge_file.parquet")
    .groupby("category")
    .agg(pl.all().sum())
    .collect(streaming=True))  # Enable streaming
```

### When to Use Streaming

- Dataset larger than available RAM
- Memory-constrained environments
- Complex aggregations on huge datasets

### Streaming Limitations

```python
# Works with streaming
result = (pl.scan_parquet("huge.parquet")
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .collect(streaming=True))

# May not work with streaming (requires sorting)
result = (pl.scan_parquet("huge.parquet")
    .sort("a")  # Sorting needs full data in memory
    .collect(streaming=True))  # May fail
```

## Performance Comparison

### Lazy vs Eager Benchmark

```python
import time

# Eager version
start = time.time()
df = pl.read_parquet("large.parquet")
result = df.filter(pl.col("value") > 100).groupby("category").agg(pl.sum("value"))
eager_time = time.time() - start

# Lazy version
start = time.time()
result = (pl.scan_parquet("large.parquet")
    .filter(pl.col("value") > 100)
    .groupby("category")
    .agg(pl.sum("value"))
    .collect())
lazy_time = time.time() - start

print(f"Eager: {eager_time:.2f}s, Lazy: {lazy_time:.2f}s")
print(f"Speedup: {eager_time / lazy_time:.2f}x")
```

## Best Practices

### Always Use Lazy for Complex Queries

```python
# Bad: Eager execution
df = pl.read_parquet("data.parquet")
df = df.filter(pl.col("date") >= "2024-01-01")
df = df.groupby("category").agg(pl.sum("value"))

# Good: Lazy execution
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .groupby("category")
    .agg(pl.sum("value"))
    .collect())
```

### Use .collect() Only When Needed

```python
# Bad: Multiple collects
result1 = df.filter(pl.col("a") > 0).collect()
result2 = result1.groupby("b").agg(pl.sum("c")).collect()

# Good: Single collect
result = (df
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .collect())
```

### Leverage Parquet Statistics

```python
# Store as Parquet with statistics
df.write_parquet("data.parquet", statistics=True)

# Filters use statistics
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")  # Uses min/max statistics
    .filter(pl.col("category") == "electronics")  # Uses min/max statistics
    .collect())
```

### Sink for Large Results

```python
# Write large results without loading into memory
(pl.scan_parquet("huge_input.parquet")
    .groupby("category")
    .agg(pl.all().sum())
    .sink_parquet("huge_output.parquet"))
```

## Anti-Patterns

### Don't Collect Too Early

```python
# Bad: Breaks optimization chain
filtered = df.filter(pl.col("a") > 0).collect()
result = filtered.groupby("b").agg(pl.sum("c"))

# Good: Keep lazy until end
result = df.filter(pl.col("a") > 0).groupby("b").agg(pl.sum("c")).collect()
```

### Don't Use Eager I/O for Large Files

```python
# Bad: Loads entire file
df = pl.read_parquet("huge.parquet")

# Good: Lazy loading
lazy_df = pl.scan_parquet("huge.parquet")
```

## Debugging Lazy Queries

### Fetch Sample

```python
# Get first few rows without full execution
sample = lazy_df.fetch(10)  # First 10 rows
sample = lazy_df.head(5)    # Alternative
```

### Slice Before Collect

```python
# Test query on subset
test_result = (lazy_df
    .slice(0, 1000)  # First 1000 rows
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .collect())

# Run full query
full_result = (lazy_df
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .collect())
```

### Profile Query

```python
# Enable profiling
result = query.collect(profile=True)

# View profiling information
print(result.profile)
```

## Integration with Other Libraries

### Convert to Pandas

```python
# Collect lazy frame, convert to pandas
result = lazy_df.collect().to_pandas()
```

### Convert from Pandas

```python
import pandas as pd

# Convert to Polars lazy
df_pd = pd.read_csv("data.csv")
lazy_df = pl.from_pandas(df_pd).lazy()
```

### Arrow Integration

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Scan with Arrow
lazy_df = pl.scan_parquet("data.parquet")

# Convert to Arrow table
table = lazy_df.collect().to_arrow()
```
