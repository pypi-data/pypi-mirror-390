# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-10

### Added
- Initial release of DSHelper
- **Missing Values Module** (`dshelper.missing`)
  - `analyze()`: Comprehensive missing value analysis with visualization
  - `quick_summary()`: Quick statistical summary of missing data
  - `drop_missing_columns()`: Drop columns above missing threshold
  - `fill_missing()`: Multiple strategies for filling missing values
  
- **Correlation Module** (`dshelper.correlation`)
  - `heatmap()`: Beautiful correlation heatmap generation
  - `top_correlations()`: Find top correlated features
  - `remove_highly_correlated()`: Remove multicollinear features
  - `correlation_with_target()`: Analyze feature-target correlations
  
- **Preprocessing Module** (`dshelper.preprocessing`)
  - `split_and_scale()`: Train-test split with automatic scaling
  - `create_scaler()`: Create configured scaler objects
  - `encode_categorical()`: Multiple encoding strategies
  - `handle_outliers()`: Detect and handle outliers (IQR, Z-score)
  - `feature_selection_quick()`: Quick feature selection using statistical tests
  
- **Evaluation Module** (`dshelper.evaluation`)
  - `quick_eval()`: Comprehensive model evaluation (auto-detects classification/regression)
  - `compare_models()`: Side-by-side model comparison
  - `cross_val_summary()`: Cross-validation with visualization
  - `feature_importance_plot()`: Feature importance visualization

### Features
- Support for both classification and regression tasks
- Automatic task type detection
- Beautiful visualizations using matplotlib and seaborn
- Comprehensive docstrings and type hints
- Production-ready error handling
- Pandas and NumPy array support

### Documentation
- Complete README with examples
- Detailed API documentation
- Real-world usage examples
- Installation instructions

### Dependencies
- numpy >= 1.20.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- matplotlib >= 3.3.0
- seaborn >= 0.11.0

### Package Configuration
- Modern pyproject.toml setup
- Backward-compatible setup.py
- Development dependencies included
- Black, Flake8, and MyPy configuration
- Pytest configuration for testing

## [Unreleased]

### Planned Features
- Deep learning utilities
- Time series analysis tools
- Automated feature engineering
- More advanced visualization options
- Performance optimization utilities
- Integration with popular ML frameworks

---

## Version History

- **0.1.0** (2025-11-10): Initial release with core functionality
