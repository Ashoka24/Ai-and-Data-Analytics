from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score, RocCurveDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "customer_churn.csv"
OUTPUT = ROOT / "outputs"
TARGET = "churn"
DROP_COLUMNS = ["customer_id", "total_charges"]


def load_data(path: Path = DATA) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"customer_id", "tenure_months", "monthly_charges", "total_charges", TARGET}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("The dataset is empty.")
    if df["customer_id"].isna().any() or df["customer_id"].duplicated().any():
        raise ValueError("customer_id must be present and unique.")
    if not set(df[TARGET].dropna().unique()).issubset({"Yes", "No"}):
        raise ValueError("churn must contain only Yes and No.")
    if df[TARGET].isna().any():
        raise ValueError("churn cannot contain missing values.")
    if (df["tenure_months"] < 0).any() or (df["monthly_charges"] < 0).any():
        raise ValueError("Tenure and monthly charges cannot be negative.")
    return df


def build_models(X: pd.DataFrame) -> dict[str, Pipeline]:
    numeric = X.select_dtypes(include=["number"]).columns.tolist()
    categorical = X.select_dtypes(exclude=["number"]).columns.tolist()
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ],
        remainder="drop",
    )
    return {
        "logistic_regression": Pipeline([
            ("preprocess", preprocess),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ]),
        "random_forest": Pipeline([
            ("preprocess", preprocess),
            ("model", RandomForestClassifier(
                n_estimators=300, min_samples_leaf=3,
                class_weight="balanced_subsample", random_state=42, n_jobs=-1,
            )),
        ]),
    }


def run_analysis(data_path: Path = DATA, output_dir: Path = OUTPUT) -> pd.DataFrame:
    df = load_data(data_path)
    y = df[TARGET].map({"No": 0, "Yes": 1})
    X = df.drop(columns=[TARGET, *DROP_COLUMNS], errors="ignore")
    numeric = X.select_dtypes(include=["number"]).columns.tolist()
    categorical = X.select_dtypes(exclude=["number"]).columns.tolist()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    models = build_models(X)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = []
    fig, ax = plt.subplots(figsize=(7, 6))
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]
        metrics.append({
            "model": name,
            "accuracy": accuracy_score(y_test, pred),
            "precision": precision_score(y_test, pred, zero_division=0),
            "recall": recall_score(y_test, pred, zero_division=0),
            "f1": f1_score(y_test, pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, probabilities),
            "test_rows": len(y_test),
        })
        report = classification_report(
            y_test, pred, labels=[0, 1], target_names=["No churn", "Churn"],
            output_dict=True, zero_division=0,
        )
        pd.DataFrame(report).T.to_csv(output_dir / f"classification_report_{name}.csv")
        cm = confusion_matrix(y_test, pred, labels=[0, 1])
        pd.DataFrame(cm, index=["actual_no_churn", "actual_churn"],
                     columns=["predicted_no_churn", "predicted_churn"]).to_csv(
                         output_dir / f"confusion_matrix_{name}.csv"
                     )
        prep = model.named_steps["preprocess"]
        names = prep.get_feature_names_out()
        estimator = model.named_steps["model"]
        if name == "logistic_regression":
            values = abs(estimator.coef_[0])
        else:
            values = estimator.feature_importances_
        pd.DataFrame({"feature": names, "importance": values}).sort_values(
            "importance", ascending=False
        ).to_csv(output_dir / f"feature_importance_{name}.csv", index=False)
        RocCurveDisplay.from_predictions(y_test, probabilities, name=name.replace("_", " ").title(), ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1)
    ax.set_title("Churn model ROC curves (held-out test set)")
    fig.tight_layout()
    fig.savefig(output_dir / "roc_curves.png", dpi=160)
    plt.close(fig)

    metrics_df = pd.DataFrame(metrics).sort_values("roc_auc", ascending=False)
    metrics_df.to_csv(output_dir / "model_metrics.csv", index=False, float_format="%.4f")
    churn_by_contract = df.groupby("contract", as_index=False).agg(
        customers=("customer_id", "nunique"),
        churned=("churn", lambda s: int((s == "Yes").sum())),
    )
    churn_by_contract["churn_rate"] = churn_by_contract["churned"] / churn_by_contract["customers"]
    churn_by_contract.to_csv(output_dir / "churn_by_contract.csv", index=False, float_format="%.4f")
    best = metrics_df.iloc[0]
    report = f"""# Model evaluation summary

This report is generated from the synthetic customer dataset and the current run.

- **Customers:** {len(df):,}
- **Observed churn rate:** {(y.mean()):.1%}
- **Training rows:** {len(y_train):,}
- **Held-out test rows:** {len(y_test):,}
- **Highest ROC-AUC in this run:** {best['model']} ({best['roc_auc']:.3f})
- **Precision / recall / F1 for that model:** {best['precision']:.3f} / {best['recall']:.3f} / {best['f1']:.3f}

The model was evaluated on a stratified hold-out set. These metrics are not a guarantee of performance on real customer data. Model feature rankings are associations learned by the estimator, not causal explanations.
"""
    (output_dir / "key_findings.md").write_text(report, encoding="utf-8")
    return metrics_df


if __name__ == "__main__":
    result = run_analysis()
    print(result.to_string(index=False))
    print(f"Outputs written to: {OUTPUT}")
