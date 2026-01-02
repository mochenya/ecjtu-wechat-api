from pydantic import BaseModel


class TermItem(BaseModel):
    name: str  # e.g., "2025.1"
    url: str  # URL to fetch this term's scores


class ScoreItem(BaseModel):
    course_name: str
    course_code: str | None = None
    final_score: str
    reexam_score: str | None = None
    retake_score: str | None = None
    course_type: str  # e.g., "必修课"
    credit: float
    major: str | None = None  # e.g., "主修"


class StudentScoreInfo(BaseModel):
    student_name: str
    current_term: str
    available_terms: list[TermItem]
    score_count: int
    scores: list[ScoreItem]
