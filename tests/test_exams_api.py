"""
考试安排 API 测试模块
"""

import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from ecjtu_wechat_api.core.exceptions import EducationSystemError, ParseError
from ecjtu_wechat_api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    """每个测试前后清空缓存"""
    from ecjtu_wechat_api.utils.cache import clear_cache

    clear_cache()
    yield
    clear_cache()


# 正常场景测试
@patch(
    "ecjtu_wechat_api.api.routes.exams.fetch_exam_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.exams.parse_exam_schedule")
def test_get_exam_schedule_with_term(mock_parse, mock_fetch):
    """测试提供学期参数获取考试安排"""
    # Mock 成功的抓取和解析
    mock_fetch.return_value = "<html>Mocked HTML</html>"
    mock_parse.return_value = {
        "student_name": "张三",
        "current_term": "2025.1",
        "available_terms": [{"name": "2025.1", "url": "test_url"}],
        "exam_count": 1,
        "exams": [
            {
                "course_name": "C语言程序设计",
                "week": "第18周",
                "exam_date": "2026年01月08日",
                "day_of_week": "星期四",
                "time_range": "14:00-16:00",
                "time_start": "14:00",
                "time_end": "16:00",
                "location": "教1-101",
                "course_type": "必修课",
                "class_name": "计算机241班",
                "exam_count_num": 45,
                "note": None,
            }
        ],
    }

    response = client.get("/exams/schedule?weiXinID=test_id&term=2025.1")

    assert response.status_code == 200
    data = response.json()
    assert data["student_name"] == "张三"
    assert data["current_term"] == "2025.1"
    assert len(data["exams"]) == 1
    assert data["exams"][0]["course_name"] == "C语言程序设计"


@patch(
    "ecjtu_wechat_api.api.routes.exams.fetch_exam_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.exams.parse_exam_schedule")
def test_get_exam_schedule_without_term(mock_parse, mock_fetch):
    """测试不提供学期参数，获取当前学期考试安排"""
    mock_fetch.return_value = "<html>Mocked HTML</html>"
    mock_parse.return_value = {
        "student_name": "李四",
        "current_term": "2025.1",
        "available_terms": [
            {"name": "2025.1", "url": "test_url1"},
            {"name": "2024.2", "url": "test_url2"},
        ],
        "exam_count": 2,
        "exams": [
            {
                "course_name": "高等数学",
                "week": "第19周",
                "exam_date": "2026年01月10日",
                "day_of_week": "星期六",
                "time_range": "09:00-11:00",
                "time_start": "09:00",
                "time_end": "11:00",
                "location": "教2-201",
                "course_type": "必修课",
                "class_name": "计算机241班",
                "exam_count_num": 45,
                "note": None,
            },
            {
                "course_name": "大学英语",
                "week": "第19周",
                "exam_date": "2026年01月12日",
                "day_of_week": "星期一",
                "time_range": "14:00-16:00",
                "time_start": "14:00",
                "time_end": "16:00",
                "location": "教3-301",
                "course_type": "必修课",
                "class_name": "计算机241班",
                "exam_count_num": 45,
                "note": "请携带学生证",
            },
        ],
    }

    response = client.get("/exams/schedule?weiXinID=test_id")

    assert response.status_code == 200
    data = response.json()
    assert data["student_name"] == "李四"
    assert len(data["exams"]) == 2
    assert data["exams"][1]["note"] == "请携带学生证"


# 异常场景测试
@patch(
    "ecjtu_wechat_api.api.routes.exams.fetch_exam_schedule",
    new_callable=AsyncMock,
)
def test_get_exam_schedule_network_error(mock_fetch):
    """测试网络错误"""
    # Mock 网络错误
    mock_fetch.side_effect = EducationSystemError("网络请求失败", status_code=500)

    response = client.get("/exams/schedule?weiXinID=test_id&term=2025.1")

    assert response.status_code == 500
    assert "网络请求失败" in response.json()["message"]


@patch(
    "ecjtu_wechat_api.api.routes.exams.fetch_exam_schedule",
    new_callable=AsyncMock,
)
@patch("ecjtu_wechat_api.api.routes.exams.parse_exam_schedule")
def test_get_exam_schedule_parse_error(mock_parse, mock_fetch):
    """测试解析错误"""
    # Mock 抓取成功但解析失败
    mock_fetch.return_value = "<html>Invalid HTML</html>"
    mock_parse.side_effect = ParseError("数据解析失败")

    response = client.get("/exams/schedule?weiXinID=test_id&term=2025.1")

    assert response.status_code == 400
    assert "数据解析失败" in response.json()["message"]


# 参数验证测试
def test_get_exam_schedule_missing_weixinid():
    """测试缺少 weiXinID 参数"""
    response = client.get("/exams/schedule?term=2025.1")

    assert response.status_code == 422
