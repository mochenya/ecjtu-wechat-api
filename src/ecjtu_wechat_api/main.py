from fastapi import FastAPI

from ecjtu_wechat_api.api.routes import courses_router, scores_router

app = FastAPI(
    title="华东交通大学教务系统微信版 API",
    description="提供华东交通大学教务系统的课程表查询与解析服务，支持获取每日课程安排及结构化数据。",
    version="1.0.0",
)

# 注册 API 路由
app.include_router(courses_router)
app.include_router(scores_router)


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
            "或者通过 /scores/info 路径获取成绩数据。"
        ),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ecjtu_wechat_api.main:app", host="0.0.0.0", port=6894, reload=True)
