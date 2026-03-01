# Machine Learning with Dask

Dask integrates with popular ML libraries to enable distributed machine learning at scale.

## Core Concepts

### Why Dask for ML?

- **Scale out**: Train on datasets larger than memory
- **Parallel training**: Multi-core and distributed training
- **Hyperparameter tuning**: Parallel search across parameters
- **Familiar APIs**: Scikit-learn, XGBoost, and other popular libraries

## Scikit-learn Integration

### dask-ml Overview

`dask-ml` provides distributed versions of scikit-learn estimators:

```python
import dask.array as da
from dask_ml.linear_model import LinearRegression
from dask_ml.model_selection import train_test_split

# Create large dataset
X = da.random.random((1_000_000, 100), chunks=(100_000, 100))
y = da.random.random(1_000_000, chunks=100_000)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model (distributed)
model = LinearRegression()
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)
score = model.score(X_test, y_test)
```

### Incremental Learning

For algorithms that don't support parallel learning:

```python
from dask_ml.wrappers import Incremental
from sklearn.linear_model import SGDClassifier

# Wrap incremental estimator
inc_model = Incremental(SGDClassifier(),
                        scoring='accuracy',
                        assume_equal_features=True)

# Train incrementally
inc_model.fit(X_train, y_train, classes=[0, 1, 2])

# Predict
predictions = inc_model.predict(X_test)
```

### Parallel Preprocessing

```python
from dask_ml.preprocessing import StandardScaler
from dask_ml.decomposition import PCA

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dimensionality reduction
pca = PCA(n_components=10)
X_reduced = pca.fit_transform(X_scaled)
```

## Model Selection

### Grid Search (Parallel)

```python
from dask_ml.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

# Define parameter grid
param_grid = {
    'n_estimators': [100, 200, 500],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10]
}

# Create base estimator
base_model = RandomForestClassifier(random_state=42)

# Grid search (parallel across workers)
grid_search = GridSearchCV(base_model, param_grid, cv=5, scoring='accuracy')

# Fit (distributes across cluster)
grid_search.fit(X_train, y_train)

# Best parameters
print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_}")
```

### Random Search

```python
from dask_ml.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

# Define distributions
param_distributions = {
    'n_estimators': randint(100, 500),
    'max_depth': randint(10, 50),
    'learning_rate': uniform(0.01, 0.1)
}

# Random search
random_search = RandomizedSearchCV(
    base_model,
    param_distributions,
    n_iter=50,  # 50 random combinations
    cv=5,
    scoring='accuracy'
)

random_search.fit(X_train, y_train)
```

### Hyperband (Successive Halving)

```python
from dask_ml.model_selection import HyperbandSearchCV
import numpy as np

# Hyperband for efficient resource allocation
hyperband = HyperbandSearchCV(
    base_model,
    param_grid,
    max_iter=100,  # Max iterations per model
    patience=10    # Early stopping patience
)

hyperband.fit(X_train, y_train)
```

## XGBoost Integration

### Distributed Training

```python
import dask.dataframe as dd
import xgboost as xgb
from xgboost.dask import DaskXGBClassifier

# Load data
df = dd.read_parquet('training_data.parquet')
X = df.drop('target', axis=1)
y = df['target']

# Train on worker data (no data movement)
model = DaskXGBClassifier(
    n_estimators=1000,
    max_depth=6,
    learning_rate=0.1,
    n_jobs=-1  # Use all threads
)

model.fit(X, y)

# Predict
predictions = model.predict(X_test)
```

### Cross-Validation

```python
from xgboost.dask import DaskXGBClassifier

# Create DaskDMatrix for efficiency
dtrain = xgb.dask.DaskDMatrix(client, X_train, y_train)
dtest = xgb.dask.DaskDMatrix(client, X_test, y_test)

# Cross-validation results
cv_results = xgb.dask.cv(
    client,
    params={'max_depth': 6, 'eta': 0.1, 'objective': 'binary:logistic'},
    dtrain=dtrain,
    num_boost_round=1000,
    nfold=5
)

print(cv_results.head())
```

### Feature Importance

```python
# Train model
model.fit(X_train, y_train)

# Get feature importance
importance = model.booster_.get_score(importance_type='gain')

# Plot importance
import matplotlib.pyplot as plt
xgb.plot_importance(model.booster_, importance_type='gain')
plt.show()
```

## Distributed Training Patterns

### Data Parallel Training

```python
from dask_ml.xgboost import XGBClassifier

# Training happens on each worker's local data
model = XGBClassifier(n_estimators=100, max_depth=6)

# Data stays on workers (no movement)
model.fit(X_train, y_train)
```

### Model Parallel Training

For models too large for single machine:

```python
# Split model across workers
# (specific to frameworks that support it)
from dask_ml.decomposition import PCA

# PCA with many components
pca = PCA(n_components=1000)
pca.fit(X_large)  # Distributes computation
```

## Feature Engineering at Scale

### Parallel Feature Engineering

```python
import dask.dataframe as dd
import dask.array as da

# Load data
df = dd.read_parquet('features.parquet')

# Create features in parallel
df['feature_1'] = df['col_a'] * df['col_b']
df['feature_2'] = df['col_c'].rolling(10).mean()
df['feature_3'] = df.groupby('id')['value'].transform('sum')

# Compute features
features = df[['feature_1', 'feature_2', 'feature_3']].compute()
```

