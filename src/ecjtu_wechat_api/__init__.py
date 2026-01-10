__version__ = "1.1.0"
__author__ = "mochenyaa"
__copyright__ = "Copyright (c) 2026 mochenyaa"

from ecjtu_wechat_api.api import courses_router, exams_router, scores_router
from ecjtu_wechat_api.services import (
    fetch_course_schedule,
    fetch_exam_schedule,
    fetch_score_info,
    parse_course_schedule,
    parse_exam_schedule,
    parse_score_info,
)

__all__ = [
    "courses_router",
    "scores_router",
    "exams_router",
    "fetch_course_schedule",
    "parse_course_schedule",
    "fetch_score_info",
    "parse_score_info",
    "fetch_exam_schedule",
    "parse_exam_schedule",
]
