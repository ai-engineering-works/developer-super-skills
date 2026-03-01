# Polars Performance Optimization

Maximize Polars performance through proper data types, query patterns, and memory management.

## Core Concepts

### Why Polars is Fast

1. **Rust implementation**: Zero-copy operations, memory safety
2. **Multi-threading**: Automatic parallelization
3. **Columnar storage**: Cache-efficient access
4. **Query optimization**: Lazy evaluation rewrites
5. **Arrow memory model**: Interoperability, zero-copy

## Data Type Optimization

### Use Appropriate Numeric Types

```python
import polars as pl

# Default: Int64 (8 bytes)
df = pl.DataFrame({
    "id": [1, 2, 3],
    "value": [100, 200, 300]
})

# Optimized: Int32 (4 bytes), Int16 (2 bytes)
df = df.with_columns([
    pl.col("id").cast(pl.Int32),
    pl.col("value").cast(pl.Int16)
])

# Memory savings: 50-75%
```

### Type Selection Guide

| Range | Recommended Type | Bytes |
|-------|-----------------|-------|
| -128 to 127 | Int8 | 1 |
| -32768 to 32767 | Int16 | 2 |
| -2.1B to 2.1B | Int32 | 4 |
| Larger | Int64 | 8 |
| 0 to 255 | UInt8 | 1 |
| 0 to 65535 | UInt16 | 2 |
| Float precision | Float32 | 4 |
| Double precision | Float64 | 8 |

### Categorical for Strings

```python
# Before: String comparisons (slow)
df = pl.DataFrame({
    "category": ["A", "B", "A", "C", "B"] * 100000
})
result = df.filter(pl.col("category") == "A")

# After: Categorical (fast)
df = df.with_columns([
    pl.col("category").cast(pl.Categorical)
])
result = df.filter(pl.col("category") == "A")

# Speedup: 5-10x for filtering/groupby
```

### When to Use Categorical

**Use Categorical when:**
- Low cardinality (< 100 unique values)
- Repeated string values
- Used for grouping or filtering
- Memory optimization needed

**Avoid Categorical when:**
- High cardinality (> 1000 unique values)
- Mostly unique values (like IDs)
- Need string manipulation

### Boolean for Flags

```python
# Before: String flags
df = pl.DataFrame({
    "is_active": ["true", "false", "true"] * 1000
})

# After: Boolean flags
df = df.with_columns([
    pl.col("is_active").cast(pl.Boolean)
])

# Memory savings: 8x (1 byte vs 8 bytes)
```

## Memory Efficiency

### Reduce Memory Footprint

```python
import polars as pl

# Load data and optimize types
df = pl.read_csv("data.csv").with_columns([
    pl.col(pl.Int64).cast(pl.Int32),
    pl.col(pl.Int64).cast(pl.Int16),
    pl.col(pl.String).cast(pl.Categorical),
    pl.col("^is_.*$").cast(pl.Boolean)
])

# Profile memory usage
print(df.estimated_size())
print(df.schema)
```

### Streaming for Large Data

```python
# Process data larger than RAM
result = (pl.scan_parquet("huge.parquet")
    .groupby("category")
    .agg(pl.all().sum())
    .collect(streaming=True))
```

### Free Memory

```python
# Drop columns early
result = (df
    .drop(["unused1", "unused2"])
    .groupby("category")
    .agg(pl.sum("value"))
)

# Use del for large intermediates
large_df = process_large_data()
result = large_df.group_by("id").agg(pl.sum("value"))
del large_df  # Free memory
```

## Query Optimization

### Use Lazy Evaluation

```python
# Bad: Eager execution
df = pl.read_parquet("data.parquet")
df = df.filter(pl.col("date") >= "2024-01-01")
result = df.groupby("category").agg(pl.sum("value"))

# Good: Lazy execution
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .groupby("category")
    .agg(pl.sum("value"))
    .collect())
```

### Avoid Unnecessary Copies

```python
# Bad: Creates copy
filtered = df.filter(pl.col("a") > 0)
summed = filtered.select(pl.sum("value"))

# Good: No copy
summed = df.filter(pl.col("a") > 0).select(pl.sum("value"))
```

### Single-Pass Operations

