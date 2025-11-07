# QuickInsights API Reference

## Overview

QuickInsights is a Python library that provides creative and innovative analysis tools for large datasets.

See also: Creative features overview in `docs/CREATIVE_FEATURES.md` for high-level descriptions and examples of:
- `infer_constraints`
- `drift_radar`
- `contrastive_explanations`

## Installation

```bash
pip install quickinsights
```

## Core Functions

### `analyze(df, show_plots=True, save_plots=False, output_dir="./quickinsights_output")`

Performs comprehensive analysis on the dataset.

**Parameters:**
- `df` (pd.DataFrame): Dataset to analyze
- `show_plots` (bool): Whether to display plots
- `save_plots` (bool): Whether to save plots
- `output_dir` (str): Directory to save plots

**Returns:**
- `dict`: Analysis results

**Example:**
```python
import quickinsights as qi
import pandas as pd

df = pd.read_csv('data.csv')
results = qi.analyze(df, save_plots=True)
```

### `analyze_numeric(df, show_plots=True, save_plots=False, output_dir="./quickinsights_output")`

Performs detailed analysis on numerical variables.

**Parameters:**
- `df` (pd.DataFrame): Dataset containing only numerical variables
- `show_plots` (bool): Whether to display plots
- `save_plots` (bool): Whether to save plots
- `output_dir` (str): Directory to save plots

**Returns:**
- `dict`: Numerical analysis results

### `analyze_categorical(df, show_plots=True, save_plots=False, output_dir="./quickinsights_output")`

Performs detailed analysis on categorical variables.

**Parameters:**
- `df` (pd.DataFrame): Dataset containing only categorical variables
- `show_plots` (bool): Whether to display plots
- `save_plots` (bool): Whether to save plots
- `output_dir` (str): Directory to save plots

**Returns:**
- `dict`: Categorical analysis results

## Visualization Functions

### `correlation_matrix(df, method='pearson', save_plots=False, output_dir="./quickinsights_output")`

Visualizes correlation matrix between numerical variables.

**Parameters:**
- `df` (pd.DataFrame): Dataset containing only numerical variables
- `method` (str): Correlation calculation method ('pearson', 'spearman')
- `save_plots` (bool): Whether to save the plot
- `output_dir` (str): Directory to save the plot

### `distribution_plots(df, save_plots=False, output_dir="./quickinsights_output")`

Creates distribution plots for numerical variables.

**Parameters:**
- `df` (pd.DataFrame): Dataset containing only numerical variables
- `save_plots` (bool): Whether to save plots
- `output_dir` (str): Directory to save plots

### `summary_stats(df)`

Calculates statistical summary of the dataset.

**Parameters:**
- `df` (pd.DataFrame): Dataset to analyze

**Returns:**
- `dict`: Statistical summary

## Utility Functions

### `get_data_info(df)`

Provides general information about the dataset.

**Parameters:**
- `df` (pd.DataFrame): Dataset to analyze

**Returns:**
- `dict`: Dataset information

### `detect_outliers(df, method='iqr', threshold=1.5)`

Detects outliers in numerical variables.

**Parameters:**
- `df` (pd.DataFrame): Dataset to analyze
- `method` (str): Outlier detection method ('iqr', 'zscore')
- `threshold` (float): Threshold for outlier detection

**Returns:**
- `dict`: Outlier information

### `validate_dataframe(df)`

Validates dataframe structure and content.

**Parameters:**
- `df` (pd.DataFrame): Dataset to validate

**Returns:**
- `bool`: Validation result

## Performance Optimization Functions

### `lazy_evaluate(func)`

Decorator for lazy evaluation of functions.

**Parameters:**
- `func`: Function to wrap

**Returns:**
- Wrapped function that executes only when called

**Example:**
```python
@qi.lazy_evaluate
def expensive_function(x):
    return x ** 2

lazy_result = expensive_function(5)
result = lazy_result()  # Now executes
```

### `cache_result(ttl=3600)`

Decorator for caching function results.

**Parameters:**
- `ttl` (int): Time to live in seconds

**Returns:**
- Decorated function with caching

**Example:**
```python
@qi.cache_result(ttl=3600)
def slow_function(x):
    return x ** 3

result1 = slow_function(5)  # Slow
result2 = slow_function(5)  # Fast (from cache)
```

### `parallel_process(func, data, max_workers=None)`

