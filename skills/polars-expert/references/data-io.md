# Data I/O with Polars

Efficient reading and writing data in various formats with Polars.

## Core Concepts

### I/O Best Practices

1. **Prefer Parquet**: Best format for Polars (columnar, statistics, compression)
2. **Use Lazy I/O**: Scan files without loading into memory
3. **Select Columns**: Read only needed columns
4. **Use Statistics**: Enable row group skipping in Parquet
5. **Batch Processing**: Process large files in chunks

## Reading Data

### CSV

```python
import polars as pl

# Basic CSV reading
df = pl.read_csv("data.csv")

# With options
df = pl.read_csv(
    "data.csv",
    separator=",",
    has_header=True,
    infer_schema_length=10000,  # Rows to infer schema
    ignore_errors=True,
    null_values=["NA", "null", ""],
    parse_dates=True,
    dtypes={
        "id": pl.Int32,
        "category": pl.Categorical
    }
)

# Lazy CSV reading
lazy_df = pl.scan_csv("large_file.csv")
```

### CSV Options

```python
# Custom separator
df = pl.read_csv("data.tsv", separator="\t")

# Skip rows
df = pl.read_csv("data.csv", skip_rows=1)

# Column projection
df = pl.read_csv("data.csv", columns=["id", "name", "value"])

# Row limit
df = pl.read_csv("data.csv", n_rows=1000)

# Encoding
df = pl.read_csv("data.csv", encoding="utf-8-lossy")  # Handle invalid UTF-8
```

### Parquet (Recommended)

```python
# Basic Parquet reading
df = pl.read_parquet("data.parquet")

# Lazy Parquet reading (best for large files)
lazy_df = pl.scan_parquet("large_file.parquet")

# Read specific columns
df = pl.read_parquet("data.parquet", columns=["id", "name", "value"])

# Read with row groups
df = pl.read_parquet(
    "data.parquet",
    row_index_name="row_num",
    row_index_offset=0
)

# Multiple files
df = pl.read_parquet("data/*.parquet")

# With cloud storage (requires fsspec)
df = pl.read_parquet(
    "s3://bucket/data.parquet",
    storage_options={
        "aws_access_key_id": "key",
        "aws_secret_access_key": "secret"
    }
)
```

### Parquet with Statistics

```python
# Filter using statistics (fast)
result = (pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .filter(pl.col("category") == "electronics")
    .collect())
# Only reads relevant row groups
```

### JSON

```python
# JSON Lines (NDJSON)
df = pl.read_ndjson("data.jsonl")

# Lazy JSON Lines
lazy_df = pl.scan_ndjson("large_file.jsonl")

# Regular JSON (single object)
df = pl.read_json("data.json")
```

### Excel

```python
# Read Excel
df = pl.read_excel(
    "data.xlsx",
    sheet_name="Sheet1",
    has_header=True
)

# Read multiple sheets
df1 = pl.read_excel("data.xlsx", sheet_name="Sheet1")
df2 = pl.read_excel("data.xlsx", sheet_name="Sheet2")
```

### Database Connections

```python
# Using SQLAlchemy
import sqlalchemy

engine = sqlalchemy.create_engine("postgresql://user:pass@localhost/db")
df = pl.read_database("SELECT * FROM table", engine)

# Using specific connection
import psycopg2
conn = psycopg2.connect("dbname=test user=postgres")
df = pl.read_database("SELECT * FROM table", conn)
```

### Arrow/IPC

```python
# Read Arrow IPC format
df = pl.read_ipc("data.arrow")
df = pl.read_ipc("data.feather")

# Stream Arrow IPC
lazy_df = pl.scan_ipc("large_data.arrow")
```

## Writing Data

### CSV

```python
# Basic CSV writing
df.write_csv("output.csv")

# With options
df.write_csv(
    "output.csv",
    separator=",",
    has_header=True,
    quote_style="always",  # or "necessary", "non_numeric"
    null_value="NA",
    include_bom=False  # BOM for Excel compatibility
)

# Batch writing
for partition, df_batch in enumerate(df.partition_by("category")):
    df_batch.write_csv(f"output_{partition}.csv")
```

### Parquet

```python
# Basic Parquet writing
df.write_parquet("output.parquet")

# With compression
df.write_parquet(
    "output.parquet",
    compression="snappy",  # snappy, gzip, brotli, lz4, zstd
    compression_level=3
)

# With statistics (for filtering)
df.write_parquet(
    "output.parquet",
    statistics=True,  # Enable min/max statistics
    use_pyarrow=True  # Use PyArrow engine
)

# Partition by column
df.write_parquet(
    "output_dir/",
    partition_by=["year", "month"],
    use_pyarrow=True
)

# Write to cloud
df.write_parquet(
    "s3://bucket/output.parquet",
    storage_options={
        "aws_access_key_id": "key",
        "aws_secret_access_key": "secret"
    }
)
```

### JSON

```python
# JSON Lines (NDJSON)
df.write_ndjson("output.jsonl")

# Regular JSON
df.write_json("output.json", pretty=True)

# Row-oriented JSON
df.write_json("output.json", orient="row")
```

### Arrow/IPC

```python
# Write Arrow IPC
df.write_ipc("output.arrow")
df.write_ipc("output.feather")

# Streamed IPC (for large data)
df.write_ipc("output.arrow", compression="lz4")
```

### Database

```python
# Write to database
import sqlalchemy

engine = sqlalchemy.create_engine("postgresql://user:pass@localhost/db")
df.write_database(
    "table_name",
    engine,
    if_table_exists="replace"  # or "append", "fail"
)
```

