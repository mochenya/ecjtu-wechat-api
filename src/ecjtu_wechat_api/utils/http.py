import httpx

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.core.exceptions import EducationSystemError
from ecjtu_wechat_api.utils.logger import logger

# 全局 HTTP 客户端单例（连接池复用）
_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """
    获取全局 HTTP 客户端（连接池复用）。

    使用单例模式复用 TCP 连接，避免每次请求都建立新连接，
    可显著减少 50-200ms 的握手延迟。

    Returns:
        httpx.AsyncClient: 全局 HTTP 客户端实例
    """
    global _client
    if _client is None:
        # 配置连接池参数
        limits = httpx.Limits(
            max_keepalive_connections=20,  # 最大保持连接数
            max_connections=100,  # 最大连接数
            keepalive_expiry=30.0,  # 保持连接过期时间（秒）
        )
        _client = httpx.AsyncClient(
            headers=settings.DEFAULT_HEADERS,
            timeout=httpx.Timeout(10.0, connect=10.0),
            limits=limits,
        )
        logger.info("HTTP 连接池已初始化")
    return _client


async def close_http_client() -> None:
    """
    关闭 HTTP 连接池。

    应在应用关闭时调用，确保资源正确释放。
    """
    global _client
    if _client is not None:
        try:
            await _client.aclose()
            logger.info("HTTP 连接池已关闭")
        except RuntimeError as e:
            # 事件循环已关闭或其他运行时错误，静默处理
            if "Event loop is closed" not in str(e):
                logger.warning(f"关闭 HTTP 连接池时出错: {e}")
        except Exception as e:
            logger.warning(f"关闭 HTTP 连接池时出错: {e}")
        finally:
            _client = None


async def get_page(url: str, params: dict | None = None, timeout: int = 10) -> str:
    """
    异步获取网页内容。

    Args:
        url: 目标 URL
        params: 请求参数
        timeout: 超时时间（秒）

    Returns:
        str: 网页 HTML 内容

    Raises:
        EducationSystemError: 请求失败或教务系统返回错误
    """
    client = await get_http_client()
    try:
        response = await client.get(url, params=params)
        response.encoding = "utf-8"

        if response.status_code != 200:
            logger.error(
                f"教务系统返回非 200 状态码: {response.status_code}, URL: {url}"
            )
            raise EducationSystemError(
                message=f"教务系统返回错误 (状态码: {response.status_code})",
                status_code=response.status_code,
            )

        return response.text
    except httpx.RequestError as e:
        logger.error(f"请求教务系统出错: {e}, URL: {url}")
        raise EducationSystemError(message=f"网络请求失败: {str(e)}") from e
