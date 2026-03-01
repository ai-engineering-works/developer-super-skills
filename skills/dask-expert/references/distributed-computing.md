# Distributed Computing with Dask

Dask Distributed enables scaling computations from a single machine to a cluster of machines.

## Core Concepts

### Dask Distributed Architecture

```
Client (your code)
    ↓
Scheduler (coordinates work)
    ↓
Workers (execute tasks)
    ↓
Data (stored in worker memory)
```

### Components

- **Client**: User-facing interface for submitting work
- **Scheduler**: Coordinates task execution, maintains task graph
- **Workers**: Execute tasks, store data in memory
- **Dashboard**: Real-time monitoring at http://localhost:8787

## Setting Up a Cluster

### Local Cluster (Single Machine)

```python
from dask.distributed import Client

# Auto-detect resources
client = Client()  # Uses all cores, 8GB memory per worker

# Specify resources
client = Client(n_workers=4, threads_per_worker=2, memory_limit='4GB')

# Check dashboard URL
print(client.dashboard_link)  # http://localhost:8787
```

### SSH Cluster (Multiple Machines)

```python
from dask.distributed import SSHCluster

# Define worker addresses
cluster = SSHCluster([
    'scheduler-host',
    'worker1-host',
    'worker2-host',
    'worker3-host'
],
n_workers=3,
threads_per_worker=2,
memory_limit='8GB')

client = Client(cluster)
```

### Kubernetes Cluster

```python
from dask_kubernetes import KubeCluster

# Create cluster
cluster = KubeCluster(
    name='dask-cluster',
    n_workers=10,
    threads_per_worker=2,
    memory_limit='8Gi',
    env={'EXTRA_PIP_PACKAGES': 'pandas scikit-learn'}
)

client = Client(cluster)
```

### Cloud Clusters

```python
# AWS (using dask-cloudprovider)
from dask_cloudprovider.aws import FargateCluster

cluster = FargateCluster(
    n_workers=20,
    image='daskdev/dask:latest',
    memory_limit='16Gi',
    vpc='vpc-12345',
    subnets=['subnet-1', 'subnet-2']
)

# GCP
from dask_cloudprovider.gcp import GCPCluster

cluster = GCPCluster(
    n_workers=20,
    memory_limit='16Gi',
    region='us-central1'
)
```

## Scheduler Configuration

### Scheduler Types

```python
# Synchronous scheduler (default for local)
result = df.groupby('category').mean().compute(scheduler='synchronous')

# Threaded scheduler (good for NumPy/pandas operations)
result = df.groupby('category').mean().compute(scheduler='threads')

# Process scheduler (good for CPU-bound Python code)
result = df.groupby('category').mean().compute(scheduler='processes')

# Distributed scheduler (for clusters)
result = df.groupby('category').mean().compute(scheduler='distributed')
```

### Scheduler Selection Guide

| Workload | Recommended Scheduler | Reason |
|----------|---------------------|---------|
| NumPy/Pandas operations | `threads` | Low overhead, releases GIL |
| Pure Python code | `processes` | Bypass GIL |
| I/O bound | `threads` | Good for concurrent I/O |
| Multi-machine | `distributed` | Only option for clusters |

## Worker Configuration

### Memory Management

```python
# Set worker memory limit
worker = Worker(memory_limit='8GB')

# Memory spilling to disk
worker = Worker(memory_limit='8GB',
                memory_spill_disk_path='/tmp/dask-worker-space')

# Memory target (trigger spilling earlier)
worker = Worker(memory_limit='8GB',
                memory_target=0.6,  # 60% of limit
                memory_spill=0.7,    # 70% of limit
                memory_pause=0.8)    # 80% of limit
```

### Worker Resources

```python
# Custom resources (GPUs, etc.)
worker = Worker(nthreads=2,
                memory_limit='4GB',
                resources={'GPU': 1, 'custom_resource': 2})

# Submit tasks requiring resources
future = client.submit(func, resources={'GPU': 1})
```

## Data Distribution

### Data Locality

```python
# Read data distributed across cluster
df = dd.read_parquet('s3://bucket/data/*.parquet',
                     storage_options={'anon': False})

# Each worker reads local data
df = dd.read_csv('/data/worker-*.csv',
                 blocksize='256MB')
```

### Replication and Fault Tolerance

```python
# Replicate data across workers
df = df.repartition(npartitions=10)
df = df.persist(replication_factor=2)  # Store on 2 workers each

# Handle worker failures
with Client(asynchronous=True, timeout='30s') as client:
    # Retry failed tasks automatically
    result = df.groupby('category').mean().compute()
```

## Performance Monitoring

### Dashboard Metrics

Key metrics to monitor:
- **Task Stream**: Visualize task execution timeline
- **Progress Bar**: Overall computation progress
- **Memory**: Per-worker memory usage
- **CPU**: Per-worker CPU utilization
- **Network**: Data transfer between workers

### Programmatic Monitoring

