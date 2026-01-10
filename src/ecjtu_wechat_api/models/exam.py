from pydantic import BaseModel, Field


class ExamTermItem(BaseModel):
    name: str = Field(..., description="学期名称，如 '2025.1'")
    url: str = Field(..., description="该学期的考试安排 URL")


class ExamItem(BaseModel):
    course_name: str = Field(..., description="课程名称")
    week: str = Field(..., description="考试周次")
    exam_date: str = Field(default="", description="考试日期，如 '2026年01月08日'")
    day_of_week: str = Field(default="", description="星期几，如 '星期四'")
    time_range: str = Field(default="", description="考试时间段，如 '14:00-16:00'")
    time_start: str = Field(default="", description="考试开始时间，如 '14:00'")
    time_end: str = Field(default="", description="考试结束时间，如 '16:00'")
    location: str = Field(..., description="考试地点")
    course_type: str = Field(..., description="课程性质")
    class_name: str = Field(..., description="班级名称")
    exam_count_num: int = Field(..., description="考试人数")
    note: str = Field(default="", description="考试备注（红色提示文字）")


class ExamSchedule(BaseModel):
    student_name: str = Field(..., description="学生姓名")
    current_term: str = Field(..., description="当前查询学期")
    available_terms: list[ExamTermItem] = Field(default_factory=list)
    exam_count: int = Field(..., description="考试总数")
    exams: list[ExamItem] = Field(default_factory=list)
