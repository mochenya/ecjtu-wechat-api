from fastapi import APIRouter, Query

from ecjtu_wechat_api.models.score import StudentScoreInfo
from ecjtu_wechat_api.services.parse_score import (
    fetch_score_info,
    parse_score_info,
)

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get(
    "/info",
    response_model=StudentScoreInfo,
    summary="获取成绩信息",
    description="根据微信 ID 和学期，从教务系统自动化抓取并解析成绩信息。",
)
async def get_score_info(
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
    具体的成绩获取逻辑：
    1. 调用解析服务，模拟移动端环境从教务系统抓取原始 HTML。
    2. 解析 HTML 并映射到 StudentScoreInfo 结构化模型。
    3. 返回 JSON 格式的解析结果。
    """
    # 获取原始 HTML
    html_content = await fetch_score_info(weiXinID, term)

    # 解析并构造 Pydantic 模型
    parsed_data = parse_score_info(html_content)

    return parsed_data
