from typing import Any


class ECJTUAPIError(Exception):
    """项目基础异常"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.message = message
        self.details = details


class EducationSystemError(ECJTUAPIError):
    """教务系统请求或返回错误"""

    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message, details)
        self.status_code = status_code


class ParseError(ECJTUAPIError):
    """HTML 解析错误"""

    pass
