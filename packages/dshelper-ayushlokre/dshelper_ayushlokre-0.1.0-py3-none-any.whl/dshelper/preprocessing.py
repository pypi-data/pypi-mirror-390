"""
Data Preprocessing Module
==========================

This module provides utilities for data preprocessing including scaling,
splitting, and encoding.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Union, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import warnings


def split_and_scale(
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    test_size: float = 0.2,
    random_state: Optional[int] = 42,
    scaler: str = 'standard',
    stratify: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into train/test sets and apply scaling in one step.
    
    Parameters:
    -----------
    X : pd.DataFrame or np.ndarray
        Feature matrix
    y : pd.Series or np.ndarray
        Target variable
    test_size : float, default=0.2
        Proportion of dataset to include in test split
    random_state : int, optional, default=42
        Random seed for reproducibility
    scaler : str, default='standard'
        Type of scaler: 'standard', 'minmax', 'robust', or 'none'
    stratify : bool, default=False
        Whether to stratify split based on target variable
        
    Returns:
    --------
    tuple
        (X_train_scaled, X_test_scaled, y_train, y_test)
        
    Example:
    --------
    >>> from dshelper import preprocessing
    >>> X_train, X_test, y_train, y_test = preprocessing.split_and_scale(
    ...     X, y, test_size=0.3, scaler='minmax'
    ... )
    """
    # Convert to numpy if needed
    if isinstance(X, pd.DataFrame):
        X_values = X.values
        feature_names = X.columns.tolist()
    else:
        X_values = X
        feature_names = None
    
    if isinstance(y, pd.Series):
        y_values = y.values
    else:
        y_values = y
    
    # Split data
    stratify_param = y_values if stratify else None
    X_train, X_test, y_train, y_test = train_test_split(
        X_values, y_values,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_param
    )
    
    # Apply scaling
    if scaler.lower() == 'standard':
        scaler_obj = StandardScaler()
    elif scaler.lower() == 'minmax':
        scaler_obj = MinMaxScaler()
    elif scaler.lower() == 'robust':
        scaler_obj = RobustScaler()
    elif scaler.lower() == 'none':
        return X_train, X_test, y_train, y_test
    else:
        raise ValueError(f"Unknown scaler type: {scaler}. Use 'standard', 'minmax', 'robust', or 'none'")
    
    # Fit on training data only
    X_train_scaled = scaler_obj.fit_transform(X_train)
    X_test_scaled = scaler_obj.transform(X_test)
    
    print(f"✓ Data split: Train={len(X_train)}, Test={len(X_test)}")
    print(f"✓ Scaling applied: {scaler.capitalize()}Scaler")
    
    return X_train_scaled, X_test_scaled, y_train, y_test


def create_scaler(
    scaler_type: str = 'standard',
    **kwargs
):
    """
    Create a scaler object with specified parameters.
    
    Parameters:
    -----------
    scaler_type : str, default='standard'
        Type of scaler: 'standard', 'minmax', or 'robust'
    **kwargs : dict
        Additional parameters for the scaler
        
    Returns:
    --------
    scaler object
        Configured scaler object
        
    Example:
    --------
    >>> scaler = preprocessing.create_scaler('minmax', feature_range=(0, 1))
    >>> X_scaled = scaler.fit_transform(X_train)
    """
    if scaler_type.lower() == 'standard':
        return StandardScaler(**kwargs)
    elif scaler_type.lower() == 'minmax':
        return MinMaxScaler(**kwargs)
    elif scaler_type.lower() == 'robust':
        return RobustScaler(**kwargs)
    else:
        raise ValueError(f"Unknown scaler type: {scaler_type}")


def encode_categorical(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'onehot',
    drop_first: bool = False,
    handle_unknown: str = 'ignore'
) -> pd.DataFrame:
    """
    Encode categorical variables using various methods.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : list, optional
        Columns to encode. If None, encodes all object/category columns
    method : str, default='onehot'
        Encoding method: 'onehot', 'label', or 'ordinal'
    drop_first : bool, default=False
        Whether to drop first category to avoid multicollinearity (for onehot)
    handle_unknown : str, default='ignore'
        How to handle unknown categories: 'ignore' or 'error'
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with encoded columns
        
    Example:
    --------
    >>> df_encoded = preprocessing.encode_categorical(
    ...     df, columns=['category', 'type'], method='onehot'
    ... )
    """
    df_result = df.copy()
    
    if columns is None:
        columns = df_result.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not columns:
        warnings.warn("No categorical columns found or specified.")
        return df_result
    
    if method == 'onehot':
        df_result = pd.get_dummies(
            df_result,
            columns=columns,
            drop_first=drop_first,
            dtype=int
        )
        print(f"✓ One-hot encoded {len(columns)} columns")
        
    elif method == 'label':
        from sklearn.preprocessing import LabelEncoder
        
        for col in columns:
            if col in df_result.columns:
                le = LabelEncoder()
                df_result[col] = le.fit_transform(df_result[col].astype(str))
        
        print(f"✓ Label encoded {len(columns)} columns")
        
    elif method == 'ordinal':
        from sklearn.preprocessing import OrdinalEncoder
        
        encoder = OrdinalEncoder(handle_unknown=handle_unknown)
        df_result[columns] = encoder.fit_transform(df_result[columns].astype(str))
        print(f"✓ Ordinal encoded {len(columns)} columns")
        
    else:
        raise ValueError(f"Unknown encoding method: {method}")
    
    return df_result


