from sqlalchemy import Column, DateTime, Integer, String, func

from app.infrastructure.database import Base


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(120), nullable=False)
    prediction = Column(String(8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
