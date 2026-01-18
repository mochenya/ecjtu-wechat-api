"""
配置加载测试模块
"""

from pathlib import Path

from ecjtu_wechat_api.core.config import settings


def test_config_api_base_url_default():
    """测试默认 API_BASE_URL"""
    assert settings.API_BASE_URL == "http://localhost:6894"


def test_config_project_root_path():
    """测试项目根目录路径"""
    assert isinstance(settings.PROJECT_ROOT, Path)
    assert settings.PROJECT_ROOT.exists()


def test_config_data_dir_path():
    """测试数据目录路径"""
    assert isinstance(settings.DATA_DIR, Path)
    # DATA_DIR 应该是 PROJECT_ROOT 下的 data 目录
    assert settings.DATA_DIR == settings.PROJECT_ROOT / "data"


def test_config_wechat_user_agent():
    """测试微信 User-Agent"""
    assert hasattr(settings, "WECHAT_USER_AGENT")
    assert "MicroMessenger" in settings.WECHAT_USER_AGENT
    assert "Android" in settings.WECHAT_USER_AGENT


def test_config_default_headers():
    """测试默认请求头"""
    assert isinstance(settings.DEFAULT_HEADERS, dict)
    assert "User-Agent" in settings.DEFAULT_HEADERS
    assert "Accept" in settings.DEFAULT_HEADERS
    assert "Accept-Language" in settings.DEFAULT_HEADERS


def test_config_base_url():
    """测试教务系统基础 URL"""
    assert settings.BASE_URL == "https://jwxt.ecjtu.edu.cn/weixin"


def test_config_score_url():
    """测试成绩查询 URL"""
    assert f"{settings.BASE_URL}/ScoreQuery" == settings.SCORE_URL


def test_config_course_url():
    """测试课程表 URL"""
    assert f"{settings.BASE_URL}/CalendarServlet" == settings.COURSE_URL


def test_config_exam_url():
    """测试考试安排 URL"""
    assert f"{settings.BASE_URL}/ExamArrangeCl" == settings.EXAM_URL


def test_config_weixin_id_from_env(monkeypatch):
    """测试从环境变量读取 WEIXIN_ID"""
    # 设置环境变量
    monkeypatch.setenv("WEIXIN_ID", "test_weixin_id_123")

    # 需要重新加载配置模块
    import importlib

    import ecjtu_wechat_api.core.config

    importlib.reload(ecjtu_wechat_api.core.config)

    from ecjtu_wechat_api.core.config import settings as reloaded_settings

    assert reloaded_settings.WEIXIN_ID == "test_weixin_id_123"


def test_config_weixin_id_type():
    """测试 WEIXIN_ID 类型"""
    # WEIXIN_ID 可以是字符串或 None
    assert settings.WEIXIN_ID is None or isinstance(settings.WEIXIN_ID, str)


def test_config_api_base_url_custom(monkeypatch):
    """测试自定义 API_BASE_URL"""
    monkeypatch.setenv("API_BASE_URL", "http://custom.example.com:8080")

    import importlib

    import ecjtu_wechat_api.core.config

    importlib.reload(ecjtu_wechat_api.core.config)

    from ecjtu_wechat_api.core.config import settings as reloaded_settings

    assert reloaded_settings.API_BASE_URL == "http://custom.example.com:8080"


def test_config_singleton():
    """测试配置单例模式"""
    from ecjtu_wechat_api.core.config import settings as settings1
    from ecjtu_wechat_api.core.config import settings as settings2

    # 应该是同一个实例
    assert settings1 is settings2


def test_config_class_attributes():
    """测试 Config 类的所有属性"""
    expected_attrs = [
        "WEIXIN_ID",
        "API_BASE_URL",
        "PROJECT_ROOT",
        "DATA_DIR",
        "WECHAT_USER_AGENT",
        "DEFAULT_HEADERS",
        "BASE_URL",
        "SCORE_URL",
        "COURSE_URL",
        "EXAM_URL",
    ]

    for attr in expected_attrs:
        assert hasattr(settings, attr), f"Config 缺少属性: {attr}"
