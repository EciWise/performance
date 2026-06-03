from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    student_name: str = Field(..., min_length=1, max_length=120)
    gender: int = Field(..., ge=0, le=1)
    ethnicity: int = Field(..., ge=0, le=3)
    parental_education: int = Field(..., ge=0, le=4)
    study_time_weekly: float = Field(..., ge=0, le=20)
    absences: int = Field(..., ge=0, le=30)
    tutoring: int = Field(..., ge=0, le=1)
    parental_support: int = Field(..., ge=0, le=4)
    extracurricular: int = Field(..., ge=0, le=1)
    sports: int = Field(..., ge=0, le=1)
    music: int = Field(..., ge=0, le=1)
    volunteering: int = Field(..., ge=0, le=1)
    student_id: int | None = Field(
        default=None, description="Opcional, no afecta la predicción."
    )

    def to_features(self) -> dict:
        return {
            "Gender": self.gender,
            "Ethnicity": self.ethnicity,
            "ParentalEducation": self.parental_education,
            "StudyTimeWeekly": self.study_time_weekly,
            "Absences": self.absences,
            "Tutoring": self.tutoring,
            "ParentalSupport": self.parental_support,
            "Extracurricular": self.extracurricular,
            "Sports": self.sports,
            "Music": self.music,
            "Volunteering": self.volunteering,
        }


class PredictionResponse(BaseModel):
    student_name: str
    prediction: str
