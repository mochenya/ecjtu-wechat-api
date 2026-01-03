from fastapi.testclient import TestClient

from ecjtu_wechat_api.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_get_daily_courses_missing_params():
    response = client.get("/courses/daily")
    # FastAPI 对于缺失的必填查询参数返回 422 Unprocessable Entity
    assert response.status_code == 422


# 注意：测试实际的爬取功能 (/courses/daily) 理想情况下应该
# 模拟 ecjtu_wechat_api.services.parser.fetch_course_schedule 中的 requests.get
# 但对于基础的 API 结构测试，测试根路径已经足够。