```python
# Bad: Multiple passes
result1 = df.filter(pl.col("a") > 0)
result2 = result1.groupby("b").agg(pl.sum("c"))
result3 = result2.filter(pl.col("sum") > 100)

# Good: Single pass
result = (df
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.sum("c"))
    .filter(pl.col("sum") > 100)
)
```

## I/O Optimization

### Parquet > CSV

```python
# CSV: Slow, no statistics
df = pl.read_csv("data.csv")

# Parquet: Fast, with statistics
df = pl.read_parquet("data.parquet")

# Speedup: 5-10x for reading, 2-3x for filtering
```

### Write Efficient Parquet

```python
# Write with compression
df.write_parquet(
    "output.parquet",
    compression="snappy",  # Good balance
    compression_level=3,
    statistics=True,       # Enable statistics for filtering
    use_pyarrow=True       # Use PyArrow engine
)
```

### Read Optimization

```python
# Read only needed columns
df = pl.read_parquet("data.parquet", columns=["id", "name", "value"])

# Read with projection (lazy)
df = pl.scan_parquet("data.parquet").select(["id", "name", "value"])

# Read with row group skipping (lazy + filter)
df = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .collect())
```

### Batch Processing

```python
# Process large file in batches
batch_size = 100000
for i in range(0, total_rows, batch_size):
    batch = pl.read_parquet(
        "data.parquet",
        rows=batch_size,
        row_offset=i
    )
    process_batch(batch)
```

## Expression Optimization

### Vectorized Operations

```python
# Bad: Row-wise iteration
for row in df.iter_rows(named=True):
    result = row["a"] * row["b"]

# Good: Vectorized
result = df.select(pl.col("a") * pl.col("b"))
```

### Avoid Python Loops

```python
# Bad: Python loop
results = []
for value in df["column"]:
    results.append(complex_calculation(value))

# Good: Vectorized
results = df.select(
    pl.col("column").map_elements(complex_calculation, return_dtype=pl.Float64)
)
```

### Use Native Polars Functions

```python
# Bad: Custom implementation
def custom_sum(series):
    return series.sum()

# Good: Native Polars
result = df.select(pl.col("value").sum())
```

## GroupBy Optimization

### Optimize GroupBy Keys

```python
# Before: String groupby
result = df.groupby("category_string").agg(pl.sum("value"))

# After: Categorical groupby (5-10x faster)
df = df.with_columns([
    pl.col("category_string").cast(pl.Categorical)
])
result = df.groupby("category_string").agg(pl.sum("value"))
```

### Multi-Column GroupBy

```python
# Efficient multi-column groupby
result = (df
    .groupby(["category", "sub_category", "region"])
    .agg([
        pl.sum("value"),
        pl.mean("price"),
        pl.count("id")
    ])
)
```

### GroupBy Ordering

```python
# Order by group (not by value)
result = (df
    .groupby("category", maintain_order=True)
    .agg(pl.sum("value"))
)
```

## Join Optimization

### Join Strategy Selection

```python
# Left join (default)
result = df1.join(df2, on="id", how="left")

# Inner join (faster, if applicable)
result = df1.join(df2, on="id", how="inner")

# Cross join (expensive, avoid if possible)
result = df1.join(df2, how="cross")
```

### Join on Different Columns

```python
# Join on different column names
result = df1.join(
    df2,
    left_on="id1",
    right_on="id2",
    how="inner"
)
```

### Join with Predicates

```python
# Combine join with filter
result = (df1
    .join(df2, on="id")
    .filter(pl.col("date") >= "2024-01-01")
)

# Alternative: Filter before joining
df1_filtered = df1.filter(pl.col("date") >= "2024-01-01")
result = df1_filtered.join(df2, on="id")
```

## Performance Profiling

### Benchmark Operations

```python
import time

def benchmark(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed

# Benchmark different approaches
result1, time1 = benchmark(
    lambda: df.filter(pl.col("a") > 0).groupby("b").agg(pl.sum("c"))
)

result2, time2 = benchmark(
    lambda: (df.lazy()
        .filter(pl.col("a") > 0)
        .groupby("b")
        .agg(pl.sum("c"))
        .collect())
)

print(f"Eager: {time1:.3f}s, Lazy: {time2:.3f}s")
```

### Profile Memory

