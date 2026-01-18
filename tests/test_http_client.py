"""
HTTP 客户端测试模块
"""

import pytest

from ecjtu_wechat_api.core.exceptions import EducationSystemError
from ecjtu_wechat_api.utils.http import get_page


# 正常场景测试
@pytest.mark.asyncio
async def test_get_page_success(mocker):
    """测试成功获取网页内容"""
    # Mock httpx.AsyncClient.get 返回成功响应
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Test Content</html>"
    mock_response.encoding = "utf-8"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    result = await get_page("https://example.com")

    assert result == "<html>Test Content</html>"
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_with_params(mocker):
    """测试带参数的请求"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Result</html>"
    mock_response.encoding = "utf-8"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    result = await get_page("https://example.com", params={"key": "value"})

    assert result == "<html>Result</html>"
    mock_client.get.assert_called_once_with(
        "https://example.com", params={"key": "value"}
    )


# 异常场景测试
@pytest.mark.asyncio
async def test_get_page_timeout(mocker):
    """测试超时异常"""
    import httpx

    # Mock httpx.RequestError 模拟超时
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(
        side_effect=httpx.TimeoutException("Request timeout")
    )

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await get_page("https://example.com")


@pytest.mark.asyncio
async def test_get_page_connection_error(mocker):
    """测试连接错误"""
    import httpx

    # Mock httpx.RequestError
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(
        side_effect=httpx.RequestError("Connection error")
    )

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await get_page("https://example.com")


@pytest.mark.asyncio
async def test_get_page_non_200_status(mocker):
    """测试非 200 状态码"""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    with pytest.raises(EducationSystemError, match="教务系统返回错误"):
        await get_page("https://example.com")