Processes data in parallel using multiple workers.

**Parameters:**
- `func`: Function to apply to each item
- `data`: Data to process
- `max_workers` (int): Maximum number of workers

**Returns:**
- `list`: Processed results

## Big Data Functions

### `memory_optimize(df)`

Optimizes memory usage of the dataframe.

**Parameters:**
- `df` (pd.DataFrame): Dataset to optimize

**Returns:**
- `pd.DataFrame`: Memory-optimized dataset

### `process_in_chunks(df, func, chunk_size=10000)`

Processes large datasets in chunks.

**Parameters:**
- `df` (pd.DataFrame): Dataset to process
- `func`: Function to apply to each chunk
- `chunk_size` (int): Size of each chunk

**Returns:**
- `list`: Results from processing chunks

## Cloud Integration Functions

### `upload_to_cloud(file_path, provider, remote_path, **kwargs)`

Uploads files to cloud storage.

**Parameters:**
- `file_path` (str): Local file path
- `provider` (str): Cloud provider ('aws', 'azure', 'gcs')
- `remote_path` (str): Remote file path
- `**kwargs`: Provider-specific parameters

**Returns:**
- `bool`: Upload success status

### `download_from_cloud(provider, remote_path, **kwargs)`

Downloads files from cloud storage.

**Parameters:**
- `provider` (str): Cloud provider ('aws', 'azure', 'gcs')
- `remote_path` (str): Remote file path
- `**kwargs`: Provider-specific parameters

**Returns:**
- Downloaded data or file path

## AI-Powered Analysis Functions

### `AIInsightEngine(df)`

AI-powered analysis engine for discovering patterns and insights.

**Parameters:**
- `df` (pd.DataFrame): Dataset to analyze

**Methods:**
- `get_insights()`: Returns comprehensive insights
- `discover_patterns()`: Discovers data patterns
- `predict_trends()`: Predicts future trends
- `get_feature_importance()`: Calculates feature importance

## Real-time Pipeline Functions

### `RealTimePipeline(name)`

Real-time data processing pipeline.

**Parameters:**
- `name` (str): Pipeline name

**Methods:**
- `add_transformation(func)`: Adds data transformation
- `add_filter(func)`: Adds data filter
- `start()`: Starts the pipeline
- `stop()`: Stops the pipeline
- `process_stream(data_stream)`: Processes streaming data

## Data Validation Functions

### `validate_data_types(df, expected_types)`

Validates data types of dataframe columns.

**Parameters:**
- `df` (pd.DataFrame): Dataset to validate
- `expected_types` (dict): Expected column types

**Returns:**
- `dict`: Validation results

### `infer_constraints(df, max_categories=25, detect_patterns=True)`

Infers data constraints from example data (schema-by-example). Returns per-column dtype, nullability, uniqueness, cardinality, numeric stats, top categories, and pattern hints (email/phone/date). Also includes a compact `contract` dict for quick validation.

**Returns:**
- `dict`: Profile including `columns` and `contract`.

### `drift_radar(base_df, current_df, bins=10, top_k_categories=20)`

Detects schema and distribution drift between baseline and current datasets.

- Numeric: PSI (Population Stability Index), optional KS-test if SciPy is available
- Categorical: PSI over top-K categories, unseen/vanished category tracking

**Returns:**
- `dict`: Per-column drift metrics and `overall_risk` (low|medium|high)

### `check_data_quality(df)`

Checks overall data quality.

**Parameters:**
- `df` (pd.DataFrame): Dataset to check

**Returns:**
- `dict`: Quality metrics

## Error Handling

All functions include proper error handling and will raise appropriate exceptions for invalid inputs or processing errors.

## Performance Notes

- Use lazy evaluation for expensive computations
- Apply caching for frequently called functions
- Use parallel processing for large datasets
- Consider memory optimization for big data operations

## Examples

For complete usage examples, see the examples directory and the main README file.

This API reference covers the core functionality of QuickInsights. For advanced usage patterns and best practices, refer to the documentation and examples.

---

## Neural Patterns (Neural-inspired)

### `neural_pattern_mining(data, n_patterns=5, random_state=42, batch_size=4096)`
- Discovers recurring patterns via MiniBatch KMeans. Returns pattern centers, labels, and counts.

### `autoencoder_anomaly_scores(data, hidden_ratio=0.5, random_state=42, max_iter=200)`
- Computes anomaly scores via lightweight autoencoder surrogate (MLPRegressor), falls back to PCA reconstruction error.

