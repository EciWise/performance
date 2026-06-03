from dataclasses import dataclass


@dataclass(frozen=True)
class StudentFeatures:
    age: int
    gender: int
    ethnicity: int
    parental_education: int
    study_time_weekly: float
    absences: int
    tutoring: int
    parental_support: int
    extracurricular: int
    sports: int
    music: int
    volunteering: int
    gpa: float
