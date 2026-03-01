# Pandas Interoperability with Polars

Seamlessly convert between Pandas and Polars, and migrate existing code.

## Core Concepts

### Why Interoperability Matters

- **Incremental migration**: Gradually move from Pandas to Polars
- **Ecosystem compatibility**: Use libraries that only support Pandas
- **Team transition**: Mix of Pandas and Polars code
- **Learning path**: Leverage existing Pandas knowledge

## Converting Between Formats

### Pandas to Polars

```python
import pandas as pd
import polars as pl

# DataFrame conversion
df_pd = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "value": [100.0, 200.0, 300.0]
})

# Convert to Polars
df_pl = pl.from_pandas(df_pd)

# With schema override
df_pl = pl.from_pandas(df_pd, schema_overrides={
    "id": pl.Int32,
    "value": pl.Float32
})
```

### Polars to Pandas

```python
# Convert to Pandas
df_pd = df_pl.to_pandas()

# With specific dtypes
df_pd = df_pl.to_pandas(use_pyarrow_export=True)

# Convert specific columns
df_pd = df_pl[["name", "value"]].to_pandas()
```

### Series Conversion

```python
# Pandas Series to Polars Series
series_pd = pd.Series([1, 2, 3, 4, 5])
series_pl = pl.from_pandas(series_pd)

# Polars Series to Pandas Series
series_pl = pl.Series("values", [1, 2, 3, 4, 5])
series_pd = series_pl.to_pandas()
```

## API Mapping

### Common Operations

| Pandas | Polars | Notes |
|--------|--------|-------|
| `df['col']` | `df['col']` or `pl.col('col')` | Same syntax |
| `df[['a', 'b']]` | `df.select(['a', 'b'])` | Different method |
| `df[df['a'] > 0]` | `df.filter(pl.col('a') > 0)` | Expression-based |
| `df.groupby('col')` | `df.groupby('col')` | Same method |
| `df.merge(df2)` | `df.join(df2)` | Different name |
| `df.assign(a=1)` | `df.with_columns(pl.lit(1).alias('a'))` | Expression-based |
| `df.drop(['a'])` | `df.drop(['a'])` | Same syntax |
| `df.rename({'a': 'b'})` | `df.rename({'a': 'b'})` | Same syntax |
| `df.sort_values('a')` | `df.sort('a')` | Shorter name |
| `df.fillna(0)` | `df.fill_null(0)` | Different method |
| `df.dropna()` | `df.drop_nulls()` | Different method |

### Aggregation Mapping

```python
# Pandas
df.groupby('category').agg({
    'value': ['mean', 'sum', 'count']
})

# Polars
df.groupby('category').agg([
    pl.col('value').mean().alias('mean_value'),
    pl.col('value').sum().alias('sum_value'),
    pl.col('value').count().alias('count_value')
])
```

### Filtering Mapping

```python
# Pandas
df[(df['a'] > 0) & (df['b'] < 10)]

# Polars
df.filter((pl.col('a') > 0) & (pl.col('b') < 10))
```

### Column Operations

```python
# Pandas
df['new_col'] = df['old_col'] * 2

# Polars (in-place)
df = df.with_columns((pl.col('old_col') * 2).alias('new_col'))
```

## Migration Patterns

### Pattern 1: Reading Data

```python
# Pandas
df = pd.read_csv('data.csv')
df = df[df['date'] >= '2024-01-01']
result = df.groupby('category').agg({'value': 'sum'})

# Polars
result = (pl.scan_csv('data.csv')
    .filter(pl.col('date') >= '2024-01-01')
    .groupby('category')
    .agg(pl.sum('value'))
    .collect())
```

### Pattern 2: Data Cleaning

```python
# Pandas
df = df.dropna()
df['category'] = df['category'].astype('category')
df['id'] = df['id'].astype('int32')

# Polars
df = (df
    .drop_nulls()
    .with_columns([
        pl.col('category').cast(pl.Categorical),
        pl.col('id').cast(pl.Int32)
    ])
)
```

### Pattern 3: Feature Engineering

