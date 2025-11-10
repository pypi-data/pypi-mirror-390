"""
Model Evaluation Module
========================

This module provides utilities for quick model evaluation and visualization.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Union
import warnings


def quick_eval(
    y_true: Union[np.ndarray, pd.Series, List],
    y_pred: Union[np.ndarray, pd.Series, List],
    task_type: str = 'auto',
    show_plot: bool = True,
    figsize: tuple = (12, 5),
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Quick evaluation of model predictions with comprehensive metrics.
    
    Parameters:
    -----------
    y_true : array-like
        True target values
    y_pred : array-like
        Predicted target values
    task_type : str, default='auto'
        Type of task: 'classification', 'regression', or 'auto' (auto-detect)
    show_plot : bool, default=True
        Whether to display visualization
    figsize : tuple, default=(12, 5)
        Figure size for plots
    labels : list, optional
        Class labels for classification tasks
        
    Returns:
    --------
    dict
        Dictionary containing evaluation metrics
        
    Example:
    --------
    >>> from dshelper import evaluation
    >>> metrics = evaluation.quick_eval(y_test, y_pred)
    >>> print(f"Accuracy: {metrics['accuracy']:.3f}")
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Auto-detect task type
    if task_type == 'auto':
        unique_values = len(np.unique(y_true))
        if unique_values <= 20 and np.all(y_true == y_true.astype(int)):
            task_type = 'classification'
        else:
            task_type = 'regression'
        print(f"Auto-detected task type: {task_type}")
    
    if task_type == 'classification':
        return _eval_classification(y_true, y_pred, show_plot, figsize, labels)
    elif task_type == 'regression':
        return _eval_regression(y_true, y_pred, show_plot, figsize)
    else:
        raise ValueError(f"Unknown task_type: {task_type}")


def _eval_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    show_plot: bool,
    figsize: tuple,
    labels: Optional[List[str]]
) -> Dict[str, Any]:
    """Internal function for classification evaluation."""
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, classification_report, roc_auc_score
    )
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    
    # Handle binary vs multiclass
    average_method = 'binary' if len(np.unique(y_true)) == 2 else 'weighted'
    
    precision = precision_score(y_true, y_pred, average=average_method, zero_division=0)
    recall = recall_score(y_true, y_pred, average=average_method, zero_division=0)
    f1 = f1_score(y_true, y_pred, average=average_method, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Classification report
    report = classification_report(y_true, y_pred, zero_division=0, output_dict=True)
    
    # Try to calculate ROC AUC for binary classification
    roc_auc = None
    if len(np.unique(y_true)) == 2:
        try:
            roc_auc = roc_auc_score(y_true, y_pred)
        except:
            pass
    
    # Print summary
    print("\n" + "="*50)
    print("CLASSIFICATION EVALUATION RESULTS")
    print("="*50)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    if roc_auc:
        print(f"ROC AUC:   {roc_auc:.4f}")
    print("="*50 + "\n")
    
    # Visualization
    if show_plot:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            fig, axes = plt.subplots(1, 2, figsize=figsize)
            
            # Confusion Matrix
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                       xticklabels=labels, yticklabels=labels)
            axes[0].set_title('Confusion Matrix', fontsize=14, fontweight='bold')
            axes[0].set_ylabel('True Label', fontsize=11)
            axes[0].set_xlabel('Predicted Label', fontsize=11)
            
            # Metrics Bar Plot
            metrics_dict = {
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1 Score': f1
            }
            if roc_auc:
                metrics_dict['ROC AUC'] = roc_auc
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            axes[1].bar(metrics_dict.keys(), metrics_dict.values(), color=colors[:len(metrics_dict)])
            axes[1].set_ylim(0, 1)
            axes[1].set_title('Performance Metrics', fontsize=14, fontweight='bold')
            axes[1].set_ylabel('Score', fontsize=11)
            axes[1].axhline(y=0.5, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
            
            # Add value labels on bars
            for i, (k, v) in enumerate(metrics_dict.items()):
                axes[1].text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            plt.show()
        except ImportError:
            warnings.warn("matplotlib or seaborn not available. Skipping plot.")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'classification_report': report
    }


def _eval_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    show_plot: bool,
    figsize: tuple
) -> Dict[str, Any]:
    """Internal function for regression evaluation."""
    from sklearn.metrics import (
        mean_squared_error, mean_absolute_error, r2_score,
        mean_absolute_percentage_error
    )
    
    # Calculate metrics
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    try:
        mape = mean_absolute_percentage_error(y_true, y_pred)
    except:
        mape = None
    
    # Calculate residuals
    residuals = y_true - y_pred
    
    # Print summary
    print("\n" + "="*50)
    print("REGRESSION EVALUATION RESULTS")
    print("="*50)
    print(f"R² Score:  {r2:.4f}")
    print(f"RMSE:      {rmse:.4f}")
    print(f"MAE:       {mae:.4f}")
    print(f"MSE:       {mse:.4f}")
    if mape:
        print(f"MAPE:      {mape:.4f}")
    print("="*50 + "\n")
    
    # Visualization
    if show_plot:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            fig, axes = plt.subplots(1, 3, figsize=figsize)
            
            # Actual vs Predicted
            axes[0].scatter(y_true, y_pred, alpha=0.6, edgecolors='k', linewidth=0.5)
            axes[0].plot([y_true.min(), y_true.max()], 
                        [y_true.min(), y_true.max()], 
                        'r--', lw=2, label='Perfect Prediction')
            axes[0].set_xlabel('Actual Values', fontsize=11)
            axes[0].set_ylabel('Predicted Values', fontsize=11)
            axes[0].set_title('Actual vs Predicted', fontsize=12, fontweight='bold')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # Residuals Plot
            axes[1].scatter(y_pred, residuals, alpha=0.6, edgecolors='k', linewidth=0.5)
            axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
            axes[1].set_xlabel('Predicted Values', fontsize=11)
            axes[1].set_ylabel('Residuals', fontsize=11)
            axes[1].set_title('Residual Plot', fontsize=12, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
            
            # Residuals Distribution
            axes[2].hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
            axes[2].axvline(x=0, color='r', linestyle='--', lw=2)
            axes[2].set_xlabel('Residuals', fontsize=11)
            axes[2].set_ylabel('Frequency', fontsize=11)
            axes[2].set_title('Residuals Distribution', fontsize=12, fontweight='bold')
            axes[2].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.show()
        except ImportError:
            warnings.warn("matplotlib or seaborn not available. Skipping plot.")
    
    return {
        'r2_score': r2,
        'rmse': rmse,
        'mae': mae,
        'mse': mse,
        'mape': mape,
        'residuals': residuals
    }


def compare_models(
    results: Dict[str, Dict[str, float]],
    metric: str = 'accuracy',
    figsize: tuple = (10, 6)
) -> pd.DataFrame:
    """
    Compare multiple models based on their metrics.
    
    Parameters:
    -----------
    results : dict
        Dictionary with model names as keys and metric dictionaries as values
        Example: {'Model1': {'accuracy': 0.85, 'f1': 0.83}, 'Model2': {...}}
    metric : str, default='accuracy'
        Primary metric to sort by
    figsize : tuple, default=(10, 6)
        Figure size for the plot
        
    Returns:
    --------
    pd.DataFrame
        Comparison DataFrame sorted by the specified metric
        
    Example:
    --------
    >>> results = {
    ...     'Logistic Regression': {'accuracy': 0.85, 'f1': 0.83},
    ...     'Random Forest': {'accuracy': 0.88, 'f1': 0.86}
    ... }
    >>> comparison = evaluation.compare_models(results, metric='accuracy')
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        warnings.warn("matplotlib or seaborn not available. Skipping plot.")
        return pd.DataFrame(results).T
    
    # Create DataFrame
    df = pd.DataFrame(results).T
    
    # Sort by metric if it exists
    if metric in df.columns:
        df = df.sort_values(metric, ascending=False)
    
    # Print comparison
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    print(df.to_string())
    print("="*60 + "\n")
    
    # Visualization
    fig, ax = plt.subplots(figsize=figsize)
    
    df.plot(kind='bar', ax=ax, width=0.8)
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Models', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    return df


