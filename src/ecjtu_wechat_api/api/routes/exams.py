from fastapi import APIRouter, Query

from ecjtu_wechat_api.models.exam import ExamSchedule
from ecjtu_wechat_api.services.parse_exam import (
    fetch_exam_schedule,
    parse_exam_schedule,
)
from ecjtu_wechat_api.utils.cache import generate_cache_key, get_cached, set_cached

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get(
    "/schedule",
    response_model=ExamSchedule,
    summary="获取考试安排",
    description="根据微信 ID 和学期，从教务系统自动化抓取并解析考试安排信息。",
)
async def get_exam_schedule(
    weiXinID: str = Query(
        ...,
        description="教务系统绑定的微信用户ID，通过访问微信教务公众号获取。",
    ),
    term: str | None = Query(
        None,
        description=(
            "查询的学期，如 '2025.1'。如果不提供，系统将默认查询当前学期的数据。"
        ),
    ),
):
    """
    具体的考试安排获取逻辑：
    1. 尝试从缓存获取数据（1小时缓存）。
    2. 如缓存未命中，调用解析服务模拟移动端环境从教务系统抓取原始 HTML。
    3. 解析 HTML 并映射到 ExamSchedule 结构化模型。
    4. 将结果存入缓存并返回 JSON 格式的解析结果。
    """
    # 尝试从缓存获取（1小时缓存）
    cache_key = generate_cache_key(weiXinID, term=term or "", endpoint="exams_schedule")
    cached_data = get_cached(cache_key)
    if cached_data is not None:
        return cached_data

    # 获取原始 HTML
    html_content = await fetch_exam_schedule(weiXinID, term)

    # 解析并构造 Pydantic 模型
    parsed_data = parse_exam_schedule(html_content)

    # 存入缓存（1小时 = 3600秒）
    set_cached(cache_key, parsed_data, ttl=3600)

    return parsed_data
