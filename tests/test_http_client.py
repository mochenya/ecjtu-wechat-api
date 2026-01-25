"""
HTTP 客户端测试模块
"""

import pytest

from ecjtu_wechat_api.core.exceptions import EducationSystemError
from ecjtu_wechat_api.utils.http import get_page


@pytest.fixture(autouse=True)
def reset_http_client():
    """每个测试前后重置 HTTP 客户端"""
    import ecjtu_wechat_api.utils.http as http_module

    # 直接重置全局变量
    original_client = http_module._client
    http_module._client = None
    yield
    http_module._client = original_client


# 正常场景测试
@pytest.mark.asyncio
async def test_get_page_success(mocker):
    """测试成功获取网页内容"""
    # Mock httpx.AsyncClient.get 返回成功响应
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Test Content</html>"
    mock_response.encoding = "utf-8"

    mock_client_instance = mocker.Mock()
    mock_client_instance.get = mocker.AsyncMock(return_value=mock_response)
    mock_client_instance.aclose = mocker.AsyncMock()

    mock_client_class = mocker.Mock()
    mock_client_class.return_value = mock_client_instance

    mocker.patch("ecjtu_wechat_api.utils.http.httpx.AsyncClient", mock_client_class)

    result = await get_page("https://example.com")

    assert result == "<html>Test Content</html>"
    mock_client_instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_with_params(mocker):
    """测试带参数的请求"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Result</html>"
    mock_response.encoding = "utf-8"

    mock_client_instance = mocker.Mock()
    mock_client_instance.get = mocker.AsyncMock(return_value=mock_response)
    mock_client_instance.aclose = mocker.AsyncMock()

    mock_client_class = mocker.Mock()
    mock_client_class.return_value = mock_client_instance

    mocker.patch("ecjtu_wechat_api.utils.http.httpx.AsyncClient", mock_client_class)

    result = await get_page("https://example.com", params={"key": "value"})

    assert result == "<html>Result</html>"
    mock_client_instance.get.assert_called_once_with(
        "https://example.com", params={"key": "value"}
    )


# 异常场景测试
@pytest.mark.asyncio
async def test_get_page_timeout(mocker):
    """测试超时异常"""
    import httpx

    # Mock httpx.AsyncClient 抛出超时异常
    mock_client_instance = mocker.Mock()
    mock_client_instance.get = mocker.AsyncMock(
        side_effect=httpx.TimeoutException("Request timeout")
    )
    mock_client_instance.aclose = mocker.AsyncMock()

    mock_client_class = mocker.Mock()
    mock_client_class.return_value = mock_client_instance

    mocker.patch("ecjtu_wechat_api.utils.http.httpx.AsyncClient", mock_client_class)

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await get_page("https://example.com")


@pytest.mark.asyncio
async def test_get_page_connection_error(mocker):
    """测试连接错误"""
    import httpx

    # Mock httpx.AsyncClient 抛出连接错误
    mock_client_instance = mocker.Mock()
    mock_client_instance.get = mocker.AsyncMock(
        side_effect=httpx.RequestError("Connection error")
    )
    mock_client_instance.aclose = mocker.AsyncMock()

    mock_client_class = mocker.Mock()
    mock_client_class.return_value = mock_client_instance

    mocker.patch("ecjtu_wechat_api.utils.http.httpx.AsyncClient", mock_client_class)

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await get_page("https://example.com")


@pytest.mark.asyncio
async def test_get_page_non_200_status(mocker):
    """测试非 200 状态码"""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    mock_client_instance = mocker.Mock()
    mock_client_instance.get = mocker.AsyncMock(return_value=mock_response)
    mock_client_instance.aclose = mocker.AsyncMock()

    mock_client_class = mocker.Mock()
    mock_client_class.return_value = mock_client_instance

    mocker.patch("ecjtu_wechat_api.utils.http.httpx.AsyncClient", mock_client_class)

    with pytest.raises(EducationSystemError, match="教务系统返回错误"):
        await get_page("https://example.com")
