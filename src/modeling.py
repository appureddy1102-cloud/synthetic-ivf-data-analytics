"""Exploratory, synthetic-only binary classification with patient-group split."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic_ivf_cleaned.csv"
OUT = ROOT / "outputs"
SEED = 20260618
NUMERIC_FEATURES = ["cycle_number", "patient_age", "infertility_duration_months", "bmi", "afc", "amh_ng_ml",
                    "stimulation_days", "estradiol_pg_ml", "progesterone_ng_ml", "total_oocytes", "mature_oocytes",
                    "fertilization_count", "embryos_formed", "day_of_embryo_transfer", "embryos_transferred",
                    "endometrial_thickness_mm", "treatment_cycle_cost_inr"]
CATEGORICAL_FEATURES = ["infertility_factor", "stimulation_protocol", "embryo_grade_category", "embryo_developmental_stage"]
TARGET = "clinical_pregnancy_outcome"


def build_preprocessor(scale_numeric):
    numeric_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    numeric = Pipeline(numeric_steps)
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([("numeric", numeric, NUMERIC_FEATURES),
                              ("categorical", categorical, CATEGORICAL_FEATURES)],
                             verbose_feature_names_out=False)


def run_models(cleaned_path=DATA):
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(cleaned_path)
    # Exclude non-transfer cycles and unknown primary target labels.
    model_df = df[df.embryos_transferred.gt(0) & df[TARGET].notna()].copy()
    X = model_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = model_df[TARGET].astype(int)
    groups = model_df["synthetic_patient_id"]
    splitter = GroupShuffleSplit(n_splits=1, test_size=.20, random_state=SEED)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train, groups_test = groups.iloc[train_idx], groups.iloc[test_idx]
    assert set(groups_train).isdisjoint(set(groups_test)), "Patient leakage detected in split"

    estimators = {
        "Dummy majority baseline": DummyClassifier(strategy="prior"),
        "Logistic regression": Pipeline([("prep", build_preprocessor(True)),
            ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED))]),
        "Random forest": Pipeline([("prep", build_preprocessor(False)),
            ("model", RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=12,
                class_weight="balanced_subsample", n_jobs=-1, random_state=SEED))])
    }
    records, predictions, probabilities = [], {}, {}
    for name, estimator in estimators.items():
        estimator.fit(X_train, y_train)
        pred = estimator.predict(X_test)
        prob = estimator.predict_proba(X_test)[:, 1] if hasattr(estimator, "predict_proba") else pred.astype(float)
        predictions[name] = pred
        probabilities[name] = prob
        records.append({"model": name, "accuracy": accuracy_score(y_test, pred),
                        "precision": precision_score(y_test, pred, zero_division=0),
                        "recall": recall_score(y_test, pred, zero_division=0),
                        "f1": f1_score(y_test, pred, zero_division=0),
                        "roc_auc": roc_auc_score(y_test, prob)})
    scores = pd.DataFrame(records).set_index("model")
    scores.to_csv(OUT / "model_metrics.csv")
    split_info = {"known_transfer_outcomes": int(len(model_df)), "train_cycles": int(len(train_idx)),
                  "test_cycles": int(len(test_idx)), "train_patients": int(groups_train.nunique()),
                  "test_patients": int(groups_test.nunique()), "patient_overlap": int(len(set(groups_train) & set(groups_test))),
                  "target_positive_rate_train": float(y_train.mean()), "target_positive_rate_test": float(y_test.mean()),
                  "target": TARGET, "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
                  "excluded": ["synthetic_patient_id", "synthetic_cycle_id", "cycle_date", "clinical_pregnancy_outcome",
                               "biochemical_pregnancy_outcome", "live_birth_outcome", "blastocyst_indicator (redundant with stage)"],
                  "synthetic_data_warning": "Metrics evaluate only this simulated data generator; not clinical validity."}
    with open(OUT / "model_split_and_feature_notes.json", "w") as f:
        json.dump(split_info, f, indent=2)

    # Confusion matrices for the two actual learned estimators.
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, name in zip(axes, ["Logistic regression", "Random forest"]):
        ConfusionMatrixDisplay(confusion_matrix(y_test, predictions[name]), display_labels=["No", "Yes"]).plot(ax=ax, colorbar=False)
        ax.set_title(name)
    fig.suptitle("Synthetic test-set confusion matrices (patient-group split)")
    fig.tight_layout()
    fig.savefig(ROOT / "visuals" / "model_confusion_matrices.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    for name in ["Logistic regression", "Random forest"]:
        fpr, tpr, _ = roc_curve(y_test, probabilities[name])
        ax.plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y_test, probabilities[name]):.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Chance")
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC curves — synthetic held-out patients")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(ROOT / "visuals" / "model_roc_curves.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    # Random-forest impurity importance is exploratory and can be biased with correlated features.
    rf = estimators["Random forest"]
    names = rf.named_steps["prep"].get_feature_names_out()
    importance = pd.Series(rf.named_steps["model"].feature_importances_, index=names).sort_values(ascending=False)
    importance.head(20).rename("importance").to_csv(OUT / "random_forest_feature_importance.csv")
    return scores, split_info, y_test, predictions, probabilities, importance

if __name__ == "__main__":
    scores, split, *_ = run_models()
    print("Patient overlap:", split["patient_overlap"])
    print(scores.round(3).to_string())