```python
# Check memory usage
print(df.estimated_size())  # Estimated size in bytes
print(df.estimated_size("mb"))  # In megabytes

# Check column memory
for col in df.columns:
    col_size = df[col].estimated_size()
    print(f"{col}: {col_size / 1024 / 1024:.2f} MB")
```

### Query Plan Analysis

```python
# Inspect optimized plan
lazy_df = pl.scan_parquet("data.parquet")
query = lazy_df.filter(pl.col("a") > 0).groupby("b").agg(pl.sum("c"))

print(query.describe_optimized_plan())
print(query.explain())
```

## Performance Patterns

### Early Projection

```python
# Select columns early (reduce memory)
result = (pl.scan_parquet("data.parquet")
    .select(["id", "category", "value"])  # Early projection
    .filter(pl.col("value") > 100)
    .groupby("category")
    .agg(pl.sum("value"))
    .collect())
```

### Early Filtering

```python
# Filter as early as possible
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")  # Early filter
    .filter(pl.col("status") == "active")
    .groupby("category")
    .agg(pl.sum("value"))
    .collect())
```

### Combine Operations

```python
# Bad: Multiple operations
df = df.filter(pl.col("a") > 0)
df = df.with_columns((pl.col("b") * 2).alias("doubled"))
df = df.groupby("c").agg(pl.sum("doubled"))

# Good: Combined
result = (df
    .filter(pl.col("a") > 0)
    .with_columns((pl.col("b") * 2).alias("doubled"))
    .groupby("c")
    .agg(pl.sum("doubled"))
)
```

## Anti-Patterns

### Don't Convert Unnecessarily

```python
# Bad: Convert to pandas unnecessarily
df_pd = df.to_pandas()
result = df_pd.groupby("category").sum()

# Good: Stay in Polars
result = df.groupby("category").agg(pl.all().sum())
```

### Don't Use Small Chunks

```python
# Bad: Process small chunks individually
results = []
for i in range(0, len(df), 100):
    chunk = df[i:i+100]
    results.append(chunk.select(pl.sum("value")))

# Good: Process entire dataset
result = df.select(pl.sum("value"))
```

### Don't Ignore Data Types

```python
# Bad: Use default types
df = pl.DataFrame({"id": range(1000000)})  # Int64

# Good: Use appropriate types
df = pl.DataFrame({"id": range(1000000)}, schema={"id": pl.Int32})
```

## Comparison with Pandas

### Performance Comparison

```python
import pandas as pd
import polars as pl
import time

# Create large dataset
data = {"a": range(10_000_000), "b": range(10_000_000)}

# Pandas
df_pd = pd.DataFrame(data)
start = time.time()
result_pd = df_pd[df_pd["a"] > 0].groupby("b").sum()
pandas_time = time.time() - start

# Polars (eager)
df_pl = pl.DataFrame(data)
start = time.time()
result_pl = df_pl.filter(pl.col("a") > 0).groupby("b").agg(pl.col("a").sum())
polars_time = time.time() - start

# Polars (lazy)
start = time.time()
result_pl_lazy = (df_pl
    .lazy()
    .filter(pl.col("a") > 0)
    .groupby("b")
    .agg(pl.col("a").sum())
    .collect())
polars_lazy_time = time.time() - start

print(f"Pandas: {pandas_time:.2f}s")
print(f"Polars eager: {polars_time:.2f}s ({pandas_time/polars_time:.1f}x)")
print(f"Polars lazy: {polars_lazy_time:.2f}s ({pandas_time/polars_lazy_time:.1f}x)")
```

### Typical Speedups

| Operation | Polars vs Pandas |
|-----------|-----------------|
| Read CSV | 2-3x |
| Filter | 3-5x |
| GroupBy | 5-10x |
| Join | 2-4x |
| Memory usage | 1/3 to 1/5 |

## Best Practices Summary

1. **Use appropriate data types**: Int32 vs Int64, Categorical for strings
2. **Lazy evaluation**: For complex queries and large datasets
3. **Parquet format**: For data storage and I/O
4. **Native expressions**: Avoid Python loops and custom functions
5. **Early projection**: Select columns early
6. **Early filtering**: Filter rows early
7. **Single-pass operations**: Chain operations together
8. **Profile**: Benchmark and optimize critical paths
9. **Streaming**: For datasets larger than RAM
10. **Categorical**: For low-cardinality strings in grouping/filtering
