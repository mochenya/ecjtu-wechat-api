from fastapi import APIRouter, Query

from ecjtu_wechat_api.models.score import StudentScoreInfo
from ecjtu_wechat_api.services.parse_score import (
    fetch_available_terms_with_scores,
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


@router.get(
    "/terms/valid",
    response_model=list[str],
    summary="获取有效学期列表",
    description=(
        "获取真正包含成绩数据的学期名称列表。"
        "系统会检查每个学期是否包含成绩数据，并过滤掉无成绩的学期。"
    ),
)
async def get_valid_terms(
    weiXinID: str = Query(
        ...,
        description="教务系统绑定的微信用户ID，通过访问微信教务公众号获取。",
    ),
) -> list[str]:
    """
    具体的学期获取逻辑：
    1. 先不带 term 获取当前学期 HTML，解析出可用学期列表
    2. 依次遍历每个学期，获取成绩数据
    3. 过滤掉无成绩的学期
    4. 返回包含成绩的学期名称列表
    """
    return await fetch_available_terms_with_scores(weiXinID)
