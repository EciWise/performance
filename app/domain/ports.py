from typing import Any, Dict, Protocol


class PredictionRepository(Protocol):
    def save(self, student_name: str, prediction: str) -> None:
        """Persist a prediction result."""


class ModelPredictor(Protocol):
    def predict(self, features: Dict[str, Any]) -> str:
        """Predict the grade class from the input features."""
