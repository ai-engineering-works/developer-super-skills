# Polars Expression API

The expression API is Polars' core innovation, enabling composable, optimized, and readable data transformations.

## Core Concepts

### What are Expressions?

Expressions are composable operations that define *what* to compute, not *how* to compute it. Polars optimizes the execution.

```python
import polars as pl

# Expression-based (idiomatic Polars)
result = df.select([
    pl.col("value").sum().alias("total"),
    pl.col("value").mean().alias("average"),
    (pl.col("value") * 2).alias("doubled")
])

# vs imperative (non-idiomatic)
result = df["value"].sum()
```

### Why Expressions Matter

- **Composable**: Chain operations naturally
- **Optimizable**: Polars rewrites and optimizes expressions
- **Parallelizable**: Automatic multi-threading
- **Type-safe**: Compile-time type checking
- **Readable**: Self-documenting code

## Basic Expressions

### Column Selection

```python
import polars as pl

# Select single column
df.select(pl.col("name"))

# Select multiple columns
df.select([pl.col("name"), pl.col("age")])

# Select with regex
df.select(pl.col("^num_.*$"))  # All columns starting with "num_"

# Select by dtype
df.select(pl.col(pl.Int64))  # All Int64 columns
df.select(pl.col(pl.String, pl.Categorical))  # String and Categorical
```

### Column Aliasing

```python
# Rename in select
df.select([
    pl.col("old_name").alias("new_name")
])

# Multiple aliases
df.select([
    pl.col("a").alias("col_a"),
    pl.col("b").alias("col_b")
])
```

### Arithmetic Operations

```python
# Basic math
df.select([
    (pl.col("a") + pl.col("b")).alias("sum"),
    (pl.col("a") - pl.col("b")).alias("difference"),
    (pl.col("a") * pl.col("b")).alias("product"),
    (pl.col("a") / pl.col("b")).alias("quotient")
])

# Scalar operations
df.select([
    (pl.col("value") * 2).alias("doubled"),
    (pl.col("value") + 10).alias("plus_ten"),
    (pl.col("value") ** 2).alias("squared")
])
```

## Comparison and Logical Operations

### Comparisons

```python
# Comparisons
df.filter(pl.col("age") > 25)
df.filter(pl.col("score") >= 90)
df.filter(pl.col("name") == "Alice")
df.filter(pl.col("status").is_in(["active", "pending"]))

# Null checks
df.filter(pl.col("value").is_null())
df.filter(pl.col("value").is_not_null())
```

### Logical Operators

```python
# AND
df.filter((pl.col("age") > 25) & (pl.col("age") < 65))

# OR
df.filter((pl.col("status") == "active") | (pl.col("status") == "pending"))

# NOT
df.filter(~pl.col("is_deleted"))

# Complex logic
df.filter(
    (pl.col("age") >= 18) &
    (pl.col("country") == "US") &
    (
        (pl.col("status") == "active") |
        (pl.col("status") == "trial")
    )
)
```

## String Operations

### Basic String Manipulation

```python
# String methods
df.select([
    pl.col("name").str.to_uppercase().alias("upper"),
    pl.col("name").str.to_lowercase().alias("lower"),
    pl.col("name").str.strip().alias("stripped"),
    pl.col("name").str.replace("old", "new").alias("replaced")
])

# String length
df.select([
    pl.col("text").str.len_chars().alias("char_count"),
    pl.col("text").str.len_bytes().alias("byte_count")
])
```

### String Parsing

```python
# Contains
df.filter(pl.col("text").str.contains("error"))

# Starts with / ends with
df.filter(pl.col("filename").str.starts_with("report_"))
df.filter(pl.col("filename").str.ends_with(".csv"))

# Extract regex
df.select([
    pl.col("email")
     .str.extract(r"([a-zA-Z0-9._%+-]+)@")
     .alias("username")
])

# Split
df.select([
    pl.col("path").str.split("/").alias("parts")
])
```

