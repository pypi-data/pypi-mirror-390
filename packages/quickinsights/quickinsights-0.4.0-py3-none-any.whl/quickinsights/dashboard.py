"""
QuickInsights - Interactive Dashboard Module

Bu modül veri analistlerinin sonuçlarını kolayca paylaşması için 
web-based dashboard oluşturma yetenekleri sağlar.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
import json
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")


class DashboardGenerator:
    """
    Interaktif dashboard oluşturucu

    Veri analizi sonuçlarını web-based dashboard'a dönüştürür.
    Stakeholder'larla paylaşım için HTML/JSON formatında çıktı verir.
    """

    def __init__(self, title: str = "QuickInsights Dashboard"):
        """
        Dashboard oluşturucu başlatıcısı

        Parameters
        ----------
        title : str, default="QuickInsights Dashboard"
            Dashboard başlığı
        """
        self.title = title
        self.sections = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "generator": "QuickInsights",
            "version": "0.2.0",
        }

    def add_dataset_overview(self, df: pd.DataFrame) -> "DashboardGenerator":
        """Veri seti genel bakış bölümü ekler"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        missing_data = df.isnull().sum()

        overview = {
            "type": "dataset_overview",
            "title": "📊 Veri Seti Genel Bakış",
            "data": {
                "shape": {"rows": len(df), "columns": len(df.columns)},
                "memory_usage_mb": round(
                    df.memory_usage(deep=True).sum() / 1024**2, 2
                ),
                "column_types": {
                    "numeric": len(numeric_cols),
                    "categorical": len(categorical_cols),
                    "other": len(df.columns)
                    - len(numeric_cols)
                    - len(categorical_cols),
                },
                "data_quality": {
                    "total_missing": missing_data.sum(),
                    "missing_percentage": round(
                        (missing_data.sum() / max(1, df.size)) * 100, 2
                    ),
                    "duplicate_rows": df.duplicated().sum(),
                    "duplicate_percentage": round(
                        (df.duplicated().sum() / max(1, len(df))) * 100, 2
                    ),
                },
                "column_details": {
                    "numeric_columns": numeric_cols[:10],  # Limit for display
                    "categorical_columns": categorical_cols[:10],
                },
            },
        }

        self.sections.append(overview)
        return self

    def add_summary_statistics(self, df: pd.DataFrame) -> "DashboardGenerator":
        """Özet istatistikler bölümü ekler"""

        numeric_df = df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) > 0:
            stats = {
                "type": "summary_statistics",
                "title": "📈 Özet İstatistikler",
                "data": {
                    "statistics": numeric_df.describe().round(3).to_dict(),
                    "correlation_summary": self._get_correlation_summary(numeric_df),
                    "distribution_insights": self._get_distribution_insights(
                        numeric_df
                    ),
                },
            }
            self.sections.append(stats)

        return self

    def add_missing_data_analysis(self, df: pd.DataFrame) -> "DashboardGenerator":
        """Eksik veri analizi bölümü ekler"""

        missing_data = df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]

        if len(missing_cols) > 0:
            missing_analysis = {
                "type": "missing_data_analysis",
                "title": "❓ Eksik Veri Analizi",
                "data": {
                    "missing_by_column": missing_cols.to_dict(),
                    "missing_percentage_by_column": ((missing_cols / len(df)) * 100)
                    .round(2)
                    .to_dict(),
                    "missing_patterns": self._analyze_missing_patterns(df),
                    "recommendations": self._get_missing_data_recommendations(
                        missing_cols, len(df)
                    ),
                },
            }
            self.sections.append(missing_analysis)

        return self

    def add_categorical_analysis(self, df: pd.DataFrame) -> "DashboardGenerator":
        """Kategorik değişken analizi bölümü ekler"""

        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if len(categorical_cols) > 0:
            categorical_data = {}

            for col in categorical_cols[:5]:  # Limit to first 5 columns
                value_counts = df[col].value_counts()
                categorical_data[col] = {
                    "unique_count": df[col].nunique(),
                    "unique_ratio": round(df[col].nunique() / len(df), 3),
                    "top_values": value_counts.head(10).to_dict(),
                    "missing_count": df[col].isnull().sum(),
                }

            categorical_analysis = {
                "type": "categorical_analysis",
                "title": "🏷️ Kategorik Değişken Analizi",
                "data": categorical_data,
            }

            self.sections.append(categorical_analysis)

        return self

    def add_insights_section(self, insights: List[str]) -> "DashboardGenerator":
        """Otomatik insight'lar bölümü ekler"""

        insights_section = {
            "type": "insights",
            "title": "🔍 Otomatik Bulgular",
            "data": {
                "insights": insights[:10],  # Top 10 insights
                "insight_count": len(insights),
            },
        }

        self.sections.append(insights_section)
        return self

    def add_recommendations_section(
        self, recommendations: List[str]
    ) -> "DashboardGenerator":
        """Öneriler bölümü ekler"""

        recommendations_section = {
            "type": "recommendations",
            "title": "💡 Öneriler",
            "data": {
                "recommendations": recommendations[:8],  # Top 8 recommendations
                "recommendation_count": len(recommendations),
            },
        }

        self.sections.append(recommendations_section)
        return self

    def add_data_quality_score(
        self, quality_score: float, quality_details: Dict[str, Any]
    ) -> "DashboardGenerator":
        """Veri kalitesi skoru bölümü ekler"""

        quality_section = {
            "type": "data_quality",
            "title": "🏆 Veri Kalitesi Skoru",
            "data": {
                # Backward/forward compatible keys
                "overall_score": round(quality_score, 1),
                "quality_score": round(quality_score, 1),
                "quality_level": self._get_quality_level(quality_score),
                "quality_breakdown": quality_details,
                "quality_details": quality_details,
                "improvement_areas": self._identify_improvement_areas(quality_details),
            },
        }

        self.sections.append(quality_section)
        return self

    def _get_correlation_summary(self, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Korelasyon özetini çıkarır"""
        if len(numeric_df.columns) < 2:
            return {"message": "Korelasyon analizi için en az 2 sayısal sütun gerekli"}

        corr_matrix = numeric_df.corr()

        # Find high correlations
        high_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_correlations.append(
                        {
                            "var1": corr_matrix.columns[i],
                            "var2": corr_matrix.columns[j],
                            "correlation": round(corr_val, 3),
                        }
                    )

        return {
            "high_correlations": high_correlations[:5],  # Top 5
            "correlation_matrix_shape": corr_matrix.shape,
            "average_correlation": round(
                corr_matrix.values[
                    np.triu_indices_from(corr_matrix.values, k=1)
                ].mean(),
                3,
            ),
        }

    def _get_distribution_insights(self, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Dağılım insight'larını çıkarır"""
        insights = {}

        for col in numeric_df.columns[:5]:  # First 5 columns
            series = numeric_df[col].dropna()
            if len(series) > 0:
                skewness = series.skew()
                kurtosis = series.kurtosis()

                insights[col] = {
                    "skewness": round(skewness, 3),
                    "kurtosis": round(kurtosis, 3),
                    "distribution_type": self._classify_distribution(
                        skewness, kurtosis
                    ),
                    "outlier_count": self._count_outliers(series),
                    "range": {
                        "min": round(series.min(), 3),
                        "max": round(series.max(), 3),
                        "span": round(series.max() - series.min(), 3),
                    },
                }

        return insights

    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """Dağılım tipini sınıflandırır"""
        if abs(skewness) < 0.5:
            if abs(kurtosis) < 3:
                return "Normal-benzeri"
            else:
                return "Normal-benzeri (heavy tails)"
        elif skewness > 1:
            return "Sağa çarpık"
        elif skewness < -1:
            return "Sola çarpık"
        else:
            return "Hafif çarpık"

    def _count_outliers(self, series: pd.Series) -> int:
        """IQR yöntemi ile outlier sayısını hesaplar"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        outliers = series[(series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)]
        return len(outliers)

    def _analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Eksik veri pattern'lerini analiz eder"""
        missing_matrix = df.isnull()

        # Complete cases
        complete_cases = (~missing_matrix.any(axis=1)).sum()
        complete_percentage = (complete_cases / len(df)) * 100

        # Columns with no missing data
        complete_columns = missing_matrix.sum()[
            missing_matrix.sum() == 0
        ].index.tolist()

        return {
            "complete_cases": complete_cases,
            "complete_cases_percentage": round(complete_percentage, 2),
            "complete_columns": complete_columns[:10],  # Limit display
            "missing_combinations": self._get_missing_combinations(missing_matrix),
        }

    def _get_missing_combinations(self, missing_matrix: pd.DataFrame) -> List[Dict]:
        """Eksik veri kombinasyonlarını bulur"""
        # Convert boolean to string for grouping
        missing_patterns = missing_matrix.astype(str)
        pattern_counts = missing_patterns.value_counts()

        # Return top 5 patterns
        top_patterns = []
        for pattern, count in pattern_counts.head(5).items():
            pattern_dict = dict(zip(missing_matrix.columns, pattern))
            top_patterns.append(
                {
                    "pattern": pattern_dict,
                    "count": count,
                    "percentage": round((count / len(missing_matrix)) * 100, 2),
                }
            )

        return top_patterns

    def _get_missing_data_recommendations(
        self, missing_cols: pd.Series, total_rows: int
    ) -> List[str]:
        """Eksik veri önerilerini oluşturur"""
        recommendations = []

        for col, missing_count in missing_cols.items():
            missing_pct = (missing_count / total_rows) * 100

            if missing_pct > 50:
                recommendations.append(
                    f"🔴 '{col}' sütununda %{missing_pct:.1f} eksik veri - silmeyi düşünün"
                )
            elif missing_pct > 20:
                recommendations.append(
                    f"🟡 '{col}' sütununda %{missing_pct:.1f} eksik veri - domain expertise ile doldurun"
                )
            elif missing_pct > 5:
                recommendations.append(
                    f"🟢 '{col}' sütununda %{missing_pct:.1f} eksik veri - istatistiksel yöntemle doldurun"
                )

        return recommendations[:5]  # Top 5

    def _get_quality_level(self, score: float) -> str:
        """Kalite seviyesini belirler"""
        if score >= 90:
            return "Mükemmel ⭐⭐⭐⭐⭐"
        elif score >= 80:
            return "İyi ⭐⭐⭐⭐"
        elif score >= 70:
            return "Orta ⭐⭐⭐"
        elif score >= 60:
            return "Zayıf ⭐⭐"
        else:
            return "Kritik ⭐"

    def _identify_improvement_areas(self, quality_details: Dict[str, Any]) -> List[str]:
        """İyileştirme alanlarını belirler"""
        areas = []

        if "missing_data_reduction_pct" in quality_details:
            if (
                quality_details["missing_data_reduction_pct"] < 0
            ):  # Missing data increased
                areas.append("Eksik veri yönetimi")

        if "duplicate_reduction_pct" in quality_details:
            if (
                quality_details["duplicate_reduction_pct"] < 5
            ):  # Low duplicate reduction
                areas.append("Kopya veri temizleme")

        if "memory_reduction_pct" in quality_details:
            if quality_details["memory_reduction_pct"] < 10:  # Low memory optimization
                areas.append("Veri tipi optimizasyonu")

        return areas[:3]  # Top 3

    def generate_html_dashboard(self, output_path: str = "dashboard.html") -> str:
        """HTML dashboard dosyası oluşturur"""

        html_template = self._get_html_template()

        # Convert sections to HTML
        sections_html = ""
        for section in self.sections:
            sections_html += self._section_to_html(section)

        # Replace placeholders
        html_content = html_template.replace("{{TITLE}}", self.title)
        html_content = html_content.replace("{{SECTIONS}}", sections_html)
        html_content = html_content.replace(
            "{{METADATA}}", json.dumps(self.metadata, indent=2)
        )
        html_content = html_content.replace(
            "{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Dashboard oluşturuldu: {output_path}")
        return output_path

    def generate_json_report(self, output_path: str = "dashboard_data.json") -> str:
        """JSON formatında rapor oluşturur"""

        report_data = {
            "title": self.title,
            "metadata": self.metadata,
            "sections": self.sections,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ JSON raporu oluşturuldu: {output_path}")
        return output_path

    def _section_to_html(self, section: Dict[str, Any]) -> str:
        """Bölümü HTML'e dönüştürür"""

        section_type = section["type"]
        title = section["title"]
        data = section["data"]

        if section_type == "dataset_overview":
            return self._dataset_overview_to_html(title, data)
        elif section_type == "summary_statistics":
            return self._summary_stats_to_html(title, data)
        elif section_type == "missing_data_analysis":
            return self._missing_data_to_html(title, data)
        elif section_type == "categorical_analysis":
            return self._categorical_to_html(title, data)
        elif section_type == "insights":
            return self._insights_to_html(title, data)
        elif section_type == "recommendations":
            return self._recommendations_to_html(title, data)
        elif section_type == "data_quality":
            return self._data_quality_to_html(title, data)
        else:
            return f"<div class='section'><h2>{title}</h2><p>Bilinmeyen section tipi: {section_type}</p></div>"

    def _dataset_overview_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Dataset overview'ı HTML'e dönüştürür"""
        return f"""
        <div class='section overview'>
            <h2>{title}</h2>
            <div class='metrics-grid'>
                <div class='metric-card'>
                    <h3>Veri Boyutu</h3>
                    <p class='metric-value'>{data['shape']['rows']:,} × {data['shape']['columns']}</p>
                    <p class='metric-label'>satır × sütun</p>
                </div>
                <div class='metric-card'>
                    <h3>Bellek Kullanımı</h3>
                    <p class='metric-value'>{data['memory_usage_mb']}</p>
                    <p class='metric-label'>MB</p>
                </div>
                <div class='metric-card'>
                    <h3>Veri Kalitesi</h3>
                    <p class='metric-value'>{data['data_quality']['missing_percentage']:.1f}%</p>
                    <p class='metric-label'>eksik veri</p>
                </div>
                <div class='metric-card'>
                    <h3>Kopya Veriler</h3>
                    <p class='metric-value'>{data['data_quality']['duplicate_percentage']:.1f}%</p>
                    <p class='metric-label'>kopya satır</p>
                </div>
            </div>
        </div>
        """

    def _insights_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Insights'ları HTML'e dönüştürür"""
        insights_html = ""
        for insight in data["insights"]:
            insights_html += f"<li>{insight}</li>"

        return f"""
        <div class='section insights'>
            <h2>{title}</h2>
            <ul class='insights-list'>
                {insights_html}
            </ul>
        </div>
        """

    def _recommendations_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Recommendations'ları HTML'e dönüştürür"""
        recs_html = ""
        for rec in data["recommendations"]:
            recs_html += f"<li>{rec}</li>"

        return f"""
        <div class='section recommendations'>
            <h2>{title}</h2>
            <ul class='recommendations-list'>
                {recs_html}
            </ul>
        </div>
        """

    def _data_quality_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Data quality'yi HTML'e dönüştürür"""
        return f"""
        <div class='section data-quality'>
            <h2>{title}</h2>
            <div class='quality-score'>
                <div class='score-circle'>
                    <span class='score-value'>{data['overall_score']}</span>
                    <span class='score-label'>/100</span>
                </div>
                <p class='quality-level'>{data['quality_level']}</p>
            </div>
        </div>
        """

    def _summary_stats_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Summary statistics'i HTML'e dönüştürür"""
        return f"""
        <div class='section summary-stats'>
            <h2>{title}</h2>
            <p>İstatistiksel özet verileri burada gösterilecek.</p>
        </div>
        """

    def _missing_data_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Missing data analysis'i HTML'e dönüştürür"""
        return f"""
        <div class='section missing-data'>
            <h2>{title}</h2>
            <p>Eksik veri analizi burada gösterilecek.</p>
        </div>
        """

    def _categorical_to_html(self, title: str, data: Dict[str, Any]) -> str:
        """Categorical analysis'i HTML'e dönüştürür"""
        return f"""
        <div class='section categorical'>
            <h2>{title}</h2>
            <p>Kategorik değişken analizi burada gösterilecek.</p>
        </div>
        """

    def _get_html_template(self) -> str:
        """HTML template'ini döndürür"""
        return """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.8em;
            opacity: 0.8;
        }
        
        .insights-list, .recommendations-list {
            list-style: none;
        }
        
        .insights-list li, .recommendations-list li {
            padding: 10px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        
        .quality-score {
            text-align: center;
            padding: 20px;
        }
        
        .score-circle {
            display: inline-block;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-bottom: 10px;
        }
        
        .score-value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .score-label {
            font-size: 0.8em;
            opacity: 0.8;
        }
        
        .quality-level {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .section {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{TITLE}}</h1>
            <p>QuickInsights ile Oluşturuldu • {{TIMESTAMP}}</p>
        </div>
        
        {{SECTIONS}}
        
        <div class="footer">
            <p>Bu rapor QuickInsights kütüphanesi tarafından otomatik olarak oluşturulmuştur.</p>
        </div>
    </div>
</body>
</html>
        """


def create_dashboard(
    df: pd.DataFrame,
    title: str = "Veri Analizi Dashboard",
    output_html: str = "dashboard.html",
    output_json: str = "dashboard_data.json",
) -> Dict[str, str]:
    """
    Veri seti için otomatik dashboard oluşturur

    Parameters
    ----------
    df : pd.DataFrame
        Dashboard oluşturulacak veri seti
    title : str, default="Veri Analizi Dashboard"
        Dashboard başlığı
    output_html : str, default="dashboard.html"
        HTML çıktı dosyası
    output_json : str, default="dashboard_data.json"
        JSON çıktı dosyası

    Returns
    -------
    Dict[str, str]
        Oluşturulan dosya yolları

    Examples
    --------
    >>> import quickinsights as qi
    >>> files = qi.create_dashboard(df, title="Satış Analizi")
    >>> print(f"Dashboard: {files['html']}")
    """

    print("📊 Dashboard oluşturuluyor...")

    # Create dashboard generator
    dashboard = DashboardGenerator(title)

    # Add sections
    dashboard.add_dataset_overview(df)
    dashboard.add_summary_statistics(df)
    dashboard.add_missing_data_analysis(df)
    dashboard.add_categorical_analysis(df)

    # Quick insights for additional content
    try:
        from .quick_insights import quick_insight

        insight_result = quick_insight(df, include_viz=False)

        if "auto_insights" in insight_result:
            dashboard.add_insights_section(insight_result["auto_insights"])

        if "recommendations" in insight_result:
            dashboard.add_recommendations_section(insight_result["recommendations"])

        if "data_quality" in insight_result:
            quality_score = (
                100 - insight_result["data_quality"]["overall_score"]
            )  # Convert to positive score
            dashboard.add_data_quality_score(
                quality_score, insight_result["data_quality"]
            )

    except Exception as e:
        print(f"⚠️ Quick insights entegrasyonu başarısız: {e}")

    # Generate outputs
    html_path = dashboard.generate_html_dashboard(output_html)
    json_path = dashboard.generate_json_report(output_json)

    print("✅ Dashboard başarıyla oluşturuldu!")

    return {"html": html_path, "json": json_path, "title": title}
