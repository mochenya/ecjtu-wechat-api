__version__ = "1.0.0"
__author__ = "mochenyaa"
__copyright__ = "Copyright (c) 2026 mochenyaa"

from ecjtu_wechat_api.api import courses_router, scores_router
from ecjtu_wechat_api.services import (
    fetch_course_schedule,
    fetch_score_info,
    parse_course_schedule,
    parse_score_info,
)

__all__ = [
    "courses_router",
    "scores_router",
    "fetch_course_schedule",
    "parse_course_schedule",
    "fetch_score_info",
    "parse_score_info",
]
