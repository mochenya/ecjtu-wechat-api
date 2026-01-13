from pydantic import BaseModel, Field


class TermItem(BaseModel):
    """学期条目模型，包含学期名称和查询 URL。"""

    name: str = Field(..., description="学期名称，如 '2025.1'")
    url: str = Field(..., description="该学期成绩查询的教务微信官网 URL")


class ScoreItem(BaseModel):
    """单门课程成绩的结构化信息。"""

    course_name: str = Field(..., description="课程名称")
    course_code: str = Field(..., description="课程代码")
    final_score: str = Field(..., description="期末成绩")
    reexam_score: str | None = Field(None, description="重考成绩")
    retake_score: str | None = Field(None, description="重修成绩")
    course_type: str = Field(..., description="课程性质，如 '必修课'")
    credit: float = Field(..., description="学分")
    major: str = Field(..., description="专业标识，如 '主修'")


class StudentScoreInfo(BaseModel):
    """学生成绩信息完整响应模型，包含学生信息和成绩列表。"""

    student_name: str = Field(..., description="学生姓名")
    current_term: str = Field(..., description="当前查询学期")
    available_terms: list[TermItem] = Field(..., description="可查询的学期列表")
    score_count: int = Field(..., description="成绩总数")
    scores: list[ScoreItem] = Field(..., description="成绩列表")
