# -*- coding: utf-8 -*-
# @create: 2025-10-20
# @update: 2025-10-20
# @desc  : 封装所有与知识库（Knowledge Base）资源相关的 API 操作。

from typing import List, TYPE_CHECKING, Optional
from ..models.knowledge_base import KnowledgeBase
from ..exceptions import ApiException

# 使用 TYPE_CHECKING 来避免循环导入，同时为类型检查器提供信息
if TYPE_CHECKING:
    from ..client import CrewPlusClient

class KnowledgeBaseManager:
    """
    管理知识库资源的类。
    
    提供创建、查询、更新和删除知识库的方法。
    """
    def __init__(self, client: "CrewPlusClient"):
        """
        初始化 KnowledgeBaseManager。

        Args:
            client (CrewPlusClient): 用于执行 API 请求的客户端实例。
        """
        self._client = client

    def create(self, coll_name: str, coll_id: int, vector_store: str, description: str = "") -> KnowledgeBase:
        """
        创建一个新的知识库。

        Args:
            coll_name (str): 集合的业务名称。
            coll_id (int): 集合的唯一标识符 (来自 SaaS 系统的整数 ID)。
            vector_store (str): 要使用的向量存储实例的名称。
            description (str, optional): 知识库的描述。默认为 ""。

        Returns:
            KnowledgeBase: 新创建的知识库对象。
        """
        # 后端创建接口的路径是单数形式
        params = {"vector_store": vector_store}
        payload = {"coll_name": coll_name, "coll_id": coll_id, "description": description}

        response_data = self._client._request(
            "POST",
            "/crewplus/v2/knowledgebase",
            params=params,
            json=payload
        )
        return KnowledgeBase.model_validate(response_data)

    def get(self, kb_id: int) -> KnowledgeBase:
        """
        根据 ID 获取单个知识库的详细信息。

        Args:
            kb_id (int): 知识库的 ID。

        Returns:
            KnowledgeBase: 匹配的知识库对象。
        """
        # 后端获取单个资源的路径是单数形式
        response_data = self._client._request("GET", f"/crewplus/v2/knowledgebase/{kb_id}")
        return KnowledgeBase.model_validate(response_data)
        
    def find_by_coll_name(self, coll_name: str) -> KnowledgeBase:
        """
        根据集合名称查找知识库。

        Args:
            coll_name (str): 集合的业务名称。

        Returns:
            KnowledgeBase: 匹配的知识库对象。
        """
        response_data = self._client._request("GET", f"/crewplus/v2/knowledgebase/find/{coll_name}")
        return KnowledgeBase.model_validate(response_data)

    def update(
        self, 
        kb_id: int, 
        name: Optional[str] = None,
        coll_name: Optional[str] = None, 
        coll_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> KnowledgeBase:
        """
        更新一个已存在的知识库。

        此方法采用“先读后写”模式以兼容严格的 PUT 接口：
        它首先获取资源的当前状态，然后应用更改，最后将完整的对象发送回去。

        Args:
            kb_id (int): 要更新的知识库的 ID。
            name (Optional[str], optional): 新的知识库名称。
            coll_name (Optional[str], optional): 新的集合业务名称。
            coll_id (Optional[int], optional): 新的集合唯一标识符。
            description (Optional[str], optional): 新的描述。
            is_active (Optional[bool], optional): 新的激活状态。

        Returns:
            KnowledgeBase: 更新后的知识库对象。
        """
        # 1. 先获取当前对象的完整状态，以确保我们拥有所有必需字段。
        try:
            current_kb = self.get(kb_id)
        except Exception as e:
            raise ApiException(f"Failed to fetch knowledge base with ID {kb_id} before updating. Original error: {e}")

        # 2. 将当前对象转换为字典，作为更新的基础。
        #    注意：API 的输入模型可能与 SDK 的输出模型不同，我们只取 API 需要的字段。
        payload = {
            "name": current_kb.name,
            "coll_name": current_kb.coll_name,
            "coll_id": current_kb.coll_id,
            "description": current_kb.description,
            "is_active": current_kb.is_active,
            "create_user_id": current_kb.create_user_id,
        }
        
        # 3. 准备用户提供的、需要更新的数据。
        provided_updates = {
            "name": name,
            "coll_name": coll_name,
            "coll_id": coll_id,
            "description": description,
            "is_active": is_active,
        }

        # 4. 过滤掉未提供的参数（值为 None），并将有效的更新合并到 payload 中。
        cleaned_updates = {k: v for k, v in provided_updates.items() if v is not None}
        payload.update(cleaned_updates)
        
        # 5. 发送包含完整数据的 PUT 请求。
        response_data = self._client._request(
            "PUT",
            f"/crewplus/v2/knowledgebase/{kb_id}",
            json=payload
        )
        return KnowledgeBase.model_validate(response_data)

    def list(self, **params) -> List[KnowledgeBase]:
        """
        获取知识库列表，支持通过参数进行筛选。

        Args:
            **params: 传递给 API 的查询参数, 例如 limit, offset, name__icontains 等。

        Returns:
            List[KnowledgeBase]: 知识库对象列表。
        """
        # 后端获取列表的路径是复数形式
        response_data = self._client._request("GET", "/crewplus/v2/knowledgebases", params=params) or []
        return [KnowledgeBase.model_validate(item) for item in response_data]

    def delete(self, kb_id: int) -> None:
        """
        删除一个知识库。

        此方法会调用后端的批量删除接口，并检查响应以确保指定的 ID 已被成功删除。
        如果删除失败，则会引发 ApiException。

        Args:
            kb_id (int): 要删除的知识库的 ID。
        
        Raises:
            ApiException: 如果 API 响应表明删除未成功。
        """
        response = self._client._request("DELETE", "/crewplus/v2/knowledgebases", json={"ids": [kb_id]})
        
        # [兼容性修正] 检查响应是否为字典
        if isinstance(response, dict):
            # 首先，处理由 client._request 针对 DELETE 2xx 响应生成的通用成功对象
            if response.get("success") is True:
                return True

            # 其次，处理后端返回的、包含成功ID列表的详细响应
            success_ids = response.get("success", [])
            if isinstance(success_ids, list) and kb_id in success_ids:
                return True
            else:
                # 如果 'failed' 列表提供了具体原因，我们使用它
                failed_items = response.get("failed", [])
                failed_info = next((item for item in failed_items if item.get("id") == kb_id), {})
                reason = failed_info.get("reason", "Unknown reason. The ID was not in the success list.")
                raise ApiException(f"Deletion failed for ID {kb_id}. Reason: {reason}")
