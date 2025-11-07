"""
Centralized import management for QuickInsights library.

This module provides lazy imports and dependency checking to avoid
importing heavy libraries during package initialization.
"""

import warnings
from typing import Dict, Any, Optional

# Suppress warnings globally
warnings.filterwarnings("ignore")

# Core scientific libraries (always available)
import numpy as np
import pandas as pd

# Optional ML libraries - lazy loading
_ML_LIBS = {}


def get_sklearn_utils():
    """Get scikit-learn utilities if available."""
    if "sklearn" not in _ML_LIBS:
        try:
            from sklearn.model_selection import (
                GridSearchCV,
                RandomizedSearchCV,
                cross_val_score,
                StratifiedKFold,
                KFold,
                train_test_split,
            )
            from sklearn.ensemble import (
                RandomForestClassifier,
                RandomForestRegressor,
                GradientBoostingClassifier,
                GradientBoostingRegressor,
            )
            from sklearn.linear_model import (
                LogisticRegression,
                LinearRegression,
                Ridge,
                Lasso,
                ElasticNet,
            )
            from sklearn.svm import SVC, SVR
            from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
            from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
            from sklearn.naive_bayes import GaussianNB
            from sklearn.metrics import (
                accuracy_score,
                precision_score,
                recall_score,
                f1_score,
                mean_squared_error,
                r2_score,
                classification_report,
            )
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            from sklearn.feature_selection import SelectKBest, f_classif, f_regression
            from sklearn.cluster import KMeans, DBSCAN
            from sklearn.ensemble import IsolationForest
            from sklearn.decomposition import PCA
            from sklearn.metrics import silhouette_score

            _ML_LIBS["sklearn"] = {
                "available": True,
                "version": "loaded",
                "GridSearchCV": GridSearchCV,
                "RandomizedSearchCV": RandomizedSearchCV,
                "cross_val_score": cross_val_score,
                "StratifiedKFold": StratifiedKFold,
                "KFold": KFold,
                "train_test_split": train_test_split,
                "RandomForestClassifier": RandomForestClassifier,
                "RandomForestRegressor": RandomForestRegressor,
                "GradientBoostingClassifier": GradientBoostingClassifier,
                "GradientBoostingRegressor": GradientBoostingRegressor,
                "LogisticRegression": LogisticRegression,
                "LinearRegression": LinearRegression,
                "Ridge": Ridge,
                "Lasso": Lasso,
                "ElasticNet": ElasticNet,
                "SVC": SVC,
                "SVR": SVR,
                "KNeighborsClassifier": KNeighborsClassifier,
                "KNeighborsRegressor": KNeighborsRegressor,
                "DecisionTreeClassifier": DecisionTreeClassifier,
                "DecisionTreeRegressor": DecisionTreeRegressor,
                "GaussianNB": GaussianNB,
                "accuracy_score": accuracy_score,
                "precision_score": precision_score,
                "recall_score": recall_score,
                "f1_score": f1_score,
                "mean_squared_error": mean_squared_error,
                "r2_score": r2_score,
                "classification_report": classification_report,
                "StandardScaler": StandardScaler,
                "LabelEncoder": LabelEncoder,
                "SelectKBest": SelectKBest,
                "f_classif": f_classif,
                "f_regression": f_regression,
                "KMeans": KMeans,
                "DBSCAN": DBSCAN,
                "IsolationForest": IsolationForest,
                "PCA": PCA,
                "silhouette_score": silhouette_score,
            }
        except ImportError as e:
            _ML_LIBS["sklearn"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["sklearn"]


def get_torch_utils():
    """Get PyTorch utilities if available."""
    if "torch" not in _ML_LIBS:
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim

            _ML_LIBS["torch"] = {
                "available": True,
                "version": torch.__version__,
                "torch": torch,
                "nn": nn,
                "optim": optim,
            }
        except ImportError as e:
            _ML_LIBS["torch"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["torch"]


def get_lightgbm_utils():
    """Get LightGBM utilities if available."""
    if "lightgbm" not in _ML_LIBS:
        try:
            import lightgbm as lgb

            _ML_LIBS["lightgbm"] = {
                "available": True,
                "version": lgb.__version__,
                "LGBMClassifier": lgb.LGBMClassifier,
                "LGBMRegressor": lgb.LGBMRegressor,
            }
        except ImportError as e:
            _ML_LIBS["lightgbm"] = {
                "available": False,
                "error": str(e),
                "version": None,
            }

    return _ML_LIBS["lightgbm"]


def get_xgboost_utils():
    """Get XGBoost utilities if available."""
    if "xgboost" not in _ML_LIBS:
        try:
            import xgboost as xgb

            _ML_LIBS["xgboost"] = {
                "available": True,
                "version": xgb.__version__,
                "XGBClassifier": xgb.XGBClassifier,
                "XGBRegressor": xgb.XGBRegressor,
            }
        except ImportError as e:
            _ML_LIBS["xgboost"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["xgboost"]


def get_shap_utils():
    """Get SHAP utilities if available."""
    if "shap" not in _ML_LIBS:
        try:
            import shap

            _ML_LIBS["shap"] = {
                "available": True,
                "version": shap.__version__,
                "TreeExplainer": shap.TreeExplainer,
                "LinearExplainer": shap.LinearExplainer,
                "summary_plot": shap.summary_plot,
                "waterfall_plot": shap.waterfall_plot,
            }
        except ImportError as e:
            _ML_LIBS["shap"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["shap"]


def get_cupy_utils():
    """Get CuPy utilities if available."""
    if "cupy" not in _ML_LIBS:
        try:
            import cupy as cp

            _ML_LIBS["cupy"] = {
                "available": True,
                "version": cp.__version__,
                "cupy": cp,
            }
        except ImportError as e:
            _ML_LIBS["cupy"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["cupy"]


def get_qiskit_utils():
    """Get Qiskit utilities if available."""
    if "qiskit" not in _ML_LIBS:
        try:
            import qiskit

            _ML_LIBS["qiskit"] = {
                "available": True,
                "version": qiskit.__version__,
                "qiskit": qiskit,
            }
        except ImportError as e:
            _ML_LIBS["qiskit"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["qiskit"]


def get_dask_utils():
    """Get Dask utilities if available."""
    if "dask" not in _ML_LIBS:
        try:
            import dask.dataframe as dd
            import dask.array as da

            _ML_LIBS["dask"] = {
                "available": True,
                "version": "loaded",
                "DataFrame": dd,
                "Array": da,
            }
        except ImportError as e:
            _ML_LIBS["dask"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["dask"]


def get_scipy_utils():
    """Get SciPy utilities if available."""
    if "scipy" not in _ML_LIBS:
        try:
            from scipy import stats

            _ML_LIBS["scipy"] = {"available": True, "version": "loaded", "stats": stats}
        except ImportError as e:
            _ML_LIBS["scipy"] = {"available": False, "error": str(e), "version": None}

    return _ML_LIBS["scipy"]


def check_dependencies() -> Dict[str, bool]:
    """Check availability of all optional dependencies."""
    deps = {}

    # Check ML libraries
    sklearn_status = get_sklearn_utils()
    deps["sklearn"] = sklearn_status["available"]

    torch_status = get_torch_utils()
    deps["torch"] = torch_status["available"]

    lightgbm_status = get_lightgbm_utils()
    deps["lightgbm"] = lightgbm_status["available"]

    xgboost_status = get_xgboost_utils()
    deps["xgboost"] = xgboost_status["available"]

    shap_status = get_shap_utils()
    deps["shap"] = shap_status["available"]

    cupy_status = get_cupy_utils()
    deps["cupy"] = cupy_status["available"]

    qiskit_status = get_qiskit_utils()
    deps["qiskit"] = qiskit_status["available"]

    dask_status = get_dask_utils()
    deps["dask"] = dask_status["available"]

    scipy_status = get_scipy_utils()
    deps["scipy"] = scipy_status["available"]

    return deps


def get_dependency_info() -> Dict[str, Dict[str, Any]]:
    """Get detailed information about all dependencies."""
    return {
        "sklearn": get_sklearn_utils(),
        "torch": get_torch_utils(),
        "lightgbm": get_lightgbm_utils(),
        "xgboost": get_xgboost_utils(),
        "shap": get_shap_utils(),
        "cupy": get_cupy_utils(),
        "qiskit": get_qiskit_utils(),
        "dask": get_dask_utils(),
        "scipy": get_scipy_utils(),
    }
