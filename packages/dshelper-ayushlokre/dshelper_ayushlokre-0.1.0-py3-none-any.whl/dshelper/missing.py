"""
Missing Value Analysis Module
==============================

This module provides utilities for analyzing and handling missing values in datasets.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Dict, List
import warnings


def analyze(
    df: pd.DataFrame,
    threshold: float = 0.0,
    show_plot: bool = True,
    figsize: tuple = (10, 6)
) -> pd.DataFrame:
    """
    Analyze missing values in a DataFrame and generate a comprehensive report.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame to analyze
    threshold : float, default=0.0
        Only show columns with missing percentage above this threshold (0-100)
    show_plot : bool, default=True
        Whether to display a visualization of missing values
    figsize : tuple, default=(10, 6)
        Figure size for the plot
        
    Returns:
    --------
    pd.DataFrame
        A report DataFrame containing:
        - Column names
        - Missing count
        - Missing percentage
        - Data type
        - Non-missing count
        
    Example:
    --------
    >>> import pandas as pd
    >>> from dshelper import missing
    >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [4, None, None]})
    >>> report = missing.analyze(df)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    # Calculate missing statistics
    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100
    dtypes = df.dtypes
    non_missing = df.notnull().sum()
    
    # Create report DataFrame
    report = pd.DataFrame({
        'Column': df.columns,
        'Missing_Count': missing_count.values,
        'Missing_Percent': missing_percent.values,
        'Non_Missing_Count': non_missing.values,
        'Data_Type': dtypes.values
    })
    
    # Filter by threshold
    report = report[report['Missing_Percent'] >= threshold]
    
    # Sort by missing percentage (descending)
    report = report.sort_values('Missing_Percent', ascending=False).reset_index(drop=True)
    
    # Display plot if requested
    if show_plot and len(report) > 0:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.figure(figsize=figsize)
            sns.barplot(
                data=report.head(20),  # Show top 20
                x='Missing_Percent',
                y='Column',
                palette='viridis'
            )
            plt.xlabel('Missing Percentage (%)', fontsize=12)
            plt.ylabel('Column Name', fontsize=12)
            plt.title('Missing Values Analysis (Top 20 Columns)', fontsize=14, fontweight='bold')
            plt.xlim(0, 100)
            
            # Add percentage labels
            for i, v in enumerate(report.head(20)['Missing_Percent']):
                plt.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=9)
            
            plt.tight_layout()
            plt.show()
        except ImportError:
            warnings.warn("matplotlib or seaborn not available. Skipping plot.")
    
    return report


def quick_summary(df: pd.DataFrame) -> Dict[str, Union[int, float, List[str]]]:
    """
    Get a quick summary of missing values in the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame to analyze
        
    Returns:
    --------
    dict
        Dictionary containing:
        - total_missing: Total number of missing values
        - total_cells: Total number of cells in DataFrame
        - missing_percentage: Overall percentage of missing values
        - columns_with_missing: List of column names with missing values
        - complete_columns: List of column names without missing values
        
    Example:
    --------
    >>> summary = missing.quick_summary(df)
    >>> print(f"Total missing: {summary['total_missing']}")
    """
    total_missing = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    missing_percentage = (total_missing / total_cells * 100) if total_cells > 0 else 0
    
    columns_with_missing = df.columns[df.isnull().any()].tolist()
    complete_columns = df.columns[~df.isnull().any()].tolist()
    
    return {
        'total_missing': int(total_missing),
        'total_cells': int(total_cells),
        'missing_percentage': float(missing_percentage),
        'columns_with_missing': columns_with_missing,
        'complete_columns': complete_columns,
        'num_columns_with_missing': len(columns_with_missing),
        'num_complete_columns': len(complete_columns)
    }


def drop_missing_columns(
    df: pd.DataFrame,
    threshold: float = 50.0,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Drop columns with missing values above a specified threshold.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    threshold : float, default=50.0
        Percentage threshold (0-100). Columns with missing % above this will be dropped
    inplace : bool, default=False
        If True, modify the DataFrame in place
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns dropped (or modified in place)
        
    Example:
    --------
    >>> # Drop columns with more than 30% missing values
    >>> df_clean = missing.drop_missing_columns(df, threshold=30)
    """
    if not 0 <= threshold <= 100:
        raise ValueError("Threshold must be between 0 and 100")
    
    missing_percent = (df.isnull().sum() / len(df)) * 100
    columns_to_drop = missing_percent[missing_percent > threshold].index.tolist()
    
    if columns_to_drop:
        print(f"Dropping {len(columns_to_drop)} columns: {columns_to_drop}")
    else:
        print("No columns to drop based on the threshold.")
    
    if inplace:
        df.drop(columns=columns_to_drop, inplace=True)
        return df
    else:
        return df.drop(columns=columns_to_drop)


def fill_missing(
    df: pd.DataFrame,
    strategy: str = 'mean',
    columns: Optional[List[str]] = None,
    fill_value: Optional[Union[int, float, str]] = None,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Fill missing values using various strategies.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    strategy : str, default='mean'
        Strategy to use: 'mean', 'median', 'mode', 'forward', 'backward', 'constant'
    columns : list, optional
        List of columns to fill. If None, applies to all columns
    fill_value : scalar, optional
        Value to use when strategy='constant'
    inplace : bool, default=False
        If True, modify the DataFrame in place
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with missing values filled
        
    Example:
    --------
    >>> # Fill missing values with median
    >>> df_filled = missing.fill_missing(df, strategy='median')
    """
    if not inplace:
        df = df.copy()
    
    cols_to_fill = columns if columns else df.columns.tolist()
    
    for col in cols_to_fill:
        if col not in df.columns:
            warnings.warn(f"Column '{col}' not found in DataFrame. Skipping.")
            continue
            
        if strategy == 'mean':
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                df[col].fillna(df[col].mean(), inplace=True)
        elif strategy == 'median':
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                df[col].fillna(df[col].median(), inplace=True)
        elif strategy == 'mode':
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
        elif strategy == 'forward':
            df[col].fillna(method='ffill', inplace=True)
        elif strategy == 'backward':
            df[col].fillna(method='bfill', inplace=True)
        elif strategy == 'constant':
            if fill_value is None:
                raise ValueError("fill_value must be provided when strategy='constant'")
            df[col].fillna(fill_value, inplace=True)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    return df
