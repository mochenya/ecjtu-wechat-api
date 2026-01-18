"""
持久化工具测试模块
"""

from unittest.mock import patch

from pydantic import BaseModel

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.utils.persistence import save_debug_data


class MockModel(BaseModel):
    """用于测试的 Pydantic 模型"""

    name: str
    value: int


# 正常场景测试
def test_save_debug_data_both_html_and_json(tmp_path, monkeypatch):
    """测试同时保存 HTML 和 JSON"""
    # 临时修改 DATA_DIR
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    html_content = "<html>Test Content</html>"
    parsed_data = {"name": "test", "value": 123}

    save_debug_data("test_category", "test_file", html_content, parsed_data)

    # 验证文件已创建
    html_file = tmp_path / "test_category" / "test_file.html"
    json_file = tmp_path / "test_category" / "test_file.json"

    assert html_file.exists()
    assert json_file.exists()

    # 验证内容
    assert html_file.read_text(encoding="utf-8") == html_content

    json_content = json_file.read_text(encoding="utf-8")
    assert "test" in json_content
    assert "123" in json_content


def test_save_debug_data_html_only(tmp_path, monkeypatch):
    """测试仅保存 HTML"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    html_content = "<html>HTML Only</html>"

    save_debug_data("test_category", "test_file", html_content=html_content)

    html_file = tmp_path / "test_category" / "test_file.html"
    json_file = tmp_path / "test_category" / "test_file.json"

    assert html_file.exists()
    assert not json_file.exists()


def test_save_debug_data_json_only(tmp_path, monkeypatch):
    """测试仅保存 JSON"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    parsed_data = {"name": "json_only", "value": 456}

    save_debug_data("test_category", "test_file", parsed_data=parsed_data)

    html_file = tmp_path / "test_category" / "test_file.html"
    json_file = tmp_path / "test_category" / "test_file.json"

    assert not html_file.exists()
    assert json_file.exists()


def test_save_debug_data_with_pydantic_model(tmp_path, monkeypatch):
    """测试使用 Pydantic 模型保存"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    model_data = MockModel(name="pydantic_test", value=789)

    save_debug_data("test_category", "test_file", parsed_data=model_data)

    json_file = tmp_path / "test_category" / "test_file.json"
    assert json_file.exists()

    json_content = json_file.read_text(encoding="utf-8")
    assert "pydantic_test" in json_content
    assert "789" in json_content


def test_save_debug_data_creates_directory(tmp_path, monkeypatch):
    """测试自动创建目录"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    save_debug_data(
        "new_category/sub_category", "test_file", html_content="<html>New</html>"
    )

    # 验证嵌套目录已创建
    sub_dir = tmp_path / "new_category" / "sub_category"
    assert sub_dir.exists()
    assert (sub_dir / "test_file.html").exists()


# 异常场景测试
def test_save_debug_data_handle_write_errors(tmp_path, monkeypatch):
    """测试处理写入错误"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    # Mock open 函数模拟写入错误
    with patch("builtins.open", side_effect=OSError("Permission denied")):
        # 不应该抛出异常，而是记录警告
        save_debug_data("test_category", "test_file", html_content="<html>Error</html>")


def test_save_debug_data_empty_data(tmp_path, monkeypatch):
    """测试空数据不创建文件"""
    monkeypatch.setattr(settings, "DATA_DIR", tmp_path)

    # 不提供任何数据
    save_debug_data("test_category", "test_file")

    # 目录应该被创建，但没有文件
    category_dir = tmp_path / "test_category"
    assert category_dir.exists()

    html_file = category_dir / "test_file.html"
    json_file = category_dir / "test_file.json"

    assert not html_file.exists()
    assert not json_file.exists()
