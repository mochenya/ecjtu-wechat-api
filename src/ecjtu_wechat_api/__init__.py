import tomllib
from pathlib import Path

_pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
with _pyproject.open("rb") as f:
    __version__ = tomllib.load(f)["project"]["version"]

__author__ = "mochenyaa"
__copyright__ = "Copyright (c) 2026 mochenyaa"

from ecjtu_wechat_api.api import (  # noqa: E402
    courses_router,
    exams_router,
    scores_router,
)
from ecjtu_wechat_api.services import (  # noqa: E402
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
