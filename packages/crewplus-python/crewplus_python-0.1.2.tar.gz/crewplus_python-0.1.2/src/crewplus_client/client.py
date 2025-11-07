# -*- coding: utf-8 -*-
# @create: 2025-10-20
# @update: 2025-10-20
# @desc  : 定义 SDK 的核心客户端 CrewPlusClient。

import requests
from typing import Any, Optional

# 导入自定义异常和资源管理器
from .exceptions import ApiException, NotFoundException, AuthenticationException
from .managers.knowledge_base import KnowledgeBaseManager
from .managers.ingestion import IngestionManager
from .managers.task import TaskManager

class CrewPlusClient:
    """
    Crewplus Python SDK 的主客户端。
    
    该客户端处理所有底层的 API 请求、认证和错误处理。
    通过该客户端的属性可以访问各类 API 资源管理器。
    
    Attributes:
        knowledge_bases (KnowledgeBaseManager): 知识库资源管理器。
        ingestion (IngestionManager): 文档摄取任务管理器。
        tasks (TaskManager): 任务状态查询管理器。
    """
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """
        初始化 CrewPlusClient。

        Args:
            api_key (str): 用于认证的 API 密钥。
            base_url (str): Crewplus API 服务的基础 URL 地址, 例如 "https://api.crewplus.ai"。
            timeout (int, optional): HTTP 请求的默认超时时间（秒）。默认为 30。
        """
        self._base_url: str = base_url.rstrip("/")  # 确保 base_url 末尾没有斜杠
        self._api_key: str = api_key
        self._timeout: int = timeout
        
        # 初始化 requests.Session，用于管理连接和头部信息
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-KEY": self._api_key,
            "Content-Type": "application/json"
        })
        
        # 初始化所有资源管理器
        self.knowledge_bases = KnowledgeBaseManager(self)
        self.ingestion = IngestionManager(self)
        self.tasks = TaskManager(self)
        # self.documents = DocumentManager(self) # 待实现
        # self.tasks = TaskManager(self)       # 待实现

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """
        执行 API 请求的内部核心方法。

        Args:
            method (str): HTTP 请求方法 (e.g., "GET", "POST", "DELETE")。
            path (str): API 的请求路径 (e.g., "/crewplus/v2/knowledgebase")。
            **kwargs: 传递给 requests.Session.request 的其他参数 (e.g., json, params)。

        Returns:
            Any: 从 API 响应的 "data" 字段中解析出的数据。

        Raises:
            AuthenticationException: 如果认证失败 (401, 403)。
            NotFoundException: 如果资源未找到 (404)。
            ApiException: 如果发生其他 API 相关错误。
            requests.exceptions.RequestException: 如果发生网络层面的错误。
        """
        url = f"{self._base_url}{path}"
        
        # 设置默认超时
        kwargs.setdefault("timeout", self._timeout)
        
        try:
            response = self._session.request(method, url, **kwargs)
            
            # 优先尝试解析 JSON，以便获取后端返回的详细错误信息
            response_json: Optional[dict] = None
            try:
                response_json = response.json()
            except requests.JSONDecodeError:
                # 如果响应体不是合法的 JSON，也继续处理 HTTP 错误
                pass

            # 优雅地处理 HTTP 错误
            if not response.ok:
                message = response_json.get("message", response.text) if response_json else response.text
                status_code = response.status_code
                if status_code in (401, 403):
                    raise AuthenticationException(status_code, message, response_text=response.text)
                if status_code == 404:
                    raise NotFoundException(status_code, message, response_text=response.text)
                # 其他错误统一用 ApiException
                raise ApiException(status_code, message, response_text=response.text)
            
            # [修正] 统一解包后端 SuccessResponse，直接返回 `data` 字段
            # 如果响应不合法 (不是 JSON，或 JSON 中没有 "data" 字段)，则抛出异常
            if response_json and "data" in response_json:
                return response_json["data"]
            else:
                # 这种情况下，服务器返回了 2xx 成功状态码，但响应体格式不符合预期
                # 这应该被视为一个 API 错误
                raise ApiException(
                    response.status_code,
                    "API a devoluat un răspuns de succes, dar corpul răspunsului este invalid sau nu conține câmpul 'data'.",
                    response_text=response.text
                )

        except requests.exceptions.RequestException as e:
            # 捕获网络层面的异常并重新抛出，以便上层可以处理
            # log.error(f"Network error during request to {url}: {e}")
            raise e
