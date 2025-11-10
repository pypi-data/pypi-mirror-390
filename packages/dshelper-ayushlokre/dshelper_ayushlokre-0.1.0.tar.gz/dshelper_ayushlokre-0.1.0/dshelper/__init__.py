"""
DSHelper - A Quality-of-Life Data Science Helper Library
=========================================================

A comprehensive toolkit for common data science and machine learning tasks,
designed to save time and reduce boilerplate code.

Modules:
--------
- missing: Tools for analyzing and handling missing values
- correlation: Quick correlation analysis and visualization
- preprocessing: Data preprocessing utilities including train-test-split with scaling
- evaluation: Model evaluation metrics and visualization

Example Usage:
--------------
    >>> from dshelper import missing, preprocessing, evaluation
    >>> 
    >>> # Check missing values
    >>> missing.analyze(df)
    >>> 
    >>> # Preprocess data
    >>> X_train, X_test, y_train, y_test = preprocessing.split_and_scale(X, y)
    >>> 
    >>> # Evaluate model
    >>> evaluation.quick_eval(y_true, y_pred)
"""

__version__ = "0.1.0"
__author__ = "Ayush Lokre"
__email__ = "ayushlokre5@gmail.com"

from dshelper import missing, correlation, preprocessing, evaluation

__all__ = [
    "missing",
    "correlation",
    "preprocessing",
    "evaluation",
    "__version__",
]