```python
# Get worker status
worker_status = client.scheduler_info()['workers']

# Check memory usage
for worker, info in worker_status.items():
    print(f"{worker}: {info['memory']['used'] / 1e9:.2f} GB used")

# Get task statistics
task_stats = client.get_task_stream()
```

### Performance Diagnostics

```python
from dask.diagnostics import ProgressBar, Profiler, ResourceProfiler

# Progress bar
with ProgressBar():
    result = df.groupby('category').mean().compute()

# Profile execution time
with Profiler() as prof:
    result = df.groupby('category').mean().compute()

prof.visualize()

# Profile resource usage
with ResourceProfiler(dt=0.5) as rprof:
    result = df.groupby('category').mean().compute()

rprof.visualize()
```

## Advanced Patterns

### Dynamic Task Scheduling

```python
from dask import delayed

@delayed
def process_data(data):
    # Complex processing
    return processed_data

# Build dynamic task graph
results = []
for file in files:
    data = load_file(file)
    processed = process_data(data)
    results.append(processed)

# Compute
final = delayed(aggregate)(results)
final.compute()
```

### Actor Model (Futures)

```python
# Create distributed objects
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

# Create actors on workers
counters = [client.submit(Counter, actor=True) for _ in range(10)]

# Use actors
futures = [c[0].increment() for c in counters]
results = client.gather(futures)
```

### Scatter and Gather

```python
# Send data to workers
small_data = pd.DataFrame({'x': range(100)})
futures = client.scatter([small_data] * 10)

# Use scattered data in computation
results = [client.submit(process, future) for future in futures]

# Gather results
final_results = client.gather(results)
```

## Best Practices

### Cluster Sizing

```python
# Rule of thumb: 2-4 threads per worker
# Threads = CPU cores
# Workers = CPU cores / threads_per_worker

import psutil
n_cores = psutil.cpu_count(logical=False)

# For I/O bound
n_workers = n_cores // 2
threads_per_worker = 2

# For CPU bound
n_workers = n_cores
threads_per_worker = 1
```

### Task Granularity

```python
# Too fine-grained (millions of tiny tasks)
for i in range(1_000_000):
    futures.append(client.submit(func, i))  # Bad

# Better (coarse-grained tasks)
for batch in batches(data, batch_size=1000):
    futures.append(client.submit(process_batch, batch))  # Good
```

### Avoid Data Transfer

```python
# Bad: Data moves between workers
df = dd.read_parquet('s3://bucket/data/*.parquet')
result = df.merge(other_df)  # other_df on different worker

# Good: Keep data local
df = dd.read_parquet('s3://bucket/data/*.parquet')
result = df.map_partitions(process_partition)  # No transfer
```

## Security

### TLS/SSL

```python
from dask.distributed import Security

# Create security context
security = Security(
    tls_ca_file='/path/to/ca.crt',
    tls_scheduler_cert='/path/to/scheduler.crt',
    tls_scheduler_key='/path/to/scheduler.key',
    tls_worker_cert='/path/to/worker.crt',
    tls_worker_key='/path/to/worker.key'
)

# Connect with TLS
client = Client('scheduler-address:8786', security=security)
```

### Authentication

```python
# Simple token authentication
scheduler = Scheduler(authenticate=True,
                     dashboard_address=':8787')

# Kerberos authentication (requires dask-kerberos)
from dask_kerberos import KrbAuth
client = Client(scheduler_address, auth=KrbAuth())
```

## Troubleshooting

### Common Issues

**Out of Memory**
```python
# Reduce partition size
df = df.repartition(npartitions=100)

# Enable spilling
worker = Worker(memory_spill_disk_path='/tmp')

# Use iterative computation
for partition in df.partitions:
    result = partition.compute()
    process(result)
```

**Slow Communication**
```python
# Check network bandwidth
client.scheduler_info()

# Use compression
df.to_parquet('output/', compression='snappy')

# Minimize data transfer
df = df[df['category'] == 'A']  # Filter before shuffle
```

**Straggler Workers**
```python
# Rebalance partitions
df = df.repartition(npartitions=50, shuffle='tasks')

# Use adaptive work stealing
client = Client(adapt=True)
```

## Production Considerations

### Monitoring

```python
# Prometheus metrics
from dask.distributed import PrometheusCollector

scheduler = Scheduler(services={
    ('prometheus', 8000): PrometheusCollector()
})

# Logging
import logging
logging.basicConfig(level=logging.INFO)
```

### Graceful Shutdown

```python
# Ensure cluster cleanup
try:
    result = df.groupby('category').mean().compute()
finally:
    client.close()
    cluster.close()

# Context manager
with Client() as client:
    result = df.groupby('category').mean().compute()
```

### Scaling Strategy

```python
# Adaptive scaling (auto-scale workers)
cluster.adapt(minimum=2, maximum=50)

# Scale based on workload
if workload_heavy:
    cluster.scale(n=50)
else:
    cluster.scale(n=10)
```