## Aggregation Expressions

### Basic Aggregations

```python
# Common aggregations
df.select([
    pl.col("value").sum().alias("total"),
    pl.col("value").mean().alias("average"),
    pl.col("value").median().alias("median"),
    pl.col("value").min().alias("minimum"),
    pl.col("value").max().alias("maximum"),
    pl.col("value").std().alias("std_dev"),
    pl.col("value").var().alias("variance"),
    pl.col("value").count().alias("count"),
    pl.col("value").n_unique().alias("unique_count")
])
```

### Quantiles

```python
# Quantiles
df.select([
    pl.col("value").quantile(0.25).alias("q1"),
    pl.col("value").quantile(0.50).alias("median"),
    pl.col("value").quantile(0.75).alias("q3")
])

# Multiple quantiles
df.select([
    pl.col("value").quantile([0.25, 0.5, 0.75, 0.9, 0.99])
])
```

### First and Last

```python
# First/Last non-null values
df.select([
    pl.col("value").first().alias("first_value"),
    pl.col("value").last().alias("last_value")
])
```

## Conditional Expressions

### if-then-else

```python
# Simple conditional
df.select([
    pl.when(pl.col("age") >= 18)
     .then(pl.lit("adult"))
     .otherwise(pl.lit("minor"))
     .alias("status")
])

# Multiple conditions
df.select([
    pl.when(pl.col("score") >= 90)
     .then(pl.lit("A"))
     .when(pl.col("score") >= 80)
     .then(pl.lit("B"))
     .when(pl.col("score") >= 70)
     .then(pl.lit("C"))
     .otherwise(pl.lit("F"))
     .alias("grade")
])

# Conditional with expressions
df.select([
    pl.when(pl.col("category") == "A")
     .then(pl.col("value") * 1.1)
     .when(pl.col("category") == "B")
     .then(pl.col("value") * 1.05)
     .otherwise(pl.col("value"))
     .alias("adjusted_value")
])
```

### Coalesce

```python
# First non-null value
df.select([
    pl.coalesce(["primary", "secondary", "tertiary"]).alias("first_valid")
])

# Replace null with default
df.select([
    pl.col("value").fill_null(0).alias("filled")
])
```

## Window Functions

### Ranking

```python
# Rank operations
df.select([
    pl.col("score").rank().alias("rank"),
    pl.col("score").rank(method="dense").alias("dense_rank"),
    pl.col("score").rank(method="ordinal").alias("ordinal_rank")
])

# Percent rank
df.with_columns([
    pl.col("score").rank().over("category").alias("rank_in_category")
])
```

### Rolling Operations

```python
# Rolling aggregations
df.select([
    pl.col("value").rolling_mean(window_size=7).alias("rolling_7day_mean"),
    pl.col("value").rolling_sum(window_size=7).alias("rolling_7day_sum"),
    pl.col("value").rolling_std(window_size=7).alias("rolling_7day_std")
])
```

### Shift and Lag

```python
# Shift values
df.select([
    pl.col("value").shift(1).alias("lag_1"),
    pl.col("value").shift(-1).alias("lead_1"),
    pl.col("value").shift(7).alias("lag_7")
])

# With grouping
df.with_columns([
    pl.col("value").shift(1).over("user_id").alias("user_lag_1")
])
```

## List and Array Operations

### Explode

```python
# Explode lists to rows
df.select([
    pl.col("tags").explode().alias("individual_tags")
])

# Count list elements
df.select([
    pl.col("tags").list.len().alias("tag_count")
])
```

### List Operations

```python
# List aggregations
df.select([
    pl.col("numbers").list.sum().alias("sum"),
    pl.col("numbers").list.mean().alias("mean"),
    pl.col("numbers").list.min().alias("min"),
    pl.col("numbers").list.max().alias("max")
])

# List slicing
df.select([
    pl.col("numbers").list.slice(0, 3).alias("first_three")
])

# List evaluation
df.select([
    pl.col("numbers").list.eval(pl.element() * 2).alias("doubled")
])
```

