"""
QuickInsights - AI-Powered Data Insights Engine

This module provides AI-powered data analysis with automatic pattern recognition,
anomaly detection and intelligent insights using machine learning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import warnings

warnings.filterwarnings("ignore")


# Lazy loading of ML libraries
def _get_ml_libraries():
    """Get ML libraries with lazy loading."""
    from ._imports import get_sklearn_utils, get_scipy_utils

    sklearn_utils = get_sklearn_utils()
    scipy_utils = get_scipy_utils()

    return sklearn_utils, scipy_utils


# Check availability without printing
def _check_ml_availability():
    """Check ML library availability silently."""
    sklearn_utils, scipy_utils = _get_ml_libraries()
    return sklearn_utils["available"], scipy_utils["available"]


# Global availability flags
SKLEARN_AVAILABLE, SCIPY_AVAILABLE = _check_ml_availability()


class AIInsightEngine:
    """
    AI-powered data insights engine

    Goes beyond traditional statistical methods to provide AI-based
    pattern recognition, anomaly detection and intelligent insights.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize AIInsightEngine

        Parameters
        ----------
        df : pd.DataFrame
            Data to analyze
        """
        # Empty DataFrame check
        if df.empty:
            raise ValueError(
                "AIInsightEngine cannot be initialized with empty DataFrame"
            )

        self.df = df.copy()
        self.insights = {}
        self.patterns = {}
        self.anomalies = {}
        self.trends = {}

        # Determine data types
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        # Prepare data for AI analysis
        self._prepare_data()

    def _prepare_data(self):
        """Prepare data for AI analysis"""
        # Normalize numerical data
        if len(self.numeric_cols) > 0 and SKLEARN_AVAILABLE:
            try:
                sklearn_utils = _get_ml_libraries()[0]
                StandardScaler = sklearn_utils["StandardScaler"]
                self.scaler = StandardScaler()
                self.df_scaled = pd.DataFrame(
                    self.scaler.fit_transform(self.df[self.numeric_cols]),
                    columns=self.numeric_cols,
                    index=self.df.index,
                )
            except Exception as e:
                # Silently handle errors without printing
                self.df_scaled = self.df[self.numeric_cols].copy()
        else:
            self.df_scaled = (
                self.df[self.numeric_cols].copy()
                if len(self.numeric_cols) > 0
                else pd.DataFrame()
            )

        # Encode categorical data
        self.label_encoders = {}
        self.df_encoded = self.df.copy()

        if SKLEARN_AVAILABLE:
            try:
                sklearn_utils = _get_ml_libraries()[0]
                LabelEncoder = sklearn_utils["LabelEncoder"]

                for col in self.categorical_cols:
                    try:
                        le = LabelEncoder()
                        self.df_encoded[col] = le.fit_transform(
                            self.df[col].astype(str)
                        )
                        self.label_encoders[col] = le
                    except Exception:
                        # Handle encoding errors silently
                        pass
            except Exception:
                # Handle sklearn import errors silently
                pass

    def discover_patterns(self, max_patterns: int = 10) -> Dict[str, Any]:
        """
        Discover patterns in the data using AI techniques

        Parameters
        ----------
        max_patterns : int, default=10
            Maximum number of patterns to discover

        Returns
        -------
        Dict[str, Any]
            Discovered patterns
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}

        try:
            patterns = {}

            # Linear correlations
            if len(self.numeric_cols) > 1:
                correlations = self._discover_correlations()
                if correlations:
                    patterns["correlations"] = correlations[: max_patterns // 2]

            # Sequential patterns
            if len(self.datetime_cols) > 0:
                sequential = self._discover_sequential_patterns()
                if sequential:
                    patterns["sequential"] = sequential

            # Categorical patterns
            if len(self.categorical_cols) > 0:
                categorical = self._discover_categorical_patterns()
                if categorical:
                    patterns["categorical"] = categorical

            # Feature importance patterns
            if len(self.numeric_cols) > 1:
                importance = self._discover_feature_importance()
                if importance:
                    patterns["feature_importance"] = importance

            return patterns

        except Exception as e:
            return {"error": f"Pattern discovery failed: {str(e)}"}

    def _discover_clustering_patterns(self) -> Dict[str, Any]:
        """Clustering pattern'larını keşfeder"""
        patterns = {}

        # Optimal cluster sayısını bul
        if len(self.numeric_cols) >= 2:
            # PCA ile boyut azaltma
            pca = PCA(n_components=min(3, len(self.numeric_cols)))
            data_pca = pca.fit_transform(self.df_scaled)

            # K-means için optimal k bulma
            inertias = []
            silhouette_scores = []
            k_range = range(2, min(11, len(self.df) // 10))

            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(data_pca)
                inertias.append(kmeans.inertia_)

                if k > 1:
                    silhouette_scores.append(silhouette_score(data_pca, kmeans.labels_))
                else:
                    silhouette_scores.append(0)

            # Elbow method ile optimal k
            optimal_k = k_range[np.argmax(silhouette_scores)]

            # Optimal clustering
            optimal_kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            optimal_kmeans.fit(data_pca)

            patterns["optimal_clusters"] = optimal_k
            patterns["cluster_labels"] = optimal_kmeans.labels_.tolist()
            patterns["silhouette_score"] = silhouette_score(
                data_pca, optimal_kmeans.labels_
            )
            patterns["explained_variance"] = pca.explained_variance_ratio_.tolist()

            # Cluster karakteristikleri
            cluster_centers = optimal_kmeans.cluster_centers_
            cluster_characteristics = []

            for i in range(optimal_k):
                cluster_mask = optimal_kmeans.labels_ == i
                cluster_data = self.df_scaled[cluster_mask]

                characteristics = {
                    "cluster_id": i,
                    "size": int(cluster_mask.sum()),
                    "percentage": float(cluster_mask.sum() / len(self.df) * 100),
                    "center": cluster_centers[i].tolist(),
                    "features": {},
                }

                # Her özellik için cluster karakteristikleri
                for j, col in enumerate(self.numeric_cols):
                    if j < len(cluster_centers[i]):
                        characteristics["features"][col] = {
                            "mean": float(cluster_data[col].mean()),
                            "std": float(cluster_data[col].std()),
                            "center_value": float(cluster_centers[i][j]),
                        }

                cluster_characteristics.append(characteristics)

            patterns["cluster_characteristics"] = cluster_characteristics

        return patterns

    def _discover_correlation_patterns(self) -> Dict[str, Any]:
        """Korelasyon pattern'larını keşfeder"""
        patterns = {}

        if len(self.numeric_cols) >= 2:
            # Pearson korelasyonu
            pearson_corr = self.df[self.numeric_cols].corr(method="pearson")

            # Spearman korelasyonu
            spearman_corr = self.df[self.numeric_cols].corr(method="spearman")

            # Güçlü korelasyonlar
            strong_correlations = []
            moderate_correlations = []

            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    col1, col2 = self.numeric_cols[i], self.numeric_cols[j]
                    pearson_val = pearson_corr.loc[col1, col2]
                    spearman_val = spearman_corr.loc[col1, col2]

                    correlation_info = {
                        "feature1": col1,
                        "feature2": col2,
                        "pearson": float(pearson_val),
                        "spearman": float(spearman_val),
                        "strength": (
                            "strong"
                            if abs(pearson_val) > 0.7
                            else "moderate"
                            if abs(pearson_val) > 0.3
                            else "weak"
                        ),
                    }

                    if abs(pearson_val) > 0.7:
                        strong_correlations.append(correlation_info)
                    elif abs(pearson_val) > 0.3:
                        moderate_correlations.append(correlation_info)

            patterns["strong_correlations"] = strong_correlations
            patterns["moderate_correlations"] = moderate_correlations
            patterns["pearson_matrix"] = pearson_corr.to_dict()
            patterns["spearman_matrix"] = spearman_corr.to_dict()

            # Non-linear relationships
            non_linear_patterns = self._discover_non_linear_patterns()
            patterns["non_linear_patterns"] = non_linear_patterns

        return patterns

    def _discover_non_linear_patterns(self) -> List[Dict[str, Any]]:
        """Non-linear pattern'ları keşfeder"""
        patterns = []

        if len(self.numeric_cols) >= 2:
            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    col1, col2 = self.numeric_cols[i], self.numeric_cols[j]

                    # Polynomial relationships
                    x = self.df[col1].values
                    y = self.df[col2].values

                    # 2nd degree polynomial fit
                    try:
                        coeffs = np.polyfit(x, y, 2)
                        y_pred = np.polyval(coeffs, x)
                        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum(
                            (y - np.mean(y)) ** 2
                        )

                        if r_squared > 0.7:
                            patterns.append(
                                {
                                    "type": "polynomial",
                                    "feature1": col1,
                                    "feature2": col2,
                                    "degree": 2,
                                    "r_squared": float(r_squared),
                                    "coefficients": coeffs.tolist(),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Linear pattern analizi hatası: {e}")
                        pass

                    # Exponential relationships
                    try:
                        # Log transformation
                        y_log = np.log(np.abs(y) + 1e-10)
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            x, y_log
                        )
                        r_squared = r_value**2

                        if r_squared > 0.7:
                            patterns.append(
                                {
                                    "type": "exponential",
                                    "feature1": col1,
                                    "feature2": col2,
                                    "r_squared": float(r_squared),
                                    "slope": float(slope),
                                    "intercept": float(intercept),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Exponential pattern analizi hatası: {e}")
                        pass

        return patterns

    def _discover_sequential_patterns(self) -> Dict[str, Any]:
        """Zaman serisi pattern'larını keşfeder"""
        patterns = {}

        if len(self.datetime_cols) > 0 and len(self.numeric_cols) > 0:
            time_col = self.datetime_cols[0]

            for numeric_col in self.numeric_cols[:3]:  # İlk 3 sayısal sütun
                # Zaman serisi analizi
                time_series = self.df.set_index(time_col)[numeric_col].sort_index()

                # Trend analizi
                try:
                    x = np.arange(len(time_series))
                    y = time_series.values

                    # Linear trend
                    slope, intercept, _, _, _ = stats.linregress(x, y)
                    trend_strength = slope**2

                    # Seasonality detection (basit)
                    if len(time_series) > 12:
                        # Monthly seasonality
                        monthly_means = time_series.groupby(
                            time_series.index.month
                        ).mean()
                        seasonality_strength = (
                            monthly_means.std() / monthly_means.mean()
                        )

                        patterns[f"{numeric_col}_trend"] = {
                            "slope": float(slope),
                            "trend_strength": float(trend_strength),
                            "p_value": float(
                                0
                            ),  # linregress does not return p_value directly
                            "seasonality_strength": float(seasonality_strength),
                        }
                except Exception as e:
                    print(f"⚠️  Trend analizi hatası: {e}")
                    pass

        return patterns

    def _discover_categorical_patterns(self) -> Dict[str, Any]:
        """Kategorik pattern'ları keşfeder"""
        patterns = {}

        for col in self.categorical_cols:
            if col in self.label_encoders:
                # Value counts
                value_counts = self.df[col].value_counts()

                # Entropy calculation
                probabilities = value_counts / len(self.df)
                entropy = -np.sum(probabilities * np.log2(probabilities))

                patterns[col] = {
                    "unique_values": int(value_counts.nunique()),
                    "entropy": float(entropy),
                    "most_common": (
                        value_counts.index[0] if len(value_counts) > 0 else None
                    ),
                    "most_common_count": (
                        int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
                    ),
                    "distribution": value_counts.to_dict(),
                }

        # Cross-categorical patterns
        if len(self.categorical_cols) >= 2:
            cross_patterns = []

            for i in range(len(self.categorical_cols)):
                for j in range(i + 1, len(self.categorical_cols)):
                    col1, col2 = self.categorical_cols[i], self.categorical_cols[j]

                    # Contingency table
                    contingency = pd.crosstab(self.df[col1], self.df[col2])

                    # Chi-square test
                    try:
                        chi2, p_value, dof, expected = stats.chi2_contingency(
                            contingency
                        )

                        if p_value < 0.05:  # Significant relationship
                            cross_patterns.append(
                                {
                                    "feature1": col1,
                                    "feature2": col2,
                                    "chi2": float(chi2),
                                    "p_value": float(p_value),
                                    "significant": True,
                                    "contingency_table": contingency.to_dict(),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Chi-square test hatası: {e}")
                        pass

            patterns["cross_categorical"] = cross_patterns

        return patterns

    def _discover_feature_importance(self) -> Dict[str, Any]:
        """Feature importance pattern'larını keşfeder"""
        patterns = {}

        if len(self.numeric_cols) >= 2:
            # Unsupervised feature importance (variance)
            variance_importance = self.df_scaled.var().sort_values(ascending=False)

            # Feature selection scores
            if len(self.numeric_cols) >= 3:
                try:
                    # F-regression scores (correlation with target)
                    # Use first numeric column as target for demonstration
                    target_col = self.numeric_cols[0]
                    feature_cols = self.numeric_cols[1:]

                    if len(feature_cols) > 0:
                        selector = SelectKBest(
                            score_func=f_regression, k=len(feature_cols)
                        )
                        X = self.df_scaled[feature_cols]
                        y = self.df_scaled[target_col]

                        selector.fit(X, y)
                        f_scores = selector.scores_
                        p_values = selector.pvalues_

                        feature_scores = []
                        for i, col in enumerate(feature_cols):
                            feature_scores.append(
                                {
                                    "feature": col,
                                    "f_score": float(f_scores[i]),
                                    "p_value": float(p_values[i]),
                                    "significant": p_values[i] < 0.05,
                                }
                            )

                        # Sort by f_score
                        feature_scores.sort(key=lambda x: x["f_score"], reverse=True)

                        patterns["feature_selection"] = {
                            "target": target_col,
                            "feature_scores": feature_scores,
                            "top_features": [f["feature"] for f in feature_scores[:5]],
                        }
                except Exception as e:
                    print(f"⚠️  Feature selection hatası: {e}")
                    pass

            patterns["variance_importance"] = variance_importance.to_dict()

        return patterns

    def detect_anomalies(self, method: str = "auto") -> Dict[str, Any]:
        """
        Detect anomalies in the data

        Parameters
        ----------
        method : str, default="auto"
            Anomaly detection method

        Returns
        -------
        Dict[str, Any]
            Anomaly detection results
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}

        try:
            anomalies = {}

            if method == "auto":
                # Try Isolation Forest first
                try:
                    sklearn_utils = _get_ml_libraries()[0]
                    IsolationForest = sklearn_utils["IsolationForest"]

                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    iso_forest.fit(self.df_scaled)
                    iso_scores = iso_forest.decision_function(self.df_scaled)

                    anomalies["isolation_forest"] = {
                        "scores": iso_scores.tolist(),
                        "anomaly_indices": np.where(
                            iso_scores < np.percentile(iso_scores, 10)
                        )[0].tolist(),
                    }
                    anomalies["best_method"] = "isolation_forest"

                except Exception:
                    # Fallback to statistical method
                    anomalies["statistical"] = self._statistical_anomaly_detection()
                    anomalies["best_method"] = "statistical"

            return anomalies

        except Exception as e:
            return {"error": f"Anomaly detection failed: {str(e)}"}

    def _detect_anomalies_isolation_forest(
        self, contamination: float
    ) -> Dict[str, Any]:
        """Isolation Forest ile anomali tespiti"""
        if len(self.numeric_cols) < 2:
            return {"error": "En az 2 sayısal sütun gerekli"}

        # PCA ile boyut azaltma
        pca = PCA(n_components=min(10, len(self.numeric_cols)))
        data_pca = pca.fit_transform(self.df_scaled)

        # Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(data_pca)

        # Anomalileri bul
        anomaly_indices = np.where(anomaly_labels == -1)[0]
        normal_indices = np.where(anomaly_labels == 1)[0]

        return {
            "anomaly_count": int(len(anomaly_indices)),
            "anomaly_percentage": float(len(anomaly_indices) / len(self.df) * 100),
            "anomaly_indices": anomaly_indices.tolist(),
            "normal_indices": normal_indices.tolist(),
            "anomaly_scores": iso_forest.decision_function(data_pca).tolist(),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
        }

    def _detect_anomalies_dbscan(self) -> Dict[str, Any]:
        """DBSCAN ile anomali tespiti"""
        if len(self.numeric_cols) < 2:
            return {"error": "En az 2 sayısal sütun gerekli"}

        # PCA ile boyut azaltma
        pca = PCA(n_components=min(5, len(self.numeric_cols)))
        data_pca = pca.fit_transform(self.df_scaled)

        # DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        cluster_labels = dbscan.fit_predict(data_pca)

        # Noise points (-1) anomalilerdir
        anomaly_indices = np.where(cluster_labels == -1)[0]
        normal_indices = np.where(cluster_labels != -1)[0]

        return {
            "anomaly_count": int(len(anomaly_indices)),
            "anomaly_percentage": float(len(anomaly_indices) / len(self.df) * 100),
            "anomaly_indices": anomaly_indices.tolist(),
            "normal_indices": normal_indices.tolist(),
            "cluster_count": int(
                len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            ),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
        }

    def _detect_anomalies_statistical(self) -> Dict[str, Any]:
        """İstatistiksel yöntemlerle anomali tespiti"""
        anomalies = {}

        for col in self.numeric_cols:
            # Z-score method
            z_scores = np.abs(stats.zscore(self.df[col]))
            z_anomalies = np.where(z_scores > 3)[0]

            # IQR method
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_anomalies = np.where(
                (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            )[0]

            anomalies[col] = {
                "z_score_anomalies": z_anomalies.tolist(),
                "z_score_count": int(len(z_anomalies)),
                "iqr_anomalies": iqr_anomalies.tolist(),
                "iqr_count": int(len(iqr_anomalies)),
                "iqr_bounds": {
                    "lower": float(lower_bound),
                    "upper": float(upper_bound),
                },
            }

        return anomalies

    def predict_trends(self, horizon: int = 5) -> Dict[str, Any]:
        """
        Predict future trends in the data

        Parameters
        ----------
        horizon : int, default=5
            Prediction horizon

        Returns
        -------
        Dict[str, Any]
            Trend predictions
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}

        try:
            trends = {}

            # Simple linear trend prediction
            for col in self.numeric_cols[:3]:  # First 3 numeric columns
                try:
                    x = np.arange(len(self.df))
                    y = self.df[col].values

                    # Linear regression
                    sklearn_utils = _get_ml_libraries()[0]
                    LinearRegression = sklearn_utils["LinearRegression"]

                    lr = LinearRegression()
                    lr.fit(x.reshape(-1, 1), y)

                    # Predict future values
                    future_x = np.arange(len(self.df), len(self.df) + horizon)
                    future_y = lr.predict(future_x.reshape(-1, 1))

                    trends[col] = {
                        "slope": float(lr.coef_[0]),
                        "intercept": float(lr.intercept_),
                        "future_values": future_y.tolist(),
                        "confidence": 0.8,  # Simple confidence score
                    }

                except Exception:
                    # If sklearn fails, use simple statistical trend
                    try:
                        x = np.arange(len(self.df))
                        y = self.df[col].values

                        # Simple linear trend using numpy
                        slope = np.polyfit(x, y, 1)[0]
                        intercept = np.polyfit(x, y, 1)[1]

                        # Predict future values
                        future_x = np.arange(len(self.df), len(self.df) + horizon)
                        future_y = slope * future_x + intercept

                        trends[col] = {
                            "slope": float(slope),
                            "intercept": float(intercept),
                            "future_values": future_y.tolist(),
                            "confidence": 0.6,  # Lower confidence for simple method
                        }
                    except Exception:
                        continue

            if trends:
                trends["best_model"] = "linear_regression"

            return trends

        except Exception as e:
            return {"error": f"Trend prediction failed: {str(e)}"}

    def generate_insights_report(self) -> Dict[str, Any]:
        """
        Kapsamlı insights raporu oluşturur

        Returns
        -------
        Dict[str, Any]
            Insights raporu
        """
        report = {
            "summary": {
                "total_rows": len(self.df),
                "total_columns": len(self.df.columns),
                "numeric_columns": len(self.numeric_cols),
                "categorical_columns": len(self.categorical_cols),
                "datetime_columns": len(self.datetime_cols),
            },
            "patterns": self.patterns,
            "anomalies": self.anomalies,
            "trends": self.trends,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Otomatik öneriler oluşturur"""
        recommendations = []

        # Data quality recommendations
        missing_percentage = (
            self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)) * 100
        )
        if missing_percentage > 10:
            recommendations.append(
                f"Veri setinde %{missing_percentage:.1f} eksik değer var. Data cleaning önerilir."
            )

        # Feature engineering recommendations
        if len(self.numeric_cols) >= 3:
            recommendations.append(
                "Çoklu sayısal değişkenler mevcut. Feature interaction'ları oluşturulabilir."
            )

        # Anomaly detection recommendations
        if "anomalies" in self.insights:
            anomaly_count = sum(
                len(anom.get("anomaly_indices", []))
                for anom in self.anomalies.values()
                if isinstance(anom, dict) and "anomaly_indices" in anom
            )
            if anomaly_count > 0:
                recommendations.append(
                    f"{anomaly_count} anomali tespit edildi. Detaylı inceleme önerilir."
                )

        # Clustering recommendations
        if "patterns" in self.insights and "clustering" in self.insights["patterns"]:
            cluster_count = self.insights["patterns"]["clustering"].get(
                "optimal_clusters", 0
            )
            if cluster_count > 1:
                recommendations.append(
                    f"{cluster_count} doğal cluster tespit edildi. Segmentasyon analizi yapılabilir."
                )

        # Correlation recommendations
        if "patterns" in self.insights and "correlations" in self.insights["patterns"]:
            strong_corr_count = len(
                self.insights["patterns"]["correlations"].get("strong_correlations", [])
            )
            if strong_corr_count > 0:
                recommendations.append(
                    f"{strong_corr_count} güçlü korelasyon tespit edildi. Multicollinearity kontrol edilmeli."
                )

        return recommendations

    def _discover_correlations(self) -> List[Dict[str, Any]]:
        """Discover correlations between numeric features"""
        correlations = []

        if len(self.numeric_cols) < 2:
            return correlations

        try:
            corr_matrix = self.df[self.numeric_cols].corr()

            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    col1 = self.numeric_cols[i]
                    col2 = self.numeric_cols[j]
                    corr_value = corr_matrix.loc[col1, col2]

                    if abs(corr_value) > 0.7:
                        correlations.append(
                            {
                                "feature1": col1,
                                "feature2": col2,
                                "correlation": float(corr_value),
                                "strength": "strong"
                                if abs(corr_value) > 0.8
                                else "moderate",
                            }
                        )

            # Sort by absolute correlation value
            correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        except Exception:
            pass

        return correlations

    def _discover_feature_importance(self) -> Dict[str, float]:
        """Discover feature importance using simple statistical methods"""
        importance = {}

        try:
            for col in self.numeric_cols:
                # Use variance as a simple importance measure
                importance[col] = float(self.df[col].var())

            # Normalize importance scores
            max_importance = max(importance.values()) if importance else 1
            importance = {k: v / max_importance for k, v in importance.items()}

        except Exception:
            pass

        return importance

    def _statistical_anomaly_detection(self) -> Dict[str, Any]:
        """Simple statistical anomaly detection"""
        anomalies = {}

        try:
            for col in self.numeric_cols:
                values = self.df[col].dropna()
                if len(values) > 0:
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1

                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outlier_indices = values[
                        (values < lower_bound) | (values > upper_bound)
                    ].index

                    anomalies[col] = {
                        "outlier_count": len(outlier_indices),
                        "outlier_indices": outlier_indices.tolist(),
                        "bounds": {
                            "lower": float(lower_bound),
                            "upper": float(upper_bound),
                        },
                    }
        except Exception:
            pass

        return anomalies


def auto_ai_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Otomatik AI analizi yapar

    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti

    Returns
    -------
    Dict[str, Any]
        AI analiz sonuçları
    """
    engine = AIInsightEngine(df)

    # Pattern discovery
    patterns = engine.discover_patterns()

    # Anomaly detection
    anomalies = engine.detect_anomalies()

    # Trend prediction (ilk sayısal sütun için)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    trends = {}
    if len(numeric_cols) > 0:
        trends = engine.predict_trends()

    # Comprehensive report
    report = engine.generate_insights_report()

    return {
        "patterns": patterns,
        "anomalies": anomalies,
        "trends": trends,
        "report": report,
    }