def handle_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'iqr',
    threshold: float = 1.5,
    action: str = 'remove'
) -> pd.DataFrame:
    """
    Detect and handle outliers in numerical columns.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : list, optional
        Columns to check for outliers. If None, uses all numeric columns
    method : str, default='iqr'
        Detection method: 'iqr' (Interquartile Range) or 'zscore'
    threshold : float, default=1.5
        Threshold for outlier detection (1.5 for IQR, 3 for z-score typically)
    action : str, default='remove'
        Action to take: 'remove', 'clip', or 'flag'
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with outliers handled according to specified action
        
    Example:
    --------
    >>> # Remove outliers using IQR method
    >>> df_clean = preprocessing.handle_outliers(df, method='iqr', action='remove')
    """
    df_result = df.copy()
    
    if columns is None:
        columns = df_result.select_dtypes(include=[np.number]).columns.tolist()
    
    outlier_mask = pd.Series([False] * len(df_result), index=df_result.index)
    
    for col in columns:
        if col not in df_result.columns:
            continue
        
        if method == 'iqr':
            Q1 = df_result[col].quantile(0.25)
            Q3 = df_result[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            col_outliers = (df_result[col] < lower_bound) | (df_result[col] > upper_bound)
            
            if action == 'remove':
                outlier_mask |= col_outliers
            elif action == 'clip':
                df_result[col] = df_result[col].clip(lower=lower_bound, upper=upper_bound)
            elif action == 'flag':
                df_result[f'{col}_outlier'] = col_outliers
                
        elif method == 'zscore':
            from scipy import stats
            z_scores = np.abs(stats.zscore(df_result[col].dropna()))
            col_outliers = pd.Series([False] * len(df_result), index=df_result.index)
            col_outliers.loc[df_result[col].notna()] = z_scores > threshold
            
            if action == 'remove':
                outlier_mask |= col_outliers
            elif action == 'clip':
                mean = df_result[col].mean()
                std = df_result[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                df_result[col] = df_result[col].clip(lower=lower_bound, upper=upper_bound)
            elif action == 'flag':
                df_result[f'{col}_outlier'] = col_outliers
        else:
            raise ValueError(f"Unknown method: {method}")
    
    if action == 'remove':
        original_len = len(df_result)
        df_result = df_result[~outlier_mask]
        removed = original_len - len(df_result)
        print(f"✓ Removed {removed} rows containing outliers ({removed/original_len*100:.2f}%)")
    
    return df_result


def feature_selection_quick(
    X: pd.DataFrame,
    y: Union[pd.Series, np.ndarray],
    k: int = 10,
    method: str = 'f_classif'
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Quick feature selection using statistical tests.
    
    Parameters:
    -----------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series or np.ndarray
        Target variable
    k : int, default=10
        Number of top features to select
    method : str, default='f_classif'
        Selection method: 'f_classif', 'f_regression', 'mutual_info_classif', 'mutual_info_regression'
        
    Returns:
    --------
    tuple
        (Selected features DataFrame, List of selected feature names)
        
    Example:
    --------
    >>> X_selected, selected_features = preprocessing.feature_selection_quick(
    ...     X, y, k=15, method='mutual_info_classif'
    ... )
    """
    from sklearn.feature_selection import SelectKBest, f_classif, f_regression
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
    
    # Map method strings to functions
    method_map = {
        'f_classif': f_classif,
        'f_regression': f_regression,
        'mutual_info_classif': mutual_info_classif,
        'mutual_info_regression': mutual_info_regression
    }
    
    if method not in method_map:
        raise ValueError(f"Unknown method: {method}")
    
    selector = SelectKBest(score_func=method_map[method], k=min(k, X.shape[1]))
    X_selected = selector.fit_transform(X, y)
    
    # Get selected feature names
    selected_mask = selector.get_support()
    selected_features = X.columns[selected_mask].tolist()
    
    print(f"✓ Selected {len(selected_features)} features using {method}")
    
    return pd.DataFrame(X_selected, columns=selected_features, index=X.index), selected_features