## DateTime Operations

### DateTime Extraction

```python
# Extract components
df.select([
    pl.col("timestamp").dt.year().alias("year"),
    pl.col("timestamp").dt.month().alias("month"),
    pl.col("timestamp").dt.day().alias("day"),
    pl.col("timestamp").dt.hour().alias("hour"),
    pl.col("timestamp").dt.minute().alias("minute"),
    pl.col("timestamp").dt.second().alias("second"),
    pl.col("timestamp").dt.millisecond().alias("millisecond")
])
```

### DateTime Arithmetic

```python
# Add/subtract durations
df.select([
    (pl.col("timestamp") + pl.duration(days=7)).alias("plus_7_days"),
    (pl.col("timestamp") - pl.duration(hours=1)).alias("minus_1_hour")
])

# Truncate
df.select([
    pl.col("timestamp").dt.truncate("1d").alias("date"),
    pl.col("timestamp").dt.truncate("1h").alias("hour")
])

# Difference
df.select([
    (pl.col("end_time") - pl.col("start_time")).alias("duration")
])
```

## Advanced Patterns

### Method Chaining

```python
# Build complex transformations
result = (df
    .filter(pl.col("active") == True)
    .select([
        "user_id",
        "category",
        pl.col("value").log().alias("log_value"),
        pl.col("value").rank().over("category").alias("category_rank")
    ])
    .sort("category_rank")
    .groupby("category")
    .agg([
        pl.col("log_value").mean().alias("avg_log_value"),
        pl.col("user_id").n_unique().alias("unique_users")
    ])
)
```

### Custom Expressions

```python
# Create reusable expressions
def weighted_sum(value_col, weight_col):
    return (pl.col(value_col) * pl.col(weight_col)).sum()

# Use in query
df.groupby("category").agg([
    weighted_sum("value", "weight").alias("weighted_total")
])
```

### Element-wise Operations

```python
# Apply function to each element
df.select([
    pl.col("text").map_elements(lambda x: x.upper(), return_dtype=pl.String)
])

# Apply with numpy
import numpy as np
df.select([
    pl.col("array").map_elements(np.sum, return_dtype=pl.Float64)
])
```

## Anti-Patterns

### Don't Use Python Loops

```python
# Bad: Python loop
for col in df.columns:
    df = df.with_columns(pl.col(col) * 2)

# Good: Expression with select
df.select([pl.col(col) * 2 for col in df.columns])
```

### Don't Break Expression Chains

```python
# Bad: Multiple operations
df = df.filter(pl.col("a") > 0)
df = df.select(["a", "b"])
df = df.groupby("c").agg(pl.col("a").sum())

# Good: Single chain
result = (df
    .filter(pl.col("a") > 0)
    .select(["a", "b"])
    .groupby("c")
    .agg(pl.col("a").sum())
)
```

## Performance Tips

### Use Categorical for Strings

```python
# Before: String comparisons
df.filter(pl.col("category") == "electronics")

# After: Categorical (faster)
df = df.with_columns([
    pl.col("category").cast(pl.Categorical)
])
df.filter(pl.col("category") == "electronics")
```

### Use Appropriate Data Types

```python
# Downcast integers
df = df.with_columns([
    pl.col("id").cast(pl.Int32),  # Instead of Int64
    pl.col("count").cast(pl.Int16)
])

# Use Boolean for flags
df = df.with_columns([
    pl.col("is_active").cast(pl.Boolean)
])
```

### Minimize Computations

```python
# Bad: Compute same expression multiple times
result1 = df.filter(pl.col("a") > 0).select(pl.sum("a"))
result2 = df.filter(pl.col("a") > 0).select(pl.mean("a"))

# Good: Filter once, compute multiple aggregations
filtered = df.filter(pl.col("a") > 0)
result1 = filtered.select(pl.sum("a"))
result2 = filtered.select(pl.mean("a"))
```
