# Dask Task Graphs and Optimization

Understanding and optimizing Dask task graphs is key to achieving high performance with Dask.

## Core Concepts

### What is a Task Graph?

A task graph (also called a dependency graph) is a directed acyclic graph (DAG) where:
- **Nodes**: Individual computations (tasks)
- **Edges**: Dependencies between tasks

```python
import dask.array as da

x = da.ones((10000, 10000), chunks=(1000, 1000))
y = x + 1
z = y * 2

# Visualize task graph
z.visualize(filename='task_graph.png')
```

### Why Lazy Evaluation Matters

Lazy evaluation allows Dask to:
1. **Build the full computation plan** before executing
2. **Optimize** the plan (reorder, fuse tasks)
3. **Execute** only what's needed
4. **Parallelize** effectively

## Task Graph Optimization

### Task Fusion

Dask automatically fuses small tasks to reduce overhead:

```python
# Without fusion (many small tasks)
result = (x + 1) * 2 - 3

# With fusion (fewer larger tasks)
# Dask combines operations into single tasks per chunk
```

### Controlling Fusion

```python
# Disable fusion (for debugging)
import dask
dask.config.set({'optimization.fuse.active': False})

# Adjust fusion parameters
dask.config.set({
    'optimization.fuse.max-height': 10,  # Max fused tasks
    'optimization.fuse.max-width': 5,    # Max parallel fused tasks
    'optimization.fuse.subgraphs': True  # Fuse subgraphs
})
```

### Recomputation Avoidance

```python
# Bad: Recomputes x multiple times
result1 = (x + 1).compute()
result2 = (x + 2).compute()

# Good: Compute once, reuse
x_persisted = x.persist()
result1 = (x_persisted + 1).compute()
result2 = (x_persisted + 2).compute()
```

## Common Patterns

### Reduction Operations

```python
# Tree reduction pattern
x = da.random.random(1_000_000_000, chunks=1_000_000)

# Efficient tree reduction (O(log n) steps)
sum_result = x.sum().compute()

# Compare with linear reduction (slow)
# sum_result = x.map_partitions(lambda x: x.sum()).sum().compute()
```

### Map-Reduce Pattern

```python
# Map: Process each partition
def map_func(partition):
    return partition * 2

mapped = df.map_partitions(map_func)

# Reduce: Aggregate results
result = mapped.groupby('category').sum().compute()
```

### Shuffle Operations

```python
# Expensive: Requires data movement
df = df.set_index('category')  # Shuffle

# Better: Avoid shuffle when possible
result = df.groupby('category').sum()  # Delay shuffle

# Best: Use hashing for categorical data
df['category'] = df['category'].astype('category')
result = df.groupby('category').sum()
```

## Performance Tuning

### Graph Complexity Analysis

```python
# Check task count
len(x.__dask_graph__())  # Number of tasks

# Visualize complexity
x.visualize(optimize_graph=True, filename='optimized.png')
x.visualize(optimize_graph=False, filename='unoptimized.png')

# Profile task execution
from dask.diagnostics import ProgressBar, Profiler

with ProgressBar() and Profiler() as prof:
    result = x.compute()

prof.visualize(filename='profile.png')
```

### Reducing Task Count

```python
# Bad: Too many small chunks
x = da.random.random(10000, chunks=10)  # 1000 tasks

# Good: Fewer, larger chunks
x = da.random.random(10000, chunks=1000)  # 10 tasks

# Use rechunk to consolidate
x = x.rechunk(1000)
```

### Optimizing Dependencies

```python
# Bad: Chain of dependencies
x = da.ones(1000, chunks=100)
y = x + 1
z = y + 1
w = z + 1

# Good: Combine operations
w = x + 3

# Or use persist to break chain
x_persisted = x.persist()
w = (x_persisted + 1).persist()
w = (w + 1).persist()
w = (w + 1).persist()
```

## Advanced Optimization

### Custom Task Scheduling

```python
from dask.threaded import get as threaded_get

# Use threaded scheduler for NumPy operations
result = x.compute(scheduler=threaded_get)

# Use multiprocessing for Python operations
from dask.multiprocessing import get as mp_get
result = x.compute(scheduler=mp_get)
```

### Priority Scheduling

```python
# Assign priority to critical tasks
def high_priority_task():
    return important_result

future = client.submit(high_priority_task,
                       priority=10)  # Higher = more priority

normal_future = client.submit(normal_task, priority=0)
```

### Worker Affinity