### `sequence_signature_extract(data, window=64, step=16, n_components=2, random_state=42)`
- Extracts FFT+PCA-based signatures from (multi)variate time series.

Example:
```python
from quickinsights import neural_pattern_mining, autoencoder_anomaly_scores, sequence_signature_extract
res = neural_pattern_mining(df, n_patterns=5)
scores = autoencoder_anomaly_scores(df)
sigs = sequence_signature_extract(series, window=128, step=32, n_components=3)
```

## Quantum Insights (Quantum-inspired)

### `quantum_superposition_sample(data, n_samples=10000, random_state=42)`
- Superposition-inspired sampling using randomized projections (keeps informative modes).

### `amplitude_pca(data, n_components=10, random_state=42)`
- Amplitude-encoding-inspired dimensionality reduction using randomized PCA.

### `quantum_correlation_map(data, n_blocks=5, block_size=20000, random_state=42)`
- Robust high-dimensional correlation via median-of-means across random blocks.

### `quantum_anneal_optimize(estimator, param_grid, X, y, max_iters=30, cv_folds=3, random_state=42)`
- Annealing-style hyperparameter search on discrete grids.

Example:
```python
from quickinsights import quantum_superposition_sample, amplitude_pca, quantum_correlation_map
sample = quantum_superposition_sample(df, n_samples=5000)
pca = amplitude_pca(df, n_components=8)
qc = quantum_correlation_map(df, n_blocks=3)
```

## Holographic Visualization (3D, non‑VR)

### `embed_3d_projection(data, method='pca', random_state=42)`
- 3D embedding using PCA (or UMAP if available). Returns DataFrame with `x,y,z`.

### `volumetric_density_plot(data, bins=32)`
- Computes 3D histogram volume suitable for volumetric visualization.

### `plotly_embed_3d(embedding, color=None, size=3)`
- Builds interactive Plotly 3D scatter. Returns `{"success": True, "figure": fig}` on success.

### `export_vr_scene_stub(embedding, out_path)`
- Exports a lightweight JSON point-cloud scene (portable; VR export is optional and not required).

Example:
```python
from quickinsights import embed_3d_projection, plotly_embed_3d
emb = embed_3d_projection(df)
fig_res = plotly_embed_3d(emb["embedding"], size=2)
```

## Performance Acceleration (GPU/Memory)

### `gpu_available()`
- Returns whether CuPy GPU backend is usable on this system.

### `get_array_backend(prefer_gpu=True)`
- Returns `{"xp": module, "name": "cupy|numpy", "device": "gpu|cpu"}` for array operations.

### `standardize_array(array, axis=0, prefer_gpu=True)`
- Z-score standardization with GPU fallback to CPU; always returns NumPy array.

### `backend_dot(a, b, prefer_gpu=True)`
- Dot product using selected backend; returns NumPy array and falls back safely.

### `gpu_corrcoef(array, prefer_gpu=True)`
- Correlation matrix using GPU if available, else CPU; returns NumPy array.

### `memmap_array(path, dtype, shape, mode='w+')`
- Creates/opens memory-mapped arrays; ensures directory exists.

### `chunked_apply(func, array, chunk_rows=100000)`
- Applies function to array in row-chunks for memory efficiency.

### `benchmark_backend(func, repeats=3, prefer_gpu=True)`
- Benchmarks CPU vs GPU for a simple callable that accepts `xp` (numpy/cupy).

Example:
```python
from quickinsights import gpu_available, gpu_corrcoef, memmap_array, chunked_apply
has_gpu = gpu_available()
corr = gpu_corrcoef(df.to_numpy())
mmap = memmap_array('./quickinsights_output/tmp.mmap', 'float32', (1_000_000, 8))
res = chunked_apply(lambda x: x.sum(), df.to_numpy(), chunk_rows=50_000)
```

## Explainable AI Additions

### `contrastive_explanations(model, X, y, index=0, k_neighbors=5, feature_names=None)`

Generates a contrastive explanation for a single instance by finding a minimal directional change toward the opposite class using nearest neighbors. Works best for binary classification and degrades gracefully otherwise.

Returns keys: `predicted_class`, `opposite_class`, `k_neighbors`, `mean_direction_norm`, `suggestions` (list of feature delta recommendations), and `performance`.
