import httpx

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.core.exceptions import EducationSystemError
from ecjtu_wechat_api.utils.logger import logger


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
    async with httpx.AsyncClient(
        headers=settings.DEFAULT_HEADERS, timeout=timeout
    ) as client:
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