def cross_val_summary(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5,
    scoring: Optional[Union[str, List[str]]] = None,
    show_plot: bool = True
) -> pd.DataFrame:
    """
    Perform cross-validation and summarize results.
    
    Parameters:
    -----------
    model : estimator
        Scikit-learn compatible model
    X : pd.DataFrame or np.ndarray
        Feature matrix
    y : pd.Series or np.ndarray
        Target variable
    cv : int, default=5
        Number of cross-validation folds
    scoring : str or list, optional
        Scoring metric(s) to use. If None, uses default for the estimator
    show_plot : bool, default=True
        Whether to display visualization
        
    Returns:
    --------
    pd.DataFrame
        Summary of cross-validation scores
        
    Example:
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> model = RandomForestClassifier()
    >>> cv_results = evaluation.cross_val_summary(
    ...     model, X, y, cv=5, scoring=['accuracy', 'f1']
    ... )
    """
    from sklearn.model_selection import cross_validate
    
    # Perform cross-validation
    if scoring is None:
        results = cross_validate(model, X, y, cv=cv, return_train_score=True)
    else:
        if isinstance(scoring, str):
            scoring = [scoring]
        results = cross_validate(model, X, y, cv=cv, scoring=scoring, return_train_score=True)
    
    # Create summary DataFrame
    summary_data = {}
    
    for key, values in results.items():
        if key.startswith('test_'):
            metric_name = key.replace('test_', '')
            summary_data[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
    
    summary_df = pd.DataFrame(summary_data).T
    
    # Print summary
    print("\n" + "="*60)
    print(f"CROSS-VALIDATION SUMMARY ({cv} folds)")
    print("="*60)
    print(summary_df.to_string())
    print("="*60 + "\n")
    
    # Visualization
    if show_plot:
        try:
            import matplotlib.pyplot as plt
            
            metrics = list(summary_data.keys())
            means = [summary_data[m]['mean'] for m in metrics]
            stds = [summary_data[m]['std'] for m in metrics]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            x_pos = np.arange(len(metrics))
            
            ax.bar(x_pos, means, yerr=stds, align='center', alpha=0.7, 
                   capsize=10, color='steelblue', edgecolor='black')
            ax.set_ylabel('Score', fontsize=12)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(metrics)
            ax.set_title(f'Cross-Validation Results ({cv} folds)', 
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for i, (m, s) in enumerate(zip(means, stds)):
                ax.text(i, m + s + 0.01, f'{m:.3f}±{s:.3f}', 
                       ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            plt.show()
        except ImportError:
            warnings.warn("matplotlib not available. Skipping plot.")
    
    return summary_df


def feature_importance_plot(
    model,
    feature_names: List[str],
    top_n: int = 20,
    figsize: tuple = (10, 8)
) -> pd.DataFrame:
    """
    Plot feature importances for tree-based models.
    
    Parameters:
    -----------
    model : estimator
        Trained model with feature_importances_ attribute
    feature_names : list
        List of feature names
    top_n : int, default=20
        Number of top features to display
    figsize : tuple, default=(10, 8)
        Figure size for the plot
        
    Returns:
    --------
    pd.DataFrame
        Feature importances sorted by importance
        
    Example:
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> model = RandomForestClassifier().fit(X_train, y_train)
    >>> importance_df = evaluation.feature_importance_plot(
    ...     model, X_train.columns.tolist()
    ... )
    """
    if not hasattr(model, 'feature_importances_'):
        raise ValueError("Model does not have feature_importances_ attribute")
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        raise ImportError("matplotlib and seaborn are required for plotting")
    
    # Create importance DataFrame
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    # Plot top N features
    top_features = importance_df.head(top_n)
    
    plt.figure(figsize=figsize)
    sns.barplot(data=top_features, x='Importance', y='Feature', palette='viridis')
    plt.title(f'Top {top_n} Feature Importances', fontsize=14, fontweight='bold')
    plt.xlabel('Importance', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, v in enumerate(top_features['Importance']):
        plt.text(v + 0.001, i, f'{v:.4f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    return importance_df
