# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Table Toolkit (tabkit)** is a Python library for consistent preprocessing of tabular data. It provides configuration-driven preprocessing with automatic type inference, missing value imputation, feature binning, stratified splitting, and smart caching based on config hashing.

Key package name: Published as `table-toolkit` on PyPI, imported as `tabkit` in code.

## Development Commands

### Environment Setup
This project uses **Pixi** for environment management (not pip/conda directly):
```bash
# Pixi manages dependencies via pyproject.toml
# No manual setup needed - pixi handles everything
```

### Testing
```bash
pixi run test
```
Note: Tests require `OPENML_API_KEY` and `OPENML_CACHE_DIR` environment variables. The test command sets these to test values automatically.

### Building
```bash
pixi run build
```
Creates distribution files in `dist/` directory.

### Publishing
```bash
pixi run publish
```
Uploads to PyPI via twine.

### Running Single Tests
```bash
# Run specific test file
pixi run pytest tests/data/test_transforms.py

# Run specific test function
pixi run pytest tests/data/test_table_processor.py::test_function_name

# Run with verbose output
pixi run pytest -v tests/
```

## Architecture

### Core Components

**TableProcessor** (`src/tabkit/data/table_processor.py`)
- Central class that orchestrates data loading, preprocessing, splitting, and caching
- Uses configuration hashing to create unique cache directories: `DATA_DIR/data/{dataset_hash}/{config_hash}/`
- Supports both dataclass configs and plain dictionaries (converted via `_parse_config()`)
- Main workflow: `prepare()` → `get_split()` or `get()`

**Configuration System** (`src/tabkit/data/data_config.py`)
- Two main dataclasses: `DatasetConfig` (data loading) and `TableProcessorConfig` (preprocessing/splitting)
- Supports both typed config classes and plain dicts interchangeably
- Config changes trigger new cache directories via hash computation

**Transform Pipeline** (`src/tabkit/data/transforms.py`)
- All transforms inherit from `BaseTransform` abstract class
- Each transform must implement: `fit()`, `transform()`, and optionally `update_metadata()`
- Built-in transforms: `Impute`, `Scale`, `Discretize`, `Encode`, `ConvertDatetime`
- Custom transforms registered via `add_transform()` decorator and added to `TRANSFORM_MAP`
- Transforms update `ColumnMetadata` to track type changes (e.g., continuous → categorical after discretization)

**Column Metadata** (`src/tabkit/data/column_metadata.py`)
- Tracks column properties: name, kind (categorical/continuous/binary/datetime), dtype, mapping
- Updated throughout pipeline as transforms change data types
- Used for type-aware processing decisions

### Data Splitting Modes

Two mutually exclusive modes (controlled in `TableProcessor._get_splits()`):

1. **Ratio-based** (priority if `test_ratio` and `val_ratio` are both set)
   - Simple percentage split using `train_test_split`
   - Example: `test_ratio=0.2, val_ratio=0.1` → 70/10/20 split

2. **K-fold based** (default)
   - Uses `StratifiedKFold` for systematic coverage
   - Configured via `n_splits`, `fold_idx`, `n_val_splits`, `val_fold_idx`
   - Default: 10 splits for test, 9 subsplits for validation

**Predefined splits**: Some data sources (OpenML, custom split files) provide train/test indices. In these cases, only the validation split is computed from the training portion.

### Data Source Loaders

Located in `src/tabkit/data/utils/`:
- `load_from_disk.py`: CSV/Parquet files, optional split file
- `load_openml_dataset.py`: OpenML tasks/datasets
- `load_uci_dataset.py`: UCI ML repository
- Each returns `(X, y, train_indices, test_indices)`

### Caching System

**Cache Structure**:
```
.data/data/{dataset_hash}/{config_hash}/
├── raw_df.parquet          # Original dataframe
├── train.parquet           # Processed splits
├── val.parquet
├── test.parquet
├── train_idxs.npy          # Original indices
├── val_idxs.npy
├── test_idxs.npy
├── pipeline.joblib         # Fitted transform pipeline
├── label_pipeline.joblib
├── config.json
└── dataset_info.json       # Metadata (columns_info, label_info, n_samples)
```

**Cache invalidation**: Any config change creates a new hash → new directory. Old caches are not auto-deleted.

**Checking cache**: `TableProcessor.is_cached` property verifies all required files exist.

### Environment Configuration

`src/tabkit/config.py` expects two environment variables:
- `OPENML_API_KEY`: Required for OpenML data sources
- `OPENML_CACHE_DIR`: Where OpenML caches datasets
- `DATA_DIR`: Optional, defaults to `.data/` in current directory

## Key Design Patterns

1. **Configuration flexibility**: Both dataclasses and dicts work identically via `_parse_config()`
2. **Hash-based caching**: Reproducible preprocessing - same config always produces same cache
3. **Metadata propagation**: Each transform can update column metadata as types change
4. **Stratified splitting**: Automatic stratification when possible, graceful fallback to non-stratified
5. **Pipeline composition**: Transforms are composable and order-dependent

## Common Gotchas

- The package is installed as `table-toolkit` but imported as `tabkit`
- Config changes trigger full reprocessing - caches are keyed by config hash
- Test/val split priority: ratio mode overrides k-fold if both configured
- Continuous labels in classification tasks automatically get quantile discretization unless `label_pipeline` is specified
- Environment variables must be set for OpenML usage (OPENML_API_KEY, OPENML_CACHE_DIR)

## File Structure

```
src/tabkit/
├── data/
│   ├── data_config.py          # DatasetConfig, TableProcessorConfig
│   ├── table_processor.py      # Main TableProcessor class
│   ├── transforms.py           # Transform pipeline system
│   ├── column_metadata.py      # Column type tracking
│   ├── compute_bins.py         # Discretization utilities
│   └── utils/                  # Data source loaders
tests/data/                     # Test suite
examples/                       # Usage examples
```
