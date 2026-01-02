from pydantic import BaseModel, Field


class DateInfo(BaseModel):
    """
    课程表对应的日期元数据模型。
    """

    date: str | None = Field(None, description="查询的目标日期，格式为 YYYY-MM-DD")
    day_of_week: str | None = Field(
        None, description="该日期对应的星期几（如：星期一）"
    )
    week_info: str | None = Field(None, description="教学周次（如：第17周）")


class Course(BaseModel):
    """
    单门课程的结构化信息。
    """

    name: str = Field(..., description="课程名称（如：高等数学）")
    status: str = Field(..., description="课程状态或类型（如：上课、调课）")
    time: str = Field(..., description="原始的时间描述字符串（如：1-17周 1,2节）")
    location: str = Field(..., description="教学地点/教室（如：10栋201）")
    teacher: str = Field(..., description="授课教师姓名")
    weeks: list[list[int]] = Field(
        ...,
        description=(
            "解析后的周次范围列表，子列表包含起始和结束周 [start, end] 或单周 [week]"
        ),
    )
    periods: list[int] = Field(..., description="解析后的具体节次列表（如：[1, 2]）")


class CourseSchedule(BaseModel):
    """
    完整的课程表响应模型，包含日期信息和课程列表。
    """

    date_info: DateInfo | None = Field(None, description="日期相关的辅助信息")
    courses: list[Course] = Field(
        default_factory=list, description="当日的所有课程列表"
    )
