"""
Meta Learning Module

Provides meta-learning capabilities for model selection and
hyperparameter optimization based on dataset characteristics.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd


def meta_learner(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    task_type: str = "auto",
    meta_features: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Meta-learning for intelligent model and hyperparameter selection.
    
    Args:
        X: Feature matrix
        y: Target variable
        task_type: Type of ML task
        meta_features: Pre-computed meta-features
        
    Returns:
        Dictionary with meta-learning recommendations
    """
    # Extract meta-features if not provided
    if meta_features is None:
        meta_features = _extract_meta_features(X, y)
    
    # Determine task type if auto
    if task_type == "auto":
        task_type = _detect_task_type(y)
    
    # Generate recommendations based on meta-features
    recommendations = _generate_meta_recommendations(
        meta_features, task_type
    )
    
    return {
        "meta_features": meta_features,
        "task_type": task_type,
        "recommendations": recommendations,
        "confidence": _calculate_confidence(meta_features)
    }


def _extract_meta_features(
    X: Union[np.ndarray, pd.DataFrame], 
    y: Union[np.ndarray, pd.Series]
) -> Dict[str, Any]:
    """Extract meta-features from dataset."""
    if isinstance(X, pd.DataFrame):
        n_features = X.shape[1]
        feature_types = X.dtypes.value_counts().to_dict()
    else:
        n_features = X.shape[1]
        feature_types = {"numeric": n_features}
    
    n_samples = len(X)
    
    # Statistical meta-features
    if isinstance(X, pd.DataFrame):
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            skewness = X[numeric_cols].skew().mean()
            kurtosis = X[numeric_cols].kurtosis().mean()
        else:
            skewness = kurtosis = 0.0
    else:
        skewness = float(np.mean([np.abs(np.mean(X[:, i])) for i in range(X.shape[1])]))
        kurtosis = float(np.mean([np.std(X[:, i]) for i in range(X.shape[1])]))
    
    return {
        "n_samples": n_samples,
        "n_features": n_features,
        "feature_types": feature_types,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "sparsity": _calculate_sparsity(X),
        "class_balance": _calculate_class_balance(y) if len(np.unique(y)) <= 10 else None
    }


def _detect_task_type(y: Union[np.ndarray, pd.Series]) -> str:
    """Detect ML task type from target variable."""
    unique_values = len(np.unique(y))
    if unique_values <= 10:
        return "classification"
    else:
        return "regression"


def _calculate_sparsity(X: Union[np.ndarray, pd.DataFrame]) -> float:
    """Calculate data sparsity."""
    if isinstance(X, pd.DataFrame):
        X_array = X.values
    else:
        X_array = X
    
    zero_count = np.sum(X_array == 0)
    total_elements = X_array.size
    
    return zero_count / total_elements if total_elements > 0 else 0.0


def _calculate_class_balance(y: Union[np.ndarray, pd.Series]) -> float:
    """Calculate class balance for classification tasks."""
    unique, counts = np.unique(y, return_counts=True)
    if len(counts) <= 1:
        return 1.0
    
    return min(counts) / max(counts)


def _generate_meta_recommendations(
    meta_features: Dict[str, Any], 
    task_type: str
) -> Dict[str, Any]:
    """Generate recommendations based on meta-features."""
    recommendations = {
        "preprocessing": [],
        "model_selection": [],
        "hyperparameter_tuning": [],
        "validation_strategy": []
    }
    
    # Preprocessing recommendations
    if meta_features["sparsity"] > 0.8:
        recommendations["preprocessing"].append("handle_sparse_data")
    
    if meta_features["skewness"] > 1.0:
        recommendations["preprocessing"].append("apply_log_transformation")
    
    # Model selection recommendations
    if meta_features["n_samples"] < 1000:
        recommendations["model_selection"].append("use_simple_models")
    elif meta_features["n_samples"] > 100000:
        recommendations["model_selection"].append("use_scalable_models")
    
    if meta_features["n_features"] > 100:
        recommendations["model_selection"].append("use_feature_selection")
    
    # Validation strategy
    if task_type == "classification" and meta_features["class_balance"]:
        if meta_features["class_balance"] < 0.3:
            recommendations["validation_strategy"].append("use_stratified_cv")
    
    return recommendations


def _calculate_confidence(meta_features: Dict[str, Any]) -> float:
    """Calculate confidence in meta-learning recommendations."""
    # Simple confidence calculation based on data quality
    confidence = 0.5  # Base confidence
    
    if meta_features["n_samples"] > 1000:
        confidence += 0.2
    
    if meta_features["n_features"] < 100:
        confidence += 0.1
    
    if meta_features["sparsity"] < 0.5:
        confidence += 0.1
    
    return min(confidence, 1.0)
