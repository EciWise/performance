from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd

from app.adapters.ml.training import train_and_save


class EnsemblePredictor:
    def __init__(self, artifacts_dir: Path, dataset_path: Path, auto_train: bool) -> None:
        self._artifacts_dir = artifacts_dir
        self._dataset_path = dataset_path
        self._auto_train = auto_train
        self._ensure_artifacts()
        self._models = self._load_models()
        self._feature_columns, self._class_map = self._load_metadata()

    def predict(self, features: Dict[str, float | int]) -> str:
        frame = pd.DataFrame([features])
        frame = frame[self._feature_columns]
        probabilities: List[np.ndarray] = [
            model.predict_proba(frame) for model in self._models
        ]
        avg_proba = np.mean(probabilities, axis=0)
        class_index = int(np.argmax(avg_proba, axis=1)[0])
        return self._class_map[str(class_index)]

    def _ensure_artifacts(self) -> None:
        required = [
            self._artifacts_dir / "xgboost.joblib",
            self._artifacts_dir / "lightgbm.joblib",
            self._artifacts_dir / "catboost.joblib",
            self._artifacts_dir / "metadata.json",
        ]
        if all(path.exists() for path in required):
            return
        if not self._auto_train:
            missing = ", ".join(str(path) for path in required if not path.exists())
            raise FileNotFoundError(
                "Model artifacts missing. Run scripts/train.py first. Missing: "
                + missing
            )
        train_and_save(self._dataset_path, self._artifacts_dir)

    def _load_models(self):
        return [
            joblib.load(self._artifacts_dir / "xgboost.joblib"),
            joblib.load(self._artifacts_dir / "lightgbm.joblib"),
            joblib.load(self._artifacts_dir / "catboost.joblib"),
        ]

    def _load_metadata(self):
        payload = json.loads((self._artifacts_dir / "metadata.json").read_text())
        return payload["feature_columns"], payload["class_map"]
