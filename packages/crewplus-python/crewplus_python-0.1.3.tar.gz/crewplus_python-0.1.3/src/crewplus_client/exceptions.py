# -*- coding: utf-8 -*-
# @create: 2025-10-20
# @update: 2025-10-20
# @desc  : 定义 SDK 的所有自定义异常。

from typing import Optional

class ApiException(Exception):
    """
    SDK 中所有 API 相关异常的基类。

    Attributes:
        status_code (int): 发生异常时的 HTTP 状态码。
        message (str): 从 API 返回的或 SDK 内部生成的错误信息。
        response_text (Optional[str]): 服务器返回的原始响应体文本，用于调试。
    """
    def __init__(self, status_code: int, message: Optional[str] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.message = message or f"An API error occurred with status code {status_code}"
        self.response_text = response_text
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[Status Code: {self.status_code}] {self.message}"


class AuthenticationException(ApiException):
    """
    当 API 密钥无效或权限不足时（HTTP 401, 403）抛出。
    """
    def __init__(self, status_code: int, message: Optional[str] = "Authentication failed. Please check your API key.", response_text: Optional[str] = None):
        super().__init__(status_code, message, response_text)


class NotFoundException(ApiException):
    """
    当请求的资源不存在时（HTTP 404）抛出。
    """
    def __init__(self, status_code: int, message: Optional[str] = "The requested resource was not found.", response_text: Optional[str] = None):
        super().__init__(status_code, message, response_text)
