"""
实用工具包
"""

from ecjtu_wechat_api.utils.cache import (
    clear_cache,
    generate_cache_key,
    get_cache_stats,
    get_cached,
    set_cached,
)
from ecjtu_wechat_api.utils.http import close_http_client, get_page

__all__ = [
    "get_page",
    "close_http_client",
    "generate_cache_key",
    "get_cached",
    "set_cached",
    "clear_cache",
    "get_cache_stats",
]