```python
# Pandas
df['rolling_avg'] = df['value'].rolling(7).mean()
df['lag_1'] = df['value'].shift(1)
df['pct_change'] = df['value'].pct_change()

# Polars
df = df.with_columns([
    pl.col('value').rolling_mean(7).alias('rolling_avg'),
    pl.col('value').shift(1).alias('lag_1'),
    pl.col('value').pct_change().alias('pct_change')
])
```

### Pattern 4: GroupBy Aggregations

```python
# Pandas
result = df.groupby('category').agg({
    'value': ['mean', 'std', 'min', 'max'],
    'id': 'nunique'
})
result.columns = ['_'.join(col).strip() for col in result.columns.values]

# Polars
result = df.groupby('category').agg([
    pl.col('value').mean().alias('value_mean'),
    pl.col('value').std().alias('value_std'),
    pl.col('value').min().alias('value_min'),
    pl.col('value').max().alias('value_max'),
    pl.col('id').n_unique().alias('id_nunique')
])
```

## Index Handling

### No Index in Polars

```python
# Pandas (with index)
df = df.set_index('date')
df.loc['2024-01-01':'2024-01-31']

# Polars (no index, use filter)
result = df.filter(
    pl.col('date').is_between('2024-01-01', '2024-01-31')
)
```

### Position-based Selection

```python
# Pandas
df.iloc[10:20]
df.loc[10:20]

# Polars
df[10:20]
df.slice(10, 10)
```

## Time Series Operations

### Resampling

```python
# Pandas
df.set_index('date').resample('1D').agg({'value': 'mean'})

# Polars
result = (df
    .sort('date')
    .groupby_dynamic('date', every='1d')
    .agg(pl.mean('value'))
)
```

### Rolling Operations

```python
# Pandas
df['rolling'] = df['value'].rolling(window=7, min_periods=1).mean()

# Polars
df = df.with_columns(
    pl.col('value').rolling_mean(window_size=7, min_periods=1).alias('rolling')
)
```

### Time-based Grouping

```python
# Pandas
df.groupby(pd.Grouper(key='date', freq='W')).agg({'value': 'sum'})

# Polars
result = (df
    .sort('date')
    .groupby_dynamic('date', every='1w')
    .agg(pl.sum('value'))
)
```

## String Operations

### Pandas vs Polars

```python
# Pandas
df['name'] = df['name'].str.upper()
df['email'] = df['email'].str.contains('@')
df['path'] = df['path'].str.split('/').str[0]

# Polars
df = df.with_columns([
    pl.col('name').str.to_uppercase(),
    pl.col('email').str.contains('@'),
    pl.col('path').str.split('/').list.get(0)
])
```

## Common Migration Issues

### Issue 1: In-Place Modification

```python
# Pandas (in-place)
df['new_col'] = df['old_col'] * 2

# Polars (immutable, returns new DataFrame)
df = df.with_columns((pl.col('old_col') * 2).alias('new_col'))
```

### Issue 2: Method Chaining

```python
# Pandas (often requires intermediate variables)
df = df[df['a'] > 0]
df = df.groupby('b').agg({'c': 'sum'})
df = df.reset_index()

# Polars (idiomatic chaining)
result = (df
    .filter(pl.col('a') > 0)
    .groupby('b')
    .agg(pl.sum('c'))
)
```

### Issue 3: Setting with Copy

```python
# Pandas (SettingWithCopyWarning)
df[df['a'] > 0]['b'] = 100  # Warning!

# Polars (no such issue)
df = df.with_columns(
    pl.when(pl.col('a') > 0)
    .then(pl.lit(100))
    .otherwise(pl.col('b'))
    .alias('b')
)
```

### Issue 4: Index Operations

```python
# Pandas (index-based)
df.loc[df['a'] > 0, 'b'] = 100

# Polars (no index, use expressions)
df = df.with_columns(
    pl.when(pl.col('a') > 0)
    .then(pl.lit(100))
    .otherwise(pl.col('b'))
    .alias('b')
)
```

## Hybrid Workflows

### Use Pandas for Specific Operations

```python
# Use Polars for fast I/O and filtering
df_pl = (pl.scan_parquet('large.parquet')
    .filter(pl.col('date') >= '2024-01-01')
    .collect())

# Convert to Pandas for specific library
df_pd = df_pl.to_pandas()
result = some_pandas_only_library(df_pd)

# Convert back to Polars
result_pl = pl.from_pandas(result)
```