```python
# Schedule tasks on same worker
x = client.scatter(data)

# Subsequent tasks run on same worker
y = client.submit(process, x)  # Runs on worker holding x
```

## Anti-Patterns

### Too Small Tasks

```python
# Bad: Millions of tiny tasks
x = da.arange(1_000_000_000, chunks=1)  # 1B tasks

# Good: Fewer, larger tasks
x = da.arange(1_000_000_000, chunks=10_000_000)  # 100 tasks
```

### Unnecessary Computation

```python
# Bad: Computing intermediate results
filtered = df[df['value'] > 0].compute()  # Executes immediately
result = filtered.groupby('category').mean().compute()

# Good: Lazy until final result
result = df[df['value'] > 0].groupby('category').mean().compute()
```

### Ignoring Caching

```python
# Bad: Recomputing expensive operation
for i in range(10):
    result = expensive_operation(df).compute()

# Good: Cache expensive operation
cached = expensive_operation(df).persist()
for i in range(10):
    result = cached.compute()
```

## Monitoring and Debugging

### Dashboard Task Stream

The task stream view in the dashboard shows:
- Task execution timeline
- Worker assignments
- Data movement between workers
- Task duration

### Task Statistics

```python
# Get task execution info
from distributed import Client

client = Client()
future = client.submit(func, *args)

# Task info
task_info = client.task_info(future.key)

# All task history
history = client.get_task_stream(future=None)
```

### Graph Visualization

```python
# Visualize graph structure
result.visualize(filename='graph.png',
                 optimize_graph=True,
                 color='order',
                 node_attributes={'time': lambda x: x})

# Visualize with annotations
result.visualize(filename='annotated.png',
                 cmap='autumn',
                 collapse_functions=True,
                 verbose=True)
```

## Optimization Checklist

When optimizing slow Dask computations:

1. **Check partition count**: Too many (slow) or too few (poor parallelism)?
2. **Visualize task graph**: Unexpected dependencies?
3. **Use dashboard**: Are workers fully utilized?
4. **Check for shuffles**: Can you avoid data movement?
5. **Persist intermediates**: Are you recomputing?
6. **Fuse tasks**: Is fusion disabled?
7. **Choose right scheduler**: Threads vs processes vs distributed?

## Performance Tips

### For DataFrames

```python
# Use categorical for grouping
df['category'] = df['category'].astype('category')

# Set index before groupby
df = df.set_index('category')

# Use efficient dtypes
df['id'] = df['id'].astype('int32')
```

### For Arrays

```python
# Choose appropriate chunk size
chunks = 'auto'  # Let Dask choose

# Or calculate based on memory
import psutil
memory_per_worker = psutil.virtual_memory().available / n_workers
chunk_bytes = memory_per_worker // 10  # Use 10% per chunk
```

### For Distributed

```python
# Minimize data transfer
client.scatter(data, broadcast=True)  # Send to all workers

# Use actor pattern for stateful operations
actor = client.submit(StatefulClass, actor=True)

# Use asynchronous API
async def process():
    futures = [client.submit(func, i) for i in range(100)]
    results = await client.gather(futures)
    return results
```

## Case Studies

### Case 1: Slow GroupBy

**Problem**: GroupBy takes hours on large dataset.

**Solution**:
```python
# Before: 100M rows, 1000 partitions
df = dd.read_parquet('large_data.parquet')
result = df.groupby('category').agg({'value': 'mean'}).compute()  # Slow

# After: Optimize categories and partitions
df = dd.read_parquet('large_data.parquet')
df = df.categorize(columns=['category'])  # Use categorical
df = df.repartition(npartitions=100)  # Fewer partitions
result = df.groupby('category').agg({'value': 'mean'}).compute()  # 10x faster
```

### Case 2: Memory Issues

**Problem**: Workers run out of memory during processing.

**Solution**:
```python
# Before: Process entire dataset at once
result = df.map_partitions(expensive_func).compute()  # OOM

# After: Process in batches with cleanup
for partition in df.partitions:
    result = partition.map_partitions(expensive_func).compute()
    process_and_discard(result)  # Don't accumulate
```

### Case 3: Straggler Workers

**Problem**: Some workers finish much later than others.

**Solution**:
```python
# Before: Uneven data distribution
result = df.groupby('category').mean().compute()  # Some categories skewed

# After: Rebalance data
df = df.shuffle('category', npartitions=100)  # Redistribute
result = df.groupby('category').mean().compute()  # Balanced
```
