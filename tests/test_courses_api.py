"""
课程表 API 测试模块
"""

from datetime import date as date_type
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from ecjtu_wechat_api.core.exceptions import EducationSystemError, ParseError
from ecjtu_wechat_api.main import app

client = TestClient(app)


# 正常场景测试
@patch(
    "ecjtu_wechat_api.api.routes.courses.fetch_course_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.courses.parse_course_schedule")
def test_get_daily_courses_with_date(mock_parse, mock_fetch):
    """测试提供明确日期参数获取课程表"""
    # Mock 成功的抓取和解析
    mock_fetch.return_value = "<html>Mocked HTML</html>"
    mock_parse.return_value = {
        "date_info": {"date": "2026-01-06", "day_of_week": "星期二", "week_info": "19"},
        "courses": [
            {
                "name": "大学英语",
                "status": "上课",
                "time": "1-19周 1,2节",
                "periods": [1, 2],
                "weeks": [[1, 19]],
                "location": "教1-101",
                "teacher": "张三",
            }
        ],
    }

    response = client.get("/courses/daily?weiXinID=test_id&date=2026-01-06")

    assert response.status_code == 200
    data = response.json()
    assert data["date_info"]["date"] == "2026-01-06"
    assert len(data["courses"]) == 1
    assert data["courses"][0]["name"] == "大学英语"


@patch(
    "ecjtu_wechat_api.api.routes.courses.fetch_course_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.courses.parse_course_schedule")
@patch("ecjtu_wechat_api.api.routes.courses.date_type")
def test_get_daily_courses_without_date(mock_date, mock_parse, mock_fetch):
    """测试不提供日期参数，默认使用今天日期"""
    # Mock 今天的日期
    mock_date.today.return_value = date_type(2026, 1, 6)
    mock_date.return_value.strftime.return_value = "2026-01-06"

    mock_fetch.return_value = "<html>Mocked HTML</html>"
    mock_parse.return_value = {
        "date_info": {"date": "2026-01-06", "day_of_week": "星期二", "week_info": "19"},
        "courses": [
            {
                "name": "大学英语",
                "status": "上课",
                "time": "1-19周 1,2节",
                "periods": [1, 2],
                "weeks": [[1, 19]],
                "location": "教1-101",
                "teacher": "张三",
            }
        ],
    }

    response = client.get("/courses/daily?weiXinID=test_id")

    assert response.status_code == 200
    mock_date.today.assert_called_once()


# 异常场景测试
@patch(
    "ecjtu_wechat_api.api.routes.courses.fetch_course_schedule",
    new_callable=AsyncMock,
)
def test_get_daily_courses_network_error(mock_fetch):
    """测试网络错误"""
    # Mock 网络错误
    mock_fetch.side_effect = EducationSystemError("网络请求失败", status_code=500)

    response = client.get("/courses/daily?weiXinID=test_id&date=2026-01-06")

    assert response.status_code == 500
    assert "网络请求失败" in response.json()["message"]


@patch(
    "ecjtu_wechat_api.api.routes.courses.fetch_course_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.courses.parse_course_schedule")
def test_get_daily_courses_parse_error(mock_parse, mock_fetch):
    """测试解析错误"""
    # Mock 抓取成功但解析失败
    mock_fetch.return_value = "<html>Invalid HTML</html>"
    mock_parse.side_effect = ParseError("数据解析失败")

    response = client.get("/courses/daily?weiXinID=test_id&date=2026-01-06")

    assert response.status_code == 400
    assert "数据解析失败" in response.json()["message"]


# 参数验证测试
def test_get_daily_courses_missing_weixinid():
    """测试缺少 weiXinID 参数"""
    response = client.get("/courses/daily?date=2026-01-06")

    assert response.status_code == 422