### Incremental Migration

```python
# Phase 1: Convert data loading
# Old (Pandas)
df = pd.read_csv('data.csv')

# New (Polars)
df = pl.read_csv('data.csv').to_pandas()

# Phase 2: Convert transformations
# Old
df = df[df['value'] > 0]
result = df.groupby('category').agg({'value': 'sum'})

# New
df_pl = pl.from_pandas(df)
result = (df_pl
    .filter(pl.col('value') > 0)
    .groupby('category')
    .agg(pl.sum('value'))
    .to_pandas())

# Phase 3: Full Polars
result = (pl.scan_csv('data.csv')
    .filter(pl.col('value') > 0)
    .groupby('category')
    .agg(pl.sum('value'))
    .collect())
```

## Performance Comparison

### Benchmark Example

```python
import pandas as pd
import polars as pl
import time

# Create large dataset
data = {
    'id': range(10_000_000),
    'category': ['A', 'B', 'C'] * 3_333_333 + ['A'],
    'value': range(10_000_000)
}

# Pandas
df_pd = pd.DataFrame(data)
start = time.time()
result_pd = df_pd[df_pd['value'] > 5000000].groupby('category')['value'].sum()
pandas_time = time.time() - start

# Polars
df_pl = pl.DataFrame(data)
start = time.time()
result_pl = (df_pl
    .filter(pl.col('value') > 5000000)
    .groupby('category')
    .agg(pl.sum('value'))
)
polars_time = time.time() - start

print(f"Pandas: {pandas_time:.2f}s")
print(f"Polars: {polars_time:.2f}s")
print(f"Speedup: {pandas_time / polars_time:.1f}x")
```

## Type Mapping

### Pandas to Polars Types

| Pandas dtype | Polars dtype | Notes |
|--------------|-------------|-------|
| int64 | Int64 | Default |
| int32 | Int32 | Use for memory optimization |
| float64 | Float64 | Default |
| float32 | Float32 | Use for memory optimization |
| bool | Boolean | |
| object | String | Strings |
| category | Categorical | Low-cardinality strings |
| datetime64[ns] | Datetime | Timezones handled differently |
| timedelta64[ns] | Duration | |

### Type Conversion

```python
# Convert during pandas import
df_pl = pl.from_pandas(df_pd, schema_overrides={
    'id': pl.Int32,
    'category': pl.Categorical,
    'value': pl.Float32
})

# Convert after import
df_pl = df_pl.with_columns([
    pl.col('id').cast(pl.Int32),
    pl.col('category').cast(pl.Categorical)
])
```

## Library Compatibility

### Matplotlib/Seaborn

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Convert Polars to Pandas for plotting
df_pl = pl.read_parquet('data.parquet')
df_pd = df_pl.to_pandas()

# Use plotting library
sns.scatterplot(data=df_pd, x='a', y='b')
plt.show()
```

### Scikit-learn

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Convert to Pandas/NumPy for sklearn
df_pl = pl.read_parquet('data.parquet')
X = df_pl.drop('target').to_numpy()
y = df_pl['target'].to_numpy()

# Use sklearn
X_train, X_test, y_train, y_test = train_test_split(X, y)
model = RandomForestClassifier()
model.fit(X_train, y_train)
```

### Statsmodels

```python
import statsmodels.api as sm

# Convert to Pandas for statsmodels
df_pd = df_pl.to_pandas()
X = df_pd[['feature1', 'feature2']]
y = df_pd['target']

# Add constant and fit
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
```

## Best Practices

1. **Convert at boundaries**: Minimize conversions, do them at I/O boundaries
2. **Use lazy evaluation**: For complex operations, use Polars lazy API
3. **Leverage types**: Use Polars type system for optimization
4. **Profile**: Benchmark Pandas vs Polars for your specific workload
5. **Hybrid approach**: Use Pandas for ecosystem compatibility, Polars for performance
6. **Incremental migration**: Migrate piece by piece, not all at once
7. **Keep both**: It's okay to use both libraries in the same codebase
