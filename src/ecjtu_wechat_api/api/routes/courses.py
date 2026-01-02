from datetime import date as date_type

from fastapi import APIRouter, HTTPException, Query

from ecjtu_wechat_api.models.course import CourseSchedule
from ecjtu_wechat_api.services.parser import (
    fetch_course_schedule,
    parse_course_schedule,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "/daily",
    response_model=CourseSchedule,
    summary="获取每日课程表",
    description="根据微信 ID 和日期，从教务系统自动化抓取并解析当日的课程安排。",
)
async def get_course(
    weiXinID: str = Query(
        ...,
        description=("教务系统绑定的微信用户ID，通过访问微信教务公众号获取。"),
    ),
    date: str = Query(
        None,
        description=(
            "目标查询日期，格式为 YYYY-MM-DD（如：2026-01-05）。"
            "如果不提供，系统将默认查询今天的数据。"
        ),
    ),
):
    """
    具体的课程表获取逻辑：
    1. 校验并格式化日期（默认为当天）。
    2. 调用解析服务，模拟移动端环境从教务系统抓取原始 HTML。
    3. 解析 HTML 并映射到 CourseSchedule 结构化模型。
    4. 返回 JSON 格式的解析结果。
    """
    # 默认使用当天日期
    if not date:
        date = date_type.today().strftime("%Y-%m-%d")

    # 第一步：获取原始 HTML
    status_code, html_content = fetch_course_schedule(weiXinID, date)
    if status_code != 200 or not html_content:
        raise HTTPException(
            status_code=status_code if status_code != 200 else 500,
            detail=(
                f"网络请求失败：教务系统返回状态码 {status_code}，无法获取课程表源码。"
            ),
        )

    # 第二步：解析并构造 Pydantic 模型
    parsed_data = parse_course_schedule(html_content)
    if not parsed_data:
        raise HTTPException(
            status_code=500,
            detail="数据解析失败：无法从返回的 HTML 中提取有效的课程信息。",
        )

    return parsed_data
