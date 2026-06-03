from sqlalchemy.orm import Session

from app.adapters.db.models import PredictionRecord
from app.domain.ports import PredictionRepository


class SqlAlchemyPredictionRepository(PredictionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, student_name: str, prediction: str) -> None:
        record = PredictionRecord(student_name=student_name, prediction=prediction)
        self._session.add(record)
        self._session.commit()


class NoOpPredictionRepository(PredictionRepository):
    def save(self, student_name: str, prediction: str) -> None:
        return None
