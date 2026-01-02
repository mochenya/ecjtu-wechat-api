from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from ecjtu_wechat_api.main import app

client = TestClient(app)


@patch("ecjtu_wechat_api.api.routes.scores.fetch_score_info")
@patch("ecjtu_wechat_api.api.routes.scores.parse_score_info")
def test_get_score_info_success(mock_parse, mock_fetch):
    # Mocking successful fetch and parse
    mock_fetch.return_value = (200, "<html>Mocked HTML</html>")
    mock_parse.return_value = {
        "student_name": "张三",
        "current_term": "2025.1",
        "available_terms": [{"name": "2025.1", "url": "test_url"}],
        "score_count": 1,
        "scores": [
            {
                "course_name": "高等数学",
                "course_code": "123",
                "final_score": "90",
                "reexam_score": None,
                "retake_score": None,
                "course_type": "必修课",
                "credit": 5.0,
                "major": "主修",
            }
        ],
    }

    response = client.get("/scores/info?weiXinID=test_id")

    assert response.status_code == 200
    data = response.json()
    assert data["student_name"] == "张三"
    assert data["scores"][0]["course_name"] == "高等数学"


@patch("ecjtu_wechat_api.api.routes.scores.fetch_score_info")
def test_get_score_info_network_error(mock_fetch):
    # Mocking network error
    mock_fetch.return_value = (500, None)

    response = client.get("/scores/info?weiXinID=test_id")

    assert response.status_code == 500
    assert "网络请求失败" in response.json()["detail"]


@patch("ecjtu_wechat_api.api.routes.scores.fetch_score_info")
@patch("ecjtu_wechat_api.api.routes.scores.parse_score_info")
def test_get_score_info_parse_error(mock_parse, mock_fetch):
    # Mocking successful fetch but failed parse
    mock_fetch.return_value = (200, "<html>Invalid HTML</html>")
    mock_parse.return_value = None

    response = client.get("/scores/info?weiXinID=test_id")

    assert response.status_code == 500
    assert "数据解析失败" in response.json()["detail"]
