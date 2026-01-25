from datetime import date as date_type

from fastapi import APIRouter, Query

from ecjtu_wechat_api.models.course import CourseSchedule
from ecjtu_wechat_api.services.parse_course import (
    fetch_course_schedule,
    parse_course_schedule,
)
from ecjtu_wechat_api.utils.cache import generate_cache_key, get_cached, set_cached

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
    2. 尝试从缓存获取数据（30分钟缓存）。
    3. 如缓存未命中，调用解析服务模拟移动端环境从教务系统抓取原始 HTML。
    4. 解析 HTML 并映射到 CourseSchedule 结构化模型。
    5. 将结果存入缓存并返回 JSON 格式的解析结果。
    """
    # 默认使用当天日期
    if not date:
        date = date_type.today().strftime("%Y-%m-%d")

    # 尝试从缓存获取（30分钟缓存）
    cache_key = generate_cache_key(weiXinID, date=date, endpoint="courses_daily")
    cached_data = get_cached(cache_key)
    if cached_data is not None:
        return cached_data

    # 获取原始 HTML
    html_content = await fetch_course_schedule(weiXinID, date)

    # 解析并构造 Pydantic 模型
    parsed_data = parse_course_schedule(html_content)

    # 存入缓存（30分钟 = 1800秒）
    set_cached(cache_key, parsed_data, ttl=1800)

    return parsed_data
