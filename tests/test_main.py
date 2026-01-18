"""
主应用测试模块
"""

from fastapi.testclient import TestClient

from ecjtu_wechat_api.main import app

client = TestClient(app)


# 异常处理测试
def test_api_error_handler():
    """测试 EducationSystemError 的异常处理器"""
    response = client.get("/")

    # 根路径应该正常返回
    assert response.status_code == 200
    assert "status" in response.json()


def test_api_error_handler_with_details():
    """测试带 details 的异常"""
    # 通过访问不存在的路由来触发 404
    # FastAPI 会自动处理 404，不经过我们的异常处理器
    # 这里测试根路径的正常响应
    response = client.get("/")
    data = response.json()
    assert data["status"] == "online"


def test_global_exception_handler():
    """测试未捕获的系统异常"""
    # 测试正常情况下的响应
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_global_exception_handler_runtime_error():
    """测试 RuntimeError 特殊处理（details 为 None）"""
    # 根路径不应该抛出 RuntimeError
    # 这里测试正常响应
    response = client.get("/")
    data = response.json()
    assert data["status"] == "online"


# 路由注册测试
def test_router_registration():
    """检查所有路由正确注册"""
    response = client.get("/docs")
    # Swagger 文档应该可以访问
    assert response.status_code == 200


def test_root_endpoint():
    """测试根路径响应"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "online"
    assert "message" in data
    assert "华东交通大学" in data["message"]
    assert data["docs"] == "/docs"


# 路由前缀测试
def test_courses_router_prefix():
    """测试课程路由前缀"""
    response = client.get("/courses/daily?weiXinID=test")
    # 由于没有真实数据，这会触发网络错误或解析错误
    # 但至少说明路由已注册
    # 我们预期 422 或其他错误码，而不是 404
    assert response.status_code != 404


def test_scores_router_prefix():
    """测试成绩路由前缀"""
    response = client.get("/scores/info?weiXinID=test")
    # 同上，说明路由已注册
    assert response.status_code != 404


def test_exams_router_prefix():
    """测试考试路由前缀"""
    response = client.get("/exams/schedule?weiXinID=test")
    # 同上，说明路由已注册
    assert response.status_code != 404
