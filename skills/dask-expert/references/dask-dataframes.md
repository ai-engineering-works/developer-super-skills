# Dask DataFrames

Dask DataFrames provide a parallel and distributed version of pandas, designed for datasets that don't fit in memory.

## Core Concepts

### What is a Dask DataFrame?

A Dask DataFrame is a collection of pandas DataFrames partitioned along the index. It mimics the pandas API but operates lazily and in parallel.

```python
import dask.dataframe as dd

# Read a large CSV (doesn't load into memory yet)
df = dd.read_csv('large_dataset/*.csv', blocksize='256MB')

# Operations are lazy - build task graph
result = df.groupby('category').agg({'value': 'mean', 'id': 'count'})

# Execute computation
result.compute()
```

### When to Use Dask DataFrames

- **Dataset larger than RAM**: 10GB+ CSV files, database queries
- **Parallel processing**: Multi-core CPU utilization
- **ETL pipelines**: Data transformation workflows
- **pandas scaling**: When pandas becomes too slow or memory-intensive

## Partitioning Strategy

### Block Size Selection

Choose block size based on:
- **Available memory**: Each partition must fit in worker memory
- **Task overhead**: Too many partitions = scheduler overhead
- **Data locality**: Match to underlying storage (HDFS blocks, S3 objects)

```python
# Good defaults
df = dd.read_csv('data/*.csv', blocksize='256MB')  # 256MB per partition

# For very large files
df = dd.read_csv('huge/*.csv', blocksize='1GB')

# Check partition count
df.npartitions  # Should be 10-100 for most workflows
```

### Repartitioning

```python
# Reduce partitions (too many small partitions)
df = df.repartition(npartitions=10)

# Increase partitions (too few large partitions)
df = df.repartition(npartitions=100)

# Repartition by column (for shuffling operations)
df = df.shuffle('category', npartitions=50)
```

## Common Operations

### Filtering and Selection

```python
# Filter (lazy - builds task graph)
filtered = df[df['value'] > 100]

# Multiple conditions
filtered = df[(df['value'] > 100) & (df['category'] == 'A')]

# Select columns
selected = df[['id', 'value', 'category']]

# Compute only when needed
result = filtered.compute()
```

### GroupBy and Aggregation

```python
# Simple aggregation
df.groupby('category')['value'].mean().compute()

# Multiple aggregations
result = df.groupby('category').agg({
    'value': ['mean', 'sum', 'count'],
    'id': 'nunique'
}).compute()

# Custom aggregations
def custom_agg(series):
    return series.quantile(0.75) - series.quantile(0.25)

df.groupby('category')['value'].agg(custom_agg).compute()
```

### Merge and Join

```python
# Inner join
merged = dd.merge(df1, df2, on='id')

# Left join with different column names
merged = dd.merge(df1, df2, left_on='id1', right_on='id2', how='left')

# Broadcast join (small dataframe to large)
small_df_pandas = small_df.compute()
merged = df.merge(small_df_pandas, on='category')
```

### Apply and Map

```python
# Apply function to each row (avoid if possible)
df['new_column'] = df['old_column'].apply(lambda x: x * 2, meta=('new_column', 'i8'))

# Prefer vectorized operations
df['new_column'] = df['old_column'] * 2

# Apply to each partition (more efficient)
def process_partition(partition):
    # Complex processing on entire partition
    return partition processed

df.map_partitions(process_partition, meta=df.dtypes)
```

## Performance Optimization

### Use Index for Operations

```python
# Set index for faster grouping/filtering
df = df.set_index('date')

# Filter by index (fast)
df.loc['2024-01-01':'2024-01-31']

# Group by index (fast)
df.groupby(level=0).mean()
```

### Avoid `.compute()` Until Necessary

```python
# Bad: Multiple compute calls
result1 = df[df['value'] > 100].compute()
result2 = result1.groupby('category').mean().compute()

# Good: Single compute
result = (df[df['value'] > 100]
          .groupby('category')
          .mean()
          .compute())
```

### Persist Intermediate Results

```python
# When reusing filtered data multiple times
filtered = df[df['value'] > 100].persist()  # Keeps in memory

result1 = filtered.groupby('category').mean().compute()
result2 = filtered.groupby('date').sum().compute()
```

## Working with File Formats

### CSV

```python
# Read CSV
df = dd.read_csv('data/*.csv',
                 blocksize='256MB',
                 parse_dates=['date'],
                 dtype={'id': 'int64', 'value': 'float64'})

# Write CSV
df.to_csv('output/*.csv', index=False)
```

### Parquet (Recommended)

```python
# Read Parquet (faster, preserves types)
df = dd.read_parquet('data/*.parquet', engine='pyarrow')

# Write Parquet
df.to_parquet('output/', engine='pyarrow', compression='snappy')
```

### Multiple Files

```python
# Read multiple CSVs with glob
df = dd.read_csv('data/**/*.csv', blocksize='256MB')

# Read from multiple paths
df = dd.read_csv(['data1/*.csv', 'data2/*.csv'])
```

## Memory Management

### Reduce Memory Usage

```python
# Downcast numeric types
df['id'] = df['id'].astype('int32')
df['value'] = df['value'].astype('float32')

# Use categorical for strings
df['category'] = df['category'].astype('category')

# Drop unnecessary columns early
df = df[['id', 'value', 'category']]
```

### Process in Chunks

```python
# Process large dataset in chunks
for partition in df.partitions:
    chunk = partition.compute()
    # Process chunk
    process_chunk(chunk)
```

## Common Patterns

### ETL Pipeline

```python
# Read, transform, write
(df
 .read_csv('input/*.csv')
 .pipe(clean_data)
 .pipe(transform_data)
 .to_parquet('output/', compression='snappy'))
```

### Time Series Processing

```python
# Resample after setting datetime index
df = dd.read_csv('timeseries.csv', parse_dates=['timestamp'])
df = df.set_index('timestamp')

# Daily resampling
daily = df.resample('1D').agg({
    'value': 'mean',
    'id': 'count'
}).compute()
```

### Machine Learning Features

```python
# Create features for ML
features = (df
            .groupby('user_id')
            .agg({
                'value': ['mean', 'std', 'min', 'max'],
                'timestamp': ['min', 'max']
            })
            .compute())
```

## Anti-Patterns

**Don't use `iterrows()` or `itertuples()`**
```python
# Bad: Slow row iteration
for row in df.iterrows():
    process(row)

# Good: Vectorized operations
result = df.apply(lambda x: x * 2, axis=1, meta=df.dtypes)
```

**Don't compute too early**
```python
# Bad: Breaks lazy evaluation
filtered = df[df['value'] > 100].compute()
result = filtered.groupby('category').mean()

# Good: Keep lazy
result = df[df['value'] > 100].groupby('category').mean().compute()
```

## When to Use Pandas Instead

- Dataset < 1GB (fits in memory)
- Heavy use of pandas-specific features
- Rapid prototyping and exploration
- Complex index operations not supported by Dask
- When Dask's overhead outweighs benefits
