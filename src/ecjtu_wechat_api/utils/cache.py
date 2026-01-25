"""
内存缓存工具

提供简单的内存缓存功能，适合开发和小规模部署场景。
缓存数据带过期时间，自动清理过期数据。
"""

import hashlib
import json
from datetime import datetime, timedelta

from ecjtu_wechat_api.utils.logger import logger

# 简单内存缓存存储
# 格式: {cache_key: (value, expire_time)}
_cache: dict[str, tuple[any, datetime]] = {}


def generate_cache_key(weiXinID: str, **kwargs) -> str:
    """
    生成缓存键。

    Args:
        weiXinID: 微信用户 ID
        **kwargs: 其他参数（如 date, term 等）

    Returns:
        str: MD5 哈希后的缓存键
    """
    # 将参数排序后序列化，确保相同参数生成相同键
    data = f"{weiXinID}:{json.dumps(kwargs, sort_keys=True)}"
    return hashlib.md5(data.encode()).hexdigest()


def get_cached(key: str, ttl: int = 3600) -> any | None:
    """
    获取缓存数据。

    Args:
        key: 缓存键
        ttl: 生存时间（秒），仅用于验证

    Returns:
        any: 缓存的数据，如果不存在或已过期则返回 None
    """
    if key in _cache:
        value, expire_time = _cache[key]
        if datetime.now() < expire_time:
            logger.debug(f"缓存命中: {key}")
            return value
        else:
            # 清理过期缓存
            del _cache[key]
            logger.debug(f"缓存已过期: {key}")
    return None


def set_cached(key: str, value: any, ttl: int = 3600) -> None:
    """
    设置缓存数据。

    Args:
        key: 缓存键
        value: 要缓存的值
        ttl: 生存时间（秒），默认 1 小时
    """
    expire_time = datetime.now() + timedelta(seconds=ttl)
    _cache[key] = (value, expire_time)
    logger.debug(f"缓存已设置: {key}, TTL: {ttl}s")


def clear_cache() -> None:
    """
    清空所有缓存。
    """
    count = len(_cache)
    _cache.clear()
    logger.info(f"已清空 {count} 条缓存")


def get_cache_stats() -> dict[str, any]:
    """
    获取缓存统计信息。

    Returns:
        dict: 包含缓存条目数和过期时间信息
    """
    now = datetime.now()
    active_count = sum(1 for _, expire_time in _cache.values() if now < expire_time)
    expired_count = len(_cache) - active_count

    return {
        "total_entries": len(_cache),
        "active_entries": active_count,
        "expired_entries": expired_count,
    }
