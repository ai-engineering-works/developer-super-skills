# Dask Arrays

Dask Arrays provide parallel, larger-than-memory array computing with a NumPy-like API.

## Core Concepts

### What is a Dask Array?

A Dask Array is a collection of NumPy arrays chunked along one or more dimensions. It enables parallel computation on large arrays.

```python
import dask.array as da

# Create a large array (100GB logical, not loaded into memory)
x = da.random.random((100000, 100000), chunks=(1000, 1000))

# Operations are lazy
y = (x + x.T) / 2

# Compute result
result = y.compute()
```

### When to Use Dask Arrays

- **Large arrays**: Arrays larger than RAM (100GB+, TB-scale)
- **Parallel numerical computing**: Multi-core CPU utilization
- **Scientific computing**: NumPy-style operations at scale
- **Image processing**: Large image datasets
- **Weather/climate data**: Large multidimensional arrays

## Chunking Strategy

### Choosing Chunk Sizes

```python
# Good rule of thumb: chunks should be 10MB-1GB
x = da.random.random((100000, 100000), chunks=(1000, 1000))

# For 1D arrays
x = da.arange(1e9, chunks=1e8)  # 100M elements per chunk

# Check chunk size
x.chunksize  # (1000, 1000)

# Number of chunks
x.npartitions  # 10000
```

### Chunk Size Guidelines

- **Too small**: Excessive scheduler overhead (>100K tasks)
- **Too large**: Memory pressure, poor parallelism (<10 tasks)
- **Sweet spot**: 10-1000 chunks per dimension, 10MB-1GB per chunk

```python
# Calculate optimal chunk size
import psutil
memory_gb = psutil.virtual_memory().available / 1e9
optimal_chunk_size = int(memory_gb * 0.1 * 1e9)  # 10% of available memory
```

## Common Operations

### Array Creation

```python
# From numpy array
import numpy as np
x_np = np.arange(1e7)
x_da = da.from_array(x_np, chunks=1e6)

# From functions
x = da.zeros((10000, 10000), chunks=(1000, 1000))
x = da.ones((10000, 10000), chunks=(1000, 1000))
x = da.random.random((10000, 10000), chunks=(1000, 1000))

# From files
x = da.from_npyarray('large_array.npy', chunks=(1000, 1000))
```

### Element-wise Operations

```python
x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = da.random.random((10000, 10000), chunks=(1000, 1000))

# Arithmetic (lazy)
z = x + y
z = x * 2
z = x ** 2

# Trigonometric
z = da.sin(x)
z = da.exp(x)

# Logical
z = x > 0.5
z = da.logical_and(x > 0.3, y < 0.7)
```

### Reductions

```python
# Sum along axis
total = x.sum().compute()  # Full sum
row_sums = x.sum(axis=1).compute()  # Sum across columns
col_sums = x.sum(axis=0).compute()  # Sum across rows

# Other reductions
mean = x.mean().compute()
std = x.std().compute()
min_val = x.min().compute()
max_val = x.max().compute()

# Multiple reductions at once (more efficient)
mean, std = da.compute(x.mean(), x.std())
```

### Linear Algebra

```python
# Matrix multiplication
A = da.random.random((10000, 1000), chunks=(1000, 1000))
B = da.random.random((1000, 5000), chunks=(1000, 1000))
C = A @ B  # Matrix multiplication
C.compute()

# Transpose
C = A.T

# SVD (uses dask-ml or scipy)
U, s, V = da.linalg.svd(A)
```

### Slicing and Indexing

```python
x = da.random.random((10000, 10000), chunks=(1000, 1000))

# Slice (lazy)
subset = x[1000:2000, 500:1500]

# Fancy indexing
rows = da.array([1, 5, 10, 15])
cols = da.array([2, 7, 12, 17])
subset = x[rows, cols]

# Boolean indexing
mask = x > 0.5
filtered = x[mask]
```

## Performance Optimization

### Rechunking

```python
x = da.random.random((10000, 10000), chunks=(100, 10000))

# Rechunk for better parallelism
x_rechunked = x.rechunk((1000, 1000))

# Auto rechunk (Dask chooses optimal)
x_rechunked = x.rechunk('auto')
```

### Persist Intermediate Results

```python
# When reusing arrays
A = da.random.random((10000, 10000), chunks=(1000, 1000))
A_persisted = A.persist()

B = A_persisted + 1
C = A_persisted * 2

# Compute both efficiently
da.compute(B, C)
```