### Excel

```python
# Write Excel
df.write_excel(
    "output.xlsx",
    sheet_name="Sheet1",
    position="A1"
)

# Multiple sheets
df1.write_excel("output.xlsx", sheet_name="Sheet1")
df2.write_excel("output.xlsx", sheet_name="Sheet2", worksheet="append")
```

## Advanced I/O Patterns

### Lazy to Lazy

```python
# Read, process, write without materializing
(pl.scan_parquet("input.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .select(["id", "category", "value"])
    .sink_parquet("output.parquet"))
```

### Streaming Processing

```python
# Process large dataset with streaming
(pl.scan_parquet("huge_input.parquet")
    .groupby("category")
    .agg(pl.all().sum())
    .sink_parquet("huge_output.parquet"))
```

### Batch Processing

```python
# Process in batches
batch_size = 100000
n_batches = len(df) // batch_size + 1

for i in range(n_batches):
    start = i * batch_size
    end = (i + 1) * batch_size
    batch = df[start:end]
    process_batch(batch)
```

### Parallel File Reading

```python
# Read multiple files in parallel
import glob

files = glob.glob("data/*.parquet")
lazy_df = pl.scan_parquet(files)  # Parallel reading
```

## Cloud Storage

### S3 (AWS)

```python
# Read from S3
df = pl.read_parquet(
    "s3://bucket/path/file.parquet",
    storage_options={
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY",
        "region": "us-west-2"
    }
)

# Write to S3
df.write_parquet(
    "s3://bucket/path/output.parquet",
    storage_options={
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY"
    }
)

# Using IAM role (recommended)
df = pl.read_parquet(
    "s3://bucket/path/file.parquet",
    storage_options={"region": "us-west-2"}
)
```

### GCS (Google Cloud)

```python
# Read from GCS
df = pl.read_parquet(
    "gs://bucket/path/file.parquet",
    storage_options={
        "token": "your_service_account_token"
    }
)
```

### Azure Blob

```python
# Read from Azure
df = pl.read_parquet(
    "az://bucket/path/file.parquet",
    storage_options={
        "account_name": "your_account",
        "account_key": "your_key"
    }
)
```

## I/O Performance Tips

### CSV Optimization

```python
# Faster CSV reading
df = pl.read_csv(
    "large_file.csv",
    infer_schema_length=0,  # Skip schema inference (specify manually)
    has_header=False,  # Skip header processing
    n_threads=8  # Use more threads
)
```

### Parquet Optimization

```python
# Optimize Parquet write for performance
df.write_parquet(
    "output.parquet",
    compression="snappy",  # Faster than gzip
    statistics=True,  # Enable for faster filtering
    use_pyarrow=True,  # Generally faster
    row_group_size=100000  # Optimal row group size
)
```

### Memory-Mapped Files

```python
# Memory-mapped Parquet (for very large files)
df = pl.read_parquet("huge.parquet", memory_map=True)
```

## Format Comparison

| Format | Read Speed | Write Speed | Size | Statistics | Compression |
|--------|-----------|-------------|-------|-----------|-------------|
| CSV | Slow | Slow | Large | No | None |
| JSON | Slow | Slow | Large | No | None |
| Parquet | Fast | Medium | Small | Yes | Yes |
| IPC/Arrow | Fastest | Fast | Medium | No | Optional |
| Feather | Fast | Fast | Medium | No | Optional |

### When to Use Each Format

**Use Parquet when:**
- Long-term storage
- Need columnar access
- Need statistics for filtering
- Large datasets

**Use CSV when:**
- Data exchange with other tools
- Human readability
- Small datasets

**Use IPC/Arrow when:**
- Temporary storage
- Fastest I/O needed
- Interoperability with Arrow ecosystem

**Use JSON when:**
- API responses
- Web applications
- Schemaless data

## Error Handling

### Handle Invalid Data

```python
# Skip errors
df = pl.read_csv("data.csv", ignore_errors=True)

# Specify null values
df = pl.read_csv(
    "data.csv",
    null_values=["NA", "null", "N/A", ""]
)

# Specify schema (avoid inference errors)
df = pl.read_csv(
    "data.csv",
    dtypes={
        "id": pl.Int32,
        "name": pl.String,
        "value": pl.Float64
    }
)
```

### Encoding Issues

```python
# Handle encoding errors
df = pl.read_csv("data.csv", encoding="utf-8-lossy")

# Try different encodings
try:
    df = pl.read_csv("data.csv", encoding="utf-8")
except:
    df = pl.read_csv("data.csv", encoding="latin-1")
```

### Missing Files

```python
# Check file existence
import os

if os.path.exists("data.parquet"):
    df = pl.read_parquet("data.parquet")
else:
    df = pl.DataFrame(schema=expected_schema)
```

## Integration Patterns

### Pandas Interop

```python
import pandas as pd

# Pandas → Polars
df_pd = pd.read_csv("data.csv")
df_pl = pl.from_pandas(df_pd)

# Polars → Pandas
df_pl = pl.read_parquet("data.parquet")
df_pd = df_pl.to_pandas()
```

### PyArrow Interop

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Arrow → Polars
table = pa.read_table("data.parquet")
df = pl.from_arrow(table)

# Polars → Arrow
df = pl.read_parquet("data.parquet")
table = df.to_arrow()
```

### NumPy Interop

```python
import numpy as np

# NumPy → Polars
arr = np.array([[1, 2], [3, 4]])
df = pl.DataFrame(arr, schema=["a", "b"])

# Polars → NumPy
df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
arr = df.to_numpy()
```
