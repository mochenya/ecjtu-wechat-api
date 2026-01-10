from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ecjtu_wechat_api import courses_router, exams_router, scores_router, __version__
from ecjtu_wechat_api.core.exceptions import ECJTUAPIError
from ecjtu_wechat_api.utils.logger import logger

app = FastAPI(
    title="华东交通大学教务系统微信版 API",
    description="提供华东交通大学教务系统的课程表查询、成绩获取与考试安排服务，支持结构化数据。",
    version=__version__,
)


@app.exception_handler(ECJTUAPIError)
async def api_error_handler(request: Request, exc: ECJTUAPIError):
    """
    统一处理项目自定义业务异常
    """
    status_code = getattr(exc, "status_code", 400)
    logger.error(f"业务异常: {exc.message}, 详情: {exc.details}")
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    处理未捕获的系统异常
    """
    logger.exception(f"未捕获的系统异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误，请稍后再试",
            "details": str(exc) if not isinstance(exc, RuntimeError) else None,
        },
    )


# 注册 API 路由
app.include_router(courses_router)
app.include_router(scores_router)
app.include_router(exams_router)


@app.get(
    "/", summary="根路径检查", description="显示 API 的基本状态信息及使用方法指导。"
)
async def root():
    """
    返回 API 的欢迎信息及简要的使用说明。
    """
    return {
        "status": "online",
        "message": (
            "欢迎使用华东交通大学教务系统微信版 API。服务目前运行正常。"
            "您可以通过 /courses/daily 路径获取课程表，"
            "通过 /scores/info 路径获取成绩数据，"
            "通过 /exams/schedule 路径获取考试安排。"
        ),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ecjtu_wechat_api.main:app", host="0.0.0.0", port=6894, reload=True)
