"""
Loguru 日志模块 - 适配器模式实现

使用 Loguru 替代标准 logging 模块，提供：
- 彩色控制台输出
- 文件日志轮转与压缩
- 第三方库日志拦截
- 异步安全日志记录
"""

import inspect
import logging
import sys
from pathlib import Path
from typing import Any

from loguru import logger as _logger

from ecjtu_wechat_api.core.config import settings


class InterceptHandler(logging.Handler):
    """
    将标准 logging 日志转发到 Loguru

    用于拦截第三方库（httpx、uvicorn 等）的日志输出。
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 Loguru 日志级别
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者位置（Loguru 官方推荐实现）
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _setup_logger() -> None:
    """配置 Loguru 日志系统"""

    # 移除默认处理器
    _logger.remove()

    # 控制台处理器 - 彩色输出
    _logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.LOG_LEVEL,
        colorize=settings.LOG_COLORIZE,
        enqueue=True,  # 异步安全，避免阻塞
        serialize=settings.LOG_SERIALIZE,
    )

    # 创建日志目录
    log_path = Path(settings.PROJECT_ROOT) / settings.LOG_PATH
    log_path.mkdir(parents=True, exist_ok=True)

    # 日志格式字符串（复用以减少重复）
    _file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} | {message}"
    )

    # 文件处理器 - 所有级别日志
    _logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        format=_file_format,
        level="DEBUG",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        enqueue=True,
        serialize=settings.LOG_SERIALIZE,
        encoding="utf-8",
    )

    # 文件处理器 - 仅错误级别日志
    _logger.add(
        log_path / "errors_{time:YYYY-MM-DD}.log",
        format=_file_format,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        enqueue=True,
        serialize=settings.LOG_SERIALIZE,
        encoding="utf-8",
    )

    # 拦截标准 logging 日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 配置第三方库日志级别
    for logger_name in ("httpx", "httpcore", "uvicorn", "uvicorn.access"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False


class LoggerAdapter:
    """
    日志适配器 - 保持与标准 logging 接口兼容

    提供与标准 logging.Logger 相同的方法签名，确保现有代码无需修改。
    """

    def __init__(self, logger_instance: Any = _logger) -> None:
        self._logger = logger_instance

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出 DEBUG 级别日志"""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出 INFO 级别日志"""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出 WARNING 级别日志"""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出 ERROR 级别日志"""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出 CRITICAL 级别日志"""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """输出异常堆栈信息（ERROR 级别）"""
        self._logger.exception(message, *args, **kwargs)

    def bind(self, **kwargs: Any) -> "LoggerAdapter":
        """绑定上下文变量（Loguru 特性）"""
        return LoggerAdapter(self._logger.bind(**kwargs))

    def opt(self, **kwargs: Any) -> "LoggerAdapter":
        """高级选项（Loguru 特性）"""
        return LoggerAdapter(self._logger.opt(**kwargs))


# 导出兼容的 logger 实例
logger = LoggerAdapter()


# 延迟初始化日志系统，避免循环导入问题
_setup_initialized = False
try:
    _setup_logger()
    _setup_initialized = True
except Exception as e:
    # 如果 settings 初始化失败，使用基本配置确保日志可用
    _logger.remove()
    _basic_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    _logger.add(
        sys.stderr,
        format=_basic_format,
        level="INFO",
        enqueue=True,
    )
    _logger.warning(f"日志系统使用基本配置（完整配置加载失败: {e}）")
