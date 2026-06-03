from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

FEATURE_COLUMNS: List[str] = [
    "Gender",
    "Ethnicity",
    "ParentalEducation",
    "StudyTimeWeekly",
    "Absences",
    "Tutoring",
    "ParentalSupport",
    "Extracurricular",
    "Sports",
    "Music",
    "Volunteering",
]

CLASS_MAP = {
    0: "A",
    1: "B",
    2: "C",
    3: "D",
    4: "F",
}


def train_and_save(dataset_path: Path, artifacts_dir: Path) -> Dict[str, Dict]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(dataset_path)
    X = data[FEATURE_COLUMNS]
    y = data["GradeClass"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    smote = SMOTE(random_state=42, k_neighbors=3)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

    class_weights = compute_class_weight("balanced", classes=np.unique(y_train_smote), y=y_train_smote)
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}

    models = {
        "xgboost": XGBClassifier(
            n_estimators=500,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            colsample_bylevel=0.85,
            objective="multi:softprob",
            num_class=5,
            eval_metric="mlogloss",
            scale_pos_weight=1,
            random_state=42,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=500,
            num_leaves=25,
            learning_rate=0.05,
            objective="multiclass",
            num_class=5,
            class_weight="balanced",
            verbose=-1,
            random_state=42,
        ),
        "catboost": CatBoostClassifier(
            iterations=500,
            depth=7,
            learning_rate=0.05,
            loss_function="MultiClass",
            verbose=False,
            class_weights=class_weight_dict,
            random_state=42,
        ),
    }

    metrics: Dict[str, Dict] = {}
    feature_importance_all = {}

    for name, model in models.items():
        model.fit(X_train_smote, y_train_smote)
        preds = np.asarray(model.predict(X_val)).ravel().astype(int)
        probabilities = model.predict_proba(X_val)

        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_val, preds, average="macro", zero_division=0
        )
        precision_weighted, recall_weighted, f1_weighted, _ = (
            precision_recall_fscore_support(
                y_val, preds, average="weighted", zero_division=0
            )
        )
        precision_micro, recall_micro, f1_micro, _ = precision_recall_fscore_support(
            y_val, preds, average="micro", zero_division=0
        )

        feature_importance = None
        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
            feature_importance = {
                FEATURE_COLUMNS[i]: float(importance[i])
                for i in range(len(FEATURE_COLUMNS))
            }
            feature_importance_all[name] = feature_importance

        metrics[name] = {
            "accuracy": float(accuracy_score(y_val, preds)),
            "balanced_accuracy": float(balanced_accuracy_score(y_val, preds)),
            "precision_macro": float(precision_macro),
            "recall_macro": float(recall_macro),
            "f1_macro": float(f1_macro),
            "precision_weighted": float(precision_weighted),
            "recall_weighted": float(recall_weighted),
            "f1_weighted": float(f1_weighted),
            "precision_micro": float(precision_micro),
            "recall_micro": float(recall_micro),
            "f1_micro": float(f1_micro),
            "log_loss": float(log_loss(y_val, probabilities)),
            "confusion_matrix": confusion_matrix(y_val, preds).tolist(),
            "classification_report": classification_report(
                y_val, preds, output_dict=True, zero_division=0
            ),
            "feature_importance": feature_importance,
        }
        joblib.dump(model, artifacts_dir / f"{name}.joblib")

    metadata = {
        "feature_columns": FEATURE_COLUMNS,
        "class_map": {str(k): v for k, v in CLASS_MAP.items()},
        "metrics": metrics,
        "improvements": {
            "smote": "Applied SMOTE for class balancing on training set",
            "class_weights": "Used balanced class weights for all models",
            "leakage_test": "GPA removed to test for data leakage (GPA is not available at prediction time)",
            "hyperparameters": {
                "xgboost": "n_estimators=500, max_depth=7, learning_rate=0.05",
                "lightgbm": "n_estimators=500, num_leaves=25, learning_rate=0.05",
                "catboost": "iterations=500, depth=7, learning_rate=0.05",
            },
        },
    }
    (artifacts_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return metrics
