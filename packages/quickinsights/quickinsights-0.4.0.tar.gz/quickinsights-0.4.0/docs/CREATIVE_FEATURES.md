# QuickInsights – Creative Features

This page documents the new, unique capabilities added to QuickInsights that go beyond standard libraries.

- infer_constraints: Schema-by-example constraint inference
- drift_radar: Baseline vs current drift diagnostics (numeric/categorical)
- contrastive_explanations: Minimal directional changes for opposite-class predictions

## 1) infer_constraints(df, max_categories=25, detect_patterns=True)
Infers column-level constraints directly from data.

Returns, per column:
- dtype, nullable, unique, cardinality
- numeric stats: min, max, mean, std, monotonic flags
- categorical domain: top categories and counts
- pattern hints: email, phone, date (heuristic)

Also returns a compact contract dict useful for data contracts and validators.

Example:
```python
a from quickinsights.data_validation import infer_constraints
profile = infer_constraints(df)
print(profile["contract"])  # {column: {dtype, nullable, unique, min, max, domain}}
```

Typical uses:
- Generate Great Expectations or Pydantic models from real data (see roadmap)
- Validate incoming datasets against inferred constraints
- Document datasets automatically (JSON-friendly)

## 2) drift_radar(base_df, current_df, bins=10, top_k_categories=20)
Detects schema and distribution drift between a baseline dataset and a current dataset.

- Numeric drift: PSI (Population Stability Index), optional KS-test p-values (if SciPy is available)
- Categorical drift: PSI over top-K categories, unseen/vanished category tracking
- Overall risk: low | medium | high (based on max PSI)

Example:
```python
from quickinsights.data_validation import drift_radar
base = df.sample(frac=0.5, random_state=42)
current = df.drop(base.index)
radar = drift_radar(base, current)
print(radar["overall_risk"])  # e.g., "medium"
```

Typical uses:
- Monitor data pipelines for silent schema/behavior changes
- Attach to CI/CD checks or scheduled jobs; persist JSON reports

## 3) contrastive_explanations(model, X, y, index=0, k_neighbors=5, feature_names=None)
Produces a contrastive explanation for a single instance using nearest neighbors from the opposite class, suggesting minimal directional changes to flip the prediction.

Notes:
- Best for binary classification. Falls back gracefully if classes < 2 or `predict` is unavailable
- Returns a compact list of suggested deltas (feature, delta, direction)

Example:
```python
from quickinsights import contrastive_explanations
from sklearn.linear_model import LogisticRegression

X = df.select_dtypes(float).fillna(0).to_numpy()
y = (X[:, 0] > X[:, 0].mean()).astype(int)
model = LogisticRegression().fit(X, y)

cx = contrastive_explanations(model, X, y, index=0)
print(cx["suggestions"][:3])
```

Typical uses:
- Human-readable "what to change" guidance
- Augment model audit reports with actionable explanations

## Outputs and JSON
All three features are designed to be JSON-friendly so they can be logged or stored in artefact stores easily.

## Roadmap (next)
- Data Contract Builder: Export `infer_constraints` to Great Expectations suites and Pydantic models
- Drift Radar v2: Segment-based drift (e.g., by region), additional divergences (JSD), thresholds & alerts
- Contrastive v2: Action recipes per top features; integration with anomaly explanations