### Use Appropriate Algorithms

```python
# For reduction-friendly operations
x.sum(axis=0)  # Uses tree reduction

# For linear algebra
da.linalg.dot(A, B)  # Optimized for distributed

# For FFT
da.fft.fft(x)  # Parallel FFT implementation
```

## Common Patterns

### Image Processing

```python
import dask.image.imread

# Read multiple images
images = dask.image.imread.imread('images/*.tiff')

# Process all images
processed = images / 255.0  # Normalize
blurred = dask.image.gaussian_filter(images, sigma=2)

# Compute result
result = blurred.compute()
```

### Weather Data Processing

```python
# Open NetCDF files with xarray
import xarray as xr

ds = xr.open_dataset('weather_data*.nc', chunks={'time': 365, 'lat': 180, 'lon': 360})

# Compute climatology
climatology = ds.groupby('time.month').mean().compute()
```

### Monte Carlo Simulation

```python
# Parallel random number generation
n_simulations = 10_000_000
n_steps = 100

# Generate all random numbers at once
random_steps = da.random.random((n_simulations, n_steps), chunks=(100000, n_steps))

# Compute paths
paths = (random_steps * 2 - 1).cumsum(axis=1)

# Final distribution
final_values = paths[:, -1]
mean, std = da.compute(final_values.mean(), final_values.std())
```

### Convolution and Filtering

```python
from scipy.signal import convolve2d

# Apply filter to each chunk
def convolve_chunk(block, filter_kernel=None):
    return convolve2d(block, filter_kernel, mode='same')

# Use map_overlap for boundary-aware convolution
from dask.array.overlap import map_overlap

result = map_overlap(x, convolve_chunk,
                     depth=10,  # Overlap size
                     boundary='reflect',
                     filter_kernel=kernel)
```

## Advanced Operations

### Stacking and Concatenation

```python
# Stack along new axis
a = da.ones((10, 10), chunks=(5, 5))
b = da.zeros((10, 10), chunks=(5, 5))
stacked = da.stack([a, b], axis=0)  # Shape: (2, 10, 10)

# Concatenate along existing axis
concatenated = da.concatenate([a, b], axis=0)  # Shape: (20, 10)
```

### Broadcasting

```python
# Broadcast smaller array
x = da.random.random((1000, 1000), chunks=(100, 100))
y = da.random.random(1000, chunks=100)

# Broadcasting works like NumPy
result = x + y[:, None]  # y[:, None] has shape (1000, 1)
```

### Custom Reductions

```python
# Custom reduction using tree reduction
def custom_sum(block):
    return block.sum()

result = x.reduction(chunk=custom_sum,
                     aggregate=np.sum,
                     axis=0)
```

## Anti-Patterns

**Don't use small chunks**
```python
# Bad: Too many tasks
x = da.random.random((10000, 10000), chunks=(10, 10))  # 1M tasks

# Good: Reasonable chunk size
x = da.random.random((10000, 10000), chunks=(1000, 1000))  # 100 tasks
```

**Don't rechunk unnecessarily**
```python
# Bad: Expensive rechunking
x = x.rechunk((500, 500))
x = x.rechunk((1000, 1000))

# Good: Choose chunk size once
x = da.random.random((10000, 10000), chunks=(1000, 1000))
```

**Don't iterate over chunks**
```python
# Bad: Slow iteration
for block in x.blocks:
    result = block.compute()

# Good: Use map_blocks or vectorized operations
result = x.map_blocks(lambda block: block * 2)
```

## When to Use NumPy Instead

- Array < 1GB (fits in memory)
- Requires complex NumPy features not in Dask
- Rapid prototyping
- When computation is bound by single-core performance

## Integration with Other Libraries

### xarray (Labeled Arrays)

```python
import xarray as xr

# Create xarray with dask backend
da_xr = xr.DataArray(dask_array,
                     dims=['x', 'y', 'time'],
                     coords={'x': x_coords, 'y': y_coords, 'time': time_coords})

# Operations preserve labels
result = da_xr.groupby('time.month').mean()
```

### dask-image

```python
import dask.image.ndimage

# Parallel image processing
smoothed = dask.image.ndimage.gaussian_filter(images, sigma=2)
labeled, num_features = dask.image.ndimage.label(binary_images)
```
