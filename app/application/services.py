import logging
from typing import Any, Dict

from app.domain.ports import ModelPredictor, PredictionRepository

logger = logging.getLogger("eciwise.prediction")


class PredictionService:
    def __init__(self, predictor: ModelPredictor, repository: PredictionRepository) -> None:
        self._predictor = predictor
        self._repository = repository

    def predict_and_store(self, student_name: str, features: Dict[str, Any]) -> str:
        prediction = self._predictor.predict(features)
        logger.info("Prediction for %s: %s", student_name, prediction)
        self._repository.save(student_name, prediction)
        return prediction
