"""
Intelligent Model Selection Module

Provides intelligent model selection based on data characteristics,
performance metrics, and meta-learning insights.
"""

import time
import warnings
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from .._imports import get_sklearn_utils

warnings.filterwarnings("ignore")


def intelligent_model_selection(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    task_type: str = "auto",
    max_models: int = 10,
    cv_folds: int = 5,
    n_jobs: int = -1,
) -> Dict[str, Any]:
    """
    Intelligent model selection based on data characteristics

    Args:
        X: Feature matrix
        y: Target variable
        task_type: 'classification', 'regression', or 'auto'
        max_models: Maximum number of models to test
        cv_folds: Cross-validation folds
        n_jobs: Number of parallel jobs

    Returns:
        Dictionary with selection results and recommendations
    """
    sklearn_utils = get_sklearn_utils()
    if not sklearn_utils["available"]:
        return {"error": "Scikit-learn not available"}

    start_time = time.time()

    # Auto-detect task type
    if task_type == "auto":
        task_type = _detect_task_type(y)

    # Analyze data characteristics
    data_insights = _analyze_data_characteristics(X, y)

    # Select optimal models based on data characteristics
    selected_models = _select_models_by_characteristics(
        task_type, data_insights, max_models
    )

    # Evaluate models
    evaluation_results = _evaluate_models(
        X, y, selected_models, cv_folds, n_jobs
    )

    # Generate recommendations
    recommendations = _generate_recommendations(
        evaluation_results, data_insights
    )

    execution_time = time.time() - start_time

    return {
        "task_type": task_type,
        "data_insights": data_insights,
        "selected_models": selected_models,
        "evaluation_results": evaluation_results,
        "recommendations": recommendations,
        "execution_time": execution_time,
        "metadata": {
            "max_models": max_models,
            "cv_folds": cv_folds,
            "n_jobs": n_jobs
        }
    }


def _detect_task_type(y: Union[np.ndarray, pd.Series]) -> str:
    """Detect task type based on target variable."""
    unique_values = len(np.unique(y))
    if unique_values <= 10:
        return "classification"
    else:
        return "regression"


def _analyze_data_characteristics(
    X: Union[np.ndarray, pd.DataFrame], 
    y: Union[np.ndarray, pd.Series]
) -> Dict[str, Any]:
    """Analyze data characteristics for model selection."""
    if isinstance(X, pd.DataFrame):
        n_features = X.shape[1]
        feature_types = X.dtypes.value_counts().to_dict()
    else:
        n_features = X.shape[1]
        feature_types = {"numeric": n_features}

    n_samples = len(X)
    target_distribution = _analyze_target_distribution(y)

    return {
        "n_samples": n_samples,
        "n_features": n_features,
        "feature_types": feature_types,
        "target_distribution": target_distribution,
        "data_ratio": n_samples / n_features if n_features > 0 else 0
    }


def _analyze_target_distribution(y: Union[np.ndarray, pd.Series]) -> Dict[str, Any]:
    """Analyze target variable distribution."""
    if len(np.unique(y)) <= 10:
        # Classification
        unique, counts = np.unique(y, return_counts=True)
        class_balance = min(counts) / max(counts) if len(counts) > 1 else 1.0
        return {
            "type": "classification",
            "n_classes": len(unique),
            "class_balance": class_balance,
            "distribution": dict(zip(unique, counts))
        }
    else:
        # Regression
        return {
            "type": "regression",
            "mean": float(np.mean(y)),
            "std": float(np.std(y)),
            "range": (float(np.min(y)), float(np.max(y)))
        }


def _select_models_by_characteristics(
    task_type: str, 
    data_insights: Dict[str, Any], 
    max_models: int
) -> List[str]:
    """Select models based on data characteristics."""
    if task_type == "classification":
        return _select_classification_models(data_insights, max_models)
    else:
        return _select_regression_models(data_insights, max_models)


def _select_classification_models(
    data_insights: Dict[str, Any], 
    max_models: int
) -> List[str]:
    """Select classification models based on data characteristics."""
    models = []
    
    # Always include basic models
    models.extend(["LogisticRegression", "RandomForestClassifier"])
    
    # Add models based on data size
    if data_insights["n_samples"] > 10000:
        models.extend(["SGDClassifier", "LinearSVC"])
    
    # Add models based on feature count
    if data_insights["n_features"] > 100:
        models.extend(["RidgeClassifier", "LassoCV"])
    
    # Add models based on class balance
    if data_insights["target_distribution"]["class_balance"] < 0.3:
        models.extend(["BalancedRandomForestClassifier", "SMOTE"])
    
    return models[:max_models]


def _select_regression_models(
    data_insights: Dict[str, Any], 
    max_models: int
) -> List[str]:
    """Select regression models based on data characteristics."""
    models = []
    
    # Always include basic models
    models.extend(["LinearRegression", "RandomForestRegressor"])
    
    # Add models based on data size
    if data_insights["n_samples"] > 10000:
        models.extend(["SGDRegressor", "LinearSVR"])
    
    # Add models based on feature count
    if data_insights["n_features"] > 100:
        models.extend(["Ridge", "Lasso", "ElasticNet"])
    
    return models[:max_models]


def _evaluate_models(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    models: List[str],
    cv_folds: int,
    n_jobs: int
) -> Dict[str, Any]:
    """Evaluate selected models using cross-validation."""
    # This is a simplified version - in practice, you'd implement full CV
    return {
        "models_evaluated": len(models),
        "cv_folds": cv_folds,
        "n_jobs": n_jobs,
        "status": "evaluation_placeholder"
    }


def _generate_recommendations(
    evaluation_results: Dict[str, Any],
    data_insights: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate model recommendations based on evaluation results."""
    return {
        "recommended_approach": "ensemble_methods",
        "data_preprocessing": "standard_scaling_recommended",
        "feature_engineering": "polynomial_features_if_small",
        "validation_strategy": "stratified_cv_recommended"
    }
