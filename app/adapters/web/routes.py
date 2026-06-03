from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.adapters.db.repository import (
    NoOpPredictionRepository,
    SqlAlchemyPredictionRepository,
)
from app.adapters.ml.ensemble import EnsemblePredictor
from app.application.services import PredictionService
from app.infrastructure.config import Settings
from app.infrastructure.database import get_session
from app.infrastructure.security import require_auth

from .schemas import PredictionRequest, PredictionResponse

router = APIRouter()
settings = Settings()
_predictor: EnsemblePredictor | None = None


def get_predictor() -> EnsemblePredictor:
    global _predictor
    if _predictor is None:
        _predictor = EnsemblePredictor(
            artifacts_dir=settings.artifacts_dir,
            dataset_path=settings.dataset_path,
            auto_train=settings.auto_train,
        )
    return _predictor


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/predictions", response_model=PredictionResponse)
def create_prediction(
    payload: PredictionRequest,
    session: Session | None = Depends(get_session),
    _claims: dict[str, Any] = Depends(require_auth),
) -> PredictionResponse:
    predictor = get_predictor()
    if settings.db_enabled and session is not None:
        repository = SqlAlchemyPredictionRepository(session)
    else:
        repository = NoOpPredictionRepository()
    service = PredictionService(predictor, repository)
    prediction = service.predict_and_store(payload.student_name, payload.to_features())
    return PredictionResponse(student_name=payload.student_name, prediction=prediction)
