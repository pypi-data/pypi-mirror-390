# -*- coding: utf-8 -*-
# @create: 2025-10-21
# @update: 2025-10-21
# @desc  : 封装所有与文档摄取（Ingestion）相关的 API 操作。

from typing import TYPE_CHECKING, List, Optional

from ..models.ingestion import IngestionJob, BatchJobDetails, SubTaskDetails, JobStatus, IngestTaskType

if TYPE_CHECKING:
    from ..client import CrewPlusClient

class IngestionManager:
    """
    管理文档摄取任务的类。
    
    提供从不同数据源发起摄取任务、管理任务生命周期（重启、停止、取消）
    以及查询任务状态的功能。
    """
    def __init__(self, client: "CrewPlusClient"):
        self._client = client

    def ingest_from_sharepoint(
        self,
        kbase_id: int,
        kbase_name: str,
        site_id: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        vector_store: str,
        graph_service: Optional[str] = None,
        vector_only: bool = False,
        incremental: bool = False,
        chunk_size: int = 1000,
        parser: Optional[str] = None,
        schema_ids: Optional[List[int]] = None,
        priority: str = "normal",
    ) -> IngestionJob:
        """
        从 SharePoint 站点摄取文档。
        
        Args:
            kbase_id: 目标知识库的 ID。
            kbase_name: 目标知识库的名称。
            site_id: SharePoint 站点的 ID。
            tenant_id: Azure AD (Entra ID) 的租户 ID。
            client_id: Azure AD 应用注册的客户端 ID。
            client_secret: Azure AD 应用注册的客户端密钥。
            vector_store: 要使用的向量存储实例的名称。
            graph_service: (可选) 要使用的图存储实例的名称。
            vector_only: 是否只进行向量化处理。
            incremental: 是否执行增量摄取。默认为 False (全量)。
            chunk_size: 文档分块的大小。
            parser: (可选) 指定文档解析器。
            schema_ids: (可选) 关联的 Schema ID 列表。
            priority: (可选) 任务优先级。
            
        Returns:
            一个 IngestionJob 对象，可用于追踪任务状态。
        """
        endpoint = "/crewplus/v2/aingest_library_delta" if incremental else "/crewplus/v2/aingest_library"
        
        config_payload = {
            "site_id": site_id,
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
            "vector_store": vector_store,
        }
        if graph_service:
            config_payload["graph_service"] = graph_service
        
        json_payload = {
            "kbase_id": kbase_id,
            "kbase_name": kbase_name,
            "config": config_payload,
            "vector_only": vector_only,
            "source_type": "sharepoint",
            "chunk_size": chunk_size,
            "parser": parser,
            "schema_ids": schema_ids,
            "priority": priority,
        }

        response_data = self._client._request("POST", endpoint, json=json_payload)
        
        # 后端返回的 task_ids 可能是单个字符串或列表，我们统一处理
        batch_id = response_data.get("task_ids")
        if isinstance(batch_id, list):
            batch_id = batch_id[0] if batch_id else None

        if not batch_id:
            raise ValueError("API 未能返回有效的 Job ID。")

        return IngestionJob(job_id=batch_id, manager=self)

    def ingest_from_box(
        self,
        kbase_id: int,
        kbase_name: str,
        box_folder_id: str,
        box_user_id: str,
        jwt_config: dict,
        vector_store: str,
        graph_service: Optional[str] = None,
        vector_only: bool = False,
        incremental: bool = False,
        chunk_size: int = 1000,
        parser: Optional[str] = None,
        schema_ids: Optional[List[int]] = None,
        priority: str = "normal",
    ) -> IngestionJob:
        """
        从 Box 文件夹发起文档摄取。

        Args:
            kbase_id: 知识库 ID。
            kbase_name: 知识库名称。
            box_folder_id: Box 文件夹 ID。
            box_user_id: 用于执行操作的 Box 用户 ID。
            jwt_config: Box JWT 认证所需的完整配置字典。
                        应包含 client-id, client-secret, enterprise-id, 
                        public-key-id, private-key, passphrase 等字段。
            vector_store: 要使用的向量存储实例的名称。
            graph_service: (可选) 要使用的图存储实例的名称。
            vector_only: 是否只进行向量化处理。
            incremental: 是否执行增量摄取。默认为 False (全量)。
            chunk_size: 文档分块的大小。
            parser: (可选) 指定文档解析器。
            schema_ids: (可选) 关联的 Schema ID 列表。
            priority: (可选) 任务优先级。
            
        Returns:
            一个 IngestionJob 对象，可用于追踪任务状态。
        """
        endpoint = "/crewplus/v2/aingest_library_delta" if incremental else "/crewplus/v2/aingest_library"
        
        config_payload = {
            "boxFolderId": box_folder_id,
            "boxUserId": box_user_id,
            "jwt": jwt_config,
            "vector_store": vector_store,
        }
        if graph_service:
            config_payload["graph_service"] = graph_service
            
        json_payload = {
            "kbase_id": kbase_id,
            "kbase_name": kbase_name,
            "config": config_payload,
            "vector_only": vector_only,
            "source_type": "box",
            "chunk_size": chunk_size,
            "parser": parser,
            "schema_ids": schema_ids,
            "priority": priority,
        }

        response_data = self._client._request("POST", endpoint, json=json_payload)
        
        batch_id = response_data.get("task_ids")
        if isinstance(batch_id, list):
            batch_id = batch_id[0] if batch_id else None

        if not batch_id:
            raise ValueError("API 未能返回有效的 Job ID。")

        return IngestionJob(job_id=batch_id, manager=self)

    def ingest_from_azure_storage(
        self,
        kbase_id: int,
        kbase_name: str,
        account_name: str,
        container_name: str,
        blob_path: str,
        vector_store: str,
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None,
        graph_service: Optional[str] = None,
        vector_only: bool = False,
        chunk_size: int = 1000,
        parser: Optional[str] = None,
        schema_ids: Optional[List[int]] = None,
        priority: str = "normal",
    ) -> IngestionJob:
        """
        从 Azure Storage Blob 摄取单个文档。

        Args:
            kbase_id: 知识库 ID。
            kbase_name: 知识库名称。
            account_name: Azure 存储账户名称。
            container_name: 容器名称。
            blob_path: 要摄取的 Blob 的完整路径。
            vector_store: 向量存储实例名称。
            account_key: (可选) 存储账户访问密钥。
            connection_string: (可选) 存储账户连接字符串。
                               (account_key 和 connection_string 至少提供一个)
            graph_service: (可选) 要使用的图存储实例的名称。
            vector_only: 是否只进行向量化处理。
            chunk_size: 文档分块的大小。
            parser: (可选) 指定文档解析器。
            schema_ids: (可选) 关联的 Schema ID 列表。
            priority: (可选) 任务优先级。
            
        Returns:
            一个 IngestionJob 对象，可用于追踪任务状态。
        """
        if not account_key and not connection_string:
            raise ValueError("参数 `account_key` 和 `connection_string` 必须至少提供一个。")

        # Azure Storage 总是全量处理单个文件，因此总是调用 aingest_library
        endpoint = "/crewplus/v2/aingest_library"
        
        config_payload = {
            "account_name": account_name,
            "container_name": container_name,
            "blob_path": blob_path,
            "account_key": account_key,
            "connection_string": connection_string,
            "vector_store": vector_store,
        }
        if graph_service:
            config_payload["graph_service"] = graph_service
            
        json_payload = {
            "kbase_id": kbase_id,
            "kbase_name": kbase_name,
            "config": config_payload,
            "vector_only": vector_only,
            "source_type": "azure_storage",
            "chunk_size": chunk_size,
            "parser": parser,
            "schema_ids": schema_ids,
            "priority": priority,
        }

        response_data = self._client._request("POST", endpoint, json=json_payload)
        
        batch_id = response_data.get("task_ids")
        if isinstance(batch_id, list):
            batch_id = batch_id[0] if batch_id else None

        if not batch_id:
            raise ValueError("API 未能返回有效的 Job ID。")

        return IngestionJob(job_id=batch_id, manager=self)

    # 在这里可以为 Box, Azure 等添加 ingest_from_box, ingest_from_azure 等方法...

    def get_job(self, job_id: str) -> IngestionJob:
        """
        通过 ID 获取一个已存在的摄取任务的操作句柄。
        
        这对于操作一个不是由当前程序发起的任务非常有用。
        
        Args:
            job_id: 批量任务的 ID。
            
        Returns:
            一个可用于交互的 IngestionJob 对象。
        """
        return IngestionJob(job_id=job_id, manager=self)

    def cancel_job(self, job_id: str) -> dict:
        """[基础接口] 请求取消一个批量任务。"""
        return self._client._request("POST", f"/batch/cancel/{job_id}")

    def restart_tasks(
        self,
        task_ids: List[str],
        task_type: "IngestTaskType",
        kbase_id: int,
        kbase_name: str,
        source_type: str,
        source_config: dict,
        vector_store: str,
        graph_service: Optional[str] = None,
        vector_only: bool = False,
        chunk_size: int = 1000,
        parser: Optional[str] = None,
        schema_ids: Optional[List[int]] = None,
        priority: str = "normal",
    ) -> dict:
        """
        重新启动一个或多个摄取任务（子任务或批任务）。

        Args:
            task_ids: 要重启的任务 ID 列表。
            task_type: 要重启的任务类型 (IngestTaskType.BATCH_TASKS 或 IngestTaskType.SUB_TASKS)。
            kbase_id: 任务所属的知识库 ID。
            kbase_name: 任务所属的知识库名称。
            source_type: 原始数据源类型 (例如, 'sharepoint', 'box')。
            source_config: 原始数据源的完整配置，用于重新验证和获取文档。
                           例如，SharePoint 需要 site_id, tenant_id 等。
            vector_store: 向量存储实例名称。
            graph_service: (可选) 图存储实例名称。
            vector_only: 是否只进行向量化处理。
            chunk_size: 文档分块的大小。
            parser: (可选) 指定文档解析器。
            schema_ids: (可选) 关联的 Schema ID 列表。
            priority: (可选) 任务优先级。

        Returns:
            后端返回的成功信息字典。
        """
        endpoint = "/crewplus/v2/aingest_restart_tasks"
        
        # 将 source_config 与 vector_store/graph_service 合并到最终的 config 载荷中
        config_payload = source_config.copy()
        config_payload["vector_store"] = vector_store
        if graph_service:
            config_payload["graph_service"] = graph_service

        json_payload = {
            "task_ids": task_ids,
            "task_type": task_type.value,
            "kbase_id": kbase_id,
            "kbase_name": kbase_name,
            "source_type": source_type,
            "config": config_payload,
            "vector_only": vector_only,
            "chunk_size": chunk_size,
            "parser": parser,
            "schema_ids": schema_ids,
            "priority": priority,
        }

        return self._client._request("POST", endpoint, json=json_payload)

    def stop_tasks(
        self,
        task_ids: List[str],
        task_type: "IngestTaskType",
        kbase_id: int,
        kbase_name: str,
        vector_store: str,
        graph_service: Optional[str] = None,
        vector_only: bool = False,
    ) -> dict:
        """
        请求停止一个或多个正在进行的摄取任务。这是一个“尽力而为”的操作。

        Args:
            task_ids: 要停止的任务 ID 列表。
            task_type: 要停止的任务类型 (IngestTaskType.BATCH_TASKS 或 IngestTaskType.SUB_TASKS)。
            kbase_id: 任务所属的知识库 ID。
            kbase_name: 任务所属的知识库名称。
            vector_store: 向量存储实例名称。
            graph_service: (可选) 图存储实例名称。
            vector_only: 是否只进行向量化处理。

        Returns:
            后端返回的成功信息字典。
        """
        endpoint = "/crewplus/v2/aingest_stop_tasks"
        
        config_payload = {
            "vector_store": vector_store
        }
        if graph_service:
            config_payload["graph_service"] = graph_service

        json_payload = {
            "task_ids": task_ids,
            "task_type": task_type.value,
            "kbase_id": kbase_id,
            "kbase_name": kbase_name,
            "config": config_payload,
            "vector_only": vector_only,
        }

        return self._client._request("POST", endpoint, json=json_payload)
