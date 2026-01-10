from ecjtu_wechat_api.api.routes.courses import router as courses_router
from ecjtu_wechat_api.api.routes.exams import router as exams_router
from ecjtu_wechat_api.api.routes.scores import router as scores_router

__all__ = ["courses_router", "scores_router", "exams_router"]
