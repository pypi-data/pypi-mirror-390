"""
Advanced Analysis Functions

Advanced analysis capabilities for deeper data insights.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


def analyze_correlations(
    df: pd.DataFrame,
    method: str = "pearson",
    threshold: float = 0.5
) -> Dict[str, Any]:
    """Analyze correlations between numeric variables."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return {"error": "No numeric columns found"}
    
    # Calculate correlation matrix
    corr_matrix = numeric_df.corr(method=method)
    
    # Find strong correlations
    strong_correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                strong_correlations.append({
                    "var1": corr_matrix.columns[i],
                    "var2": corr_matrix.columns[j],
                    "correlation": float(corr_value),
                    "strength": "strong" if abs(corr_value) >= 0.8 else "moderate"
                })
    
    # Sort by absolute correlation value
    strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    
    return {
        "correlation_matrix": corr_matrix.to_dict(),
        "strong_correlations": strong_correlations,
        "method": method,
        "threshold": threshold
    }


def analyze_outliers(
    df: pd.DataFrame,
    method: str = "iqr",
    threshold: float = 1.5
) -> Dict[str, Any]:
    """Analyze outliers in numeric variables."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return {"error": "No numeric columns found"}
    
    outlier_analysis = {}
    
    for col in numeric_df.columns:
        col_data = numeric_df[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        if method == "iqr":
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            
        elif method == "zscore":
            z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
            outliers = col_data[z_scores > threshold]
        
        else:
            outliers = pd.Series(dtype=float)
        
        outlier_analysis[col] = {
            "outlier_count": len(outliers),
            "outlier_percentage": (len(outliers) / len(col_data)) * 100,
            "outlier_values": outliers.tolist(),
            "method": method,
            "threshold": threshold
        }
    
    return outlier_analysis


def analyze_distributions(
    df: pd.DataFrame,
    bins: int = 20
) -> Dict[str, Any]:
    """Analyze distribution characteristics of numeric variables."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return {"error": "No numeric columns found"}
    
    distribution_analysis = {}
    
    for col in numeric_df.columns:
        col_data = numeric_df[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        # Basic distribution statistics
        stats = {
            "mean": float(col_data.mean()),
            "median": float(col_data.median()),
            "std": float(col_data.std()),
            "skewness": float(col_data.skew()),
            "kurtosis": float(col_data.kurtosis()),
            "range": float(col_data.max() - col_data.min()),
            "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25))
        }
        
        # Distribution shape classification
        if abs(stats["skewness"]) < 0.5:
            shape = "approximately normal"
        elif stats["skewness"] > 0.5:
            shape = "right-skewed"
        else:
            shape = "left-skewed"
        
        # Kurtosis classification
        if stats["kurtosis"] < -0.5:
            kurtosis_type = "platykurtic (light-tailed)"
        elif stats["kurtosis"] > 0.5:
            kurtosis_type = "leptokurtic (heavy-tailed)"
        else:
            kurtosis_type = "mesokurtic (normal-tailed)"
        
        distribution_analysis[col] = {
            "statistics": stats,
            "shape": shape,
            "kurtosis_type": kurtosis_type,
            "is_normal": abs(stats["skewness"]) < 0.5 and abs(stats["kurtosis"]) < 0.5
        }
    
    return distribution_analysis
