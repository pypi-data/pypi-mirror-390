"""
Correlation Analysis Module
============================

This module provides utilities for correlation analysis and visualization.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
import warnings


def heatmap(
    df: pd.DataFrame,
    method: str = 'pearson',
    figsize: tuple = (12, 10),
    annot: bool = True,
    cmap: str = 'coolwarm',
    vmin: float = -1,
    vmax: float = 1,
    columns: Optional[List[str]] = None,
    mask_diagonal: bool = False,
    threshold: Optional[float] = None
) -> pd.DataFrame:
    """
    Generate a correlation heatmap with customizable options.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    method : str, default='pearson'
        Correlation method: 'pearson', 'spearman', or 'kendall'
    figsize : tuple, default=(12, 10)
        Figure size for the plot
    annot : bool, default=True
        Whether to annotate cells with correlation values
    cmap : str, default='coolwarm'
        Colormap to use
    vmin : float, default=-1
        Minimum value for colormap
    vmax : float, default=1
        Maximum value for colormap
    columns : list, optional
        Specific columns to include. If None, uses all numeric columns
    mask_diagonal : bool, default=False
        Whether to mask the diagonal (correlation with self)
    threshold : float, optional
        Only show correlations with absolute value above this threshold
        
    Returns:
    --------
    pd.DataFrame
        Correlation matrix
        
    Example:
    --------
    >>> from dshelper import correlation
    >>> corr_matrix = correlation.heatmap(df, method='spearman')
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        raise ImportError("matplotlib and seaborn are required for plotting")
    
    # Select columns
    if columns:
        df_numeric = df[columns]
    else:
        df_numeric = df.select_dtypes(include=[np.number])
    
    if df_numeric.empty:
        raise ValueError("No numeric columns found in DataFrame")
    
    # Calculate correlation
    corr_matrix = df_numeric.corr(method=method)
    
    # Apply threshold if specified
    if threshold is not None:
        mask_threshold = np.abs(corr_matrix) < threshold
        corr_matrix = corr_matrix.mask(mask_threshold)
    
    # Create mask for diagonal
    mask = None
    if mask_diagonal:
        mask = np.eye(len(corr_matrix), dtype=bool)
    
    # Create plot
    plt.figure(figsize=figsize)
    sns.heatmap(
        corr_matrix,
        annot=annot,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        mask=mask,
        fmt='.2f' if annot else None
    )
    
    plt.title(f'Correlation Heatmap ({method.capitalize()} Method)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
    
    return corr_matrix


def top_correlations(
    df: pd.DataFrame,
    target: Optional[str] = None,
    method: str = 'pearson',
    n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Find top correlations in the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    target : str, optional
        If specified, returns correlations with this target column only
    method : str, default='pearson'
        Correlation method: 'pearson', 'spearman', or 'kendall'
    n : int, default=10
        Number of top correlations to return
    ascending : bool, default=False
        If False, returns highest correlations; if True, returns lowest
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with top correlations
        
    Example:
    --------
    >>> # Get top 10 features correlated with target
    >>> top_corr = correlation.top_correlations(df, target='price', n=10)
    """
    df_numeric = df.select_dtypes(include=[np.number])
    
    if df_numeric.empty:
        raise ValueError("No numeric columns found in DataFrame")
    
    corr_matrix = df_numeric.corr(method=method)
    
    if target:
        if target not in corr_matrix.columns:
            raise ValueError(f"Target column '{target}' not found in DataFrame")
        
        correlations = corr_matrix[target].drop(target)  # Exclude self-correlation
        correlations = correlations.abs().sort_values(ascending=ascending).head(n)
        
        result = pd.DataFrame({
            'Feature': correlations.index,
            'Correlation': corr_matrix[target][correlations.index].values,
            'Abs_Correlation': correlations.values
        })
    else:
        # Get all pairwise correlations
        corr_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_pairs.append({
                    'Feature_1': corr_matrix.columns[i],
                    'Feature_2': corr_matrix.columns[j],
                    'Correlation': corr_matrix.iloc[i, j],
                    'Abs_Correlation': abs(corr_matrix.iloc[i, j])
                })
        
        result = pd.DataFrame(corr_pairs)
        result = result.sort_values('Abs_Correlation', ascending=ascending).head(n)
    
    return result.reset_index(drop=True)


def remove_highly_correlated(
    df: pd.DataFrame,
    threshold: float = 0.95,
    method: str = 'pearson',
    keep: str = 'first'
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Remove highly correlated features from the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    threshold : float, default=0.95
        Correlation threshold above which features will be removed
    method : str, default='pearson'
        Correlation method: 'pearson', 'spearman', or 'kendall'
    keep : str, default='first'
        Which feature to keep: 'first' or 'last'
        
    Returns:
    --------
    tuple
        (DataFrame with columns removed, List of removed column names)
        
    Example:
    --------
    >>> df_reduced, removed = correlation.remove_highly_correlated(df, threshold=0.9)
    >>> print(f"Removed {len(removed)} features: {removed}")
    """
    df_numeric = df.select_dtypes(include=[np.number])
    
    if df_numeric.empty:
        warnings.warn("No numeric columns found. Returning original DataFrame.")
        return df, []
    
    # Calculate correlation matrix
    corr_matrix = df_numeric.corr(method=method).abs()
    
    # Get upper triangle of correlation matrix
    upper_triangle = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    
    # Find columns to drop
    to_drop = []
    
    if keep == 'first':
        to_drop = [column for column in upper_triangle.columns 
                   if any(upper_triangle[column] > threshold)]
    elif keep == 'last':
        to_drop = [column for column in upper_triangle.index 
                   if any(upper_triangle.loc[column] > threshold)]
    else:
        raise ValueError("keep must be 'first' or 'last'")
    
    # Drop columns from original DataFrame
    df_reduced = df.drop(columns=to_drop)
    
    print(f"Removed {len(to_drop)} highly correlated features (threshold={threshold})")
    
    return df_reduced, to_drop


def correlation_with_target(
    X: pd.DataFrame,
    y: pd.Series,
    method: str = 'pearson',
    plot: bool = True,
    figsize: tuple = (10, 6),
    top_n: Optional[int] = None
) -> pd.Series:
    """
    Calculate and visualize correlations between features and target variable.
    
    Parameters:
    -----------
    X : pd.DataFrame
        Feature DataFrame
    y : pd.Series
        Target variable
    method : str, default='pearson'
        Correlation method: 'pearson', 'spearman', or 'kendall'
    plot : bool, default=True
        Whether to create a visualization
    figsize : tuple, default=(10, 6)
        Figure size for the plot
    top_n : int, optional
        Show only top N features. If None, shows all
        
    Returns:
    --------
    pd.Series
        Correlations sorted by absolute value (descending)
        
    Example:
    --------
    >>> correlations = correlation.correlation_with_target(X, y, top_n=15)
    """
    if not isinstance(y, pd.Series):
        y = pd.Series(y)
    
    X_numeric = X.select_dtypes(include=[np.number])
    
    # Calculate correlations
    correlations = X_numeric.corrwith(y, method=method)
    correlations = correlations.sort_values(key=abs, ascending=False)
    
    if top_n:
        correlations_to_plot = correlations.head(top_n)
    else:
        correlations_to_plot = correlations
    
    if plot:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.figure(figsize=figsize)
            colors = ['green' if x > 0 else 'red' for x in correlations_to_plot.values]
            
            plt.barh(range(len(correlations_to_plot)), correlations_to_plot.values, color=colors)
            plt.yticks(range(len(correlations_to_plot)), correlations_to_plot.index)
            plt.xlabel('Correlation Coefficient', fontsize=12)
            plt.ylabel('Features', fontsize=12)
            plt.title('Feature Correlation with Target', fontsize=14, fontweight='bold')
            plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
            plt.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            plt.show()
        except ImportError:
            warnings.warn("matplotlib or seaborn not available. Skipping plot.")
    
    return correlations