### Parallel Pipeline

```python
from sklearn.pipeline import Pipeline
from dask_ml.preprocessing import StandardScaler
from dask_ml.decomposition import PCA
from dask_ml.wrappers import Incremental
from sklearn.linear_model import SGDClassifier

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=50)),
    ('classifier', Incremental(SGDClassifier()))
])

# Fit pipeline
pipeline.fit(X_train, y_train)

# Predict
predictions = pipeline.predict(X_test)
```

## Best Practices

### Memory Management

```python
# Process in chunks to avoid OOM
def train_in_chunks(model, X, y, chunk_size=100000):
    for i in range(0, len(X), chunk_size):
        X_chunk = X[i:i+chunk_size]
        y_chunk = y[i:i+chunk_size]
        model.partial_fit(X_chunk, y_chunk, classes=[0, 1])
    return model

model = train_in_chunks(model, X, y)
```

### Data Locality

```python
# Keep data on workers (don't gather to client)
X = dd.read_parquet('s3://bucket/X.parquet')
y = dd.read_parquet('s3://bucket/y.parquet')

# Model trains on worker data
model.fit(X, y)  # No data movement to scheduler
```

### Checkpointing

```python
# Save intermediate results
model.fit(X_train, y_train)
model.booster_.save_model('checkpoint.ubj')

# Resume training
model.fit(X_train, y_train, xgb_model='checkpoint.ubj')
```

## Performance Tips

### Use Appropriate Libraries

| Task | Library | Reason |
|------|---------|--------|
| General ML | dask-ml | Scikit-learn compatible |
| Gradient Boosting | XGBoost/LightGBM | Native distributed training |
| Deep Learning | Dask + PyTorch/TF | Dynamic batching |
| Hyperparameter Tuning | Dask-ML search | Parallel trials |

### Optimize Data Loading

```python
# Good: Parquet with statistics
df = dd.read_parquet('data.parquet', engine='pyarrow')

# Good: CSV with blocksize
df = dd.read_csv('data/*.csv', blocksize='256MB')

# Bad: Read entire dataset then partition
df = dd.from_pandas(pd.read_csv('huge.csv'), npartitions=100)
```

### Profile Training

```python
from dask.diagnostics import ProgressBar, Profiler

with ProgressBar() and Profiler() as prof:
    model.fit(X_train, y_train)

prof.visualize(filename='training_profile.png')
```

## Case Studies

### Case 1: Large-Scale Classification

**Problem**: Train classifier on 100GB dataset.

**Solution**:
```python
# Load data distributed
df = dd.read_parquet('s3://bucket/large_dataset.parquet')

# Extract features and labels
X = df.drop('label', axis=1)
y = df['label']

# Train with incremental learning
from dask_ml.wrappers import Incremental
from sklearn.linear_model import SGDClassifier

model = Incremental(SGDClassifier(loss='log_loss'))
model.fit(X, y, classes=[0, 1, 2, 3, 4])
```

### Case 2: Hyperparameter Optimization

**Problem**: Find best hyperparameters across 1000 combinations.

**Solution**:
```python
# Define search space
param_grid = {
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'max_depth': [3, 6, 9, 12],
    'n_estimators': [100, 200, 500, 1000],
    'subsample': [0.6, 0.8, 1.0]
}  # 192 combinations

# Parallel search
from dask_ml.model_selection import GridSearchCV

grid_search = GridSearchCV(
    XGBClassifier(),
    param_grid,
    cv=3,
    scoring='accuracy'
)

# Distributes across cluster
grid_search.fit(X, y)
```

### Case 3: Feature Engineering Pipeline

**Problem**: Create 1000 features from raw data.

**Solution**:
```python
# Parallel feature engineering
features = []
for col in df.columns:
    if df[col].dtype == 'object':
        # One-hot encode
        encoded = dd.get_dummies(df[col], prefix=col)
        features.append(encoded)
    else:
        # Statistical features
        feat = df[col].rolling(10).agg(['mean', 'std', 'min', 'max'])
        features.append(feat)

# Concatenate features
X = dd.concat(features, axis=1)

# Train model
model.fit(X, y)
```

## Integration with Other Libraries

### Dask + PyTorch

```python
import torch
import dask.array as da

# Convert Dask array to PyTorch tensor
def dask_to_pytorch(dask_array):
    # Gather to client, convert to tensor
    numpy_array = dask_array.compute()
    return torch.from_numpy(numpy_array)

X_train_tensor = dask_to_pytorch(X_train)
y_train_tensor = dask_to_pytorch(y_train)
```

### Dask + TensorFlow

```python
import tensorflow as tf
import dask.dataframe as dd

# Create tf.data.Dataset from Dask DataFrame
df = dd.read_parquet('data.parquet')

# Convert to pandas (for small datasets)
pandas_df = df.compute()
dataset = tf.data.Dataset.from_tensor_slices((dict(X), y))
```

### Dask + MLflow

```python
import mlflow
import mlflow.sklearn

# Log metrics during training
with mlflow.start_run():
    model.fit(X_train, y_train)

    # Log parameters
    mlflow.log_params(grid_search.best_params_)

    # Log metrics
    mlflow.log_metrics({
        'train_score': grid_search.best_score_,
        'test_score': grid_search.score(X_test, y_test)
    })

    # Log model
    mlflow.sklearn.log_model(model, 'model')
```
