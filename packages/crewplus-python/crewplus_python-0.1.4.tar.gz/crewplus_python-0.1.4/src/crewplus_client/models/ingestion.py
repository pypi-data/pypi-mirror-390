# -*- coding: utf-8 -*-
# @create: 2025-10-21
# @update: 2025-10-21
# @desc  : 定义与文档摄取任务相关的 Pydantic 数据模型和核心交互对象。

import time
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..managers.ingestion import IngestionManager
    from ..models.task import PaginatedSubTaskList


# --- Enums ---
class JobStatus(str, Enum):
    """与后端 TaskStatus 保持一致的任务状态枚举。"""
    PENDING = "PENDING"
    IN_PROGRESS = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    STOPPED = "STOPPED"

class IngestTaskType(str, Enum):
    """
    指定要操作的任务类型，与后端保持一致。
    """
    BATCH_TASKS = "BATCH_TASKS"  # 操作整个批次任务
    SUB_TASKS = "SUB_TASKS"      # 操作批次下的一个或多个子任务

# --- Data Models ---
class BatchJobDetails(BaseModel):
    """
    代表一个批量摄取任务的详细状态。
    该模型用于解析 GET /batch_task_status/{batch_id} 接口的响应。
    """
    job_id: str = Field(..., alias="batch_id")
    status: JobStatus
    total_tasks: int = Field(..., alias="total")
    completed_tasks: int = Field(..., alias="completed")
    failed_tasks: int = Field(..., alias="failed")
    progress: str
    created_at: datetime = Field(..., alias="start_time")
    updated_at: datetime = Field(..., alias="update_time")
    task_info: Optional[str] = None

class SubTaskDetails(BaseModel):
    """
    代表一个子任务及其关联文档的详细信息。
    该模型用于解析 GET /task_list_status/{batch_id} 接口响应中的 'items'。
    """
    task_id: str = Field(..., alias="id")
    status: JobStatus
    task_info: Optional[str] = None
    created_at: datetime = Field(..., alias="create_datetime")
    updated_at: datetime = Field(..., alias="update_datetime")
    
    # --- 关联的文档信息 ---
    document_id: Optional[int] = None
    title: Optional[str] = None
    source_url: Optional[str] = None
    file_type: Optional[str] = None

# --- Interaction Class ---
class IngestionJob:
    """
    一个摄取任务的操作句柄。
    
    用户在发起一个摄取任务后会获得此对象，可通过它来追踪和管理任务。
    """
    def __init__(self, job_id: str, manager: "IngestionManager", initial_details: Optional[BatchJobDetails] = None):
        self._job_id = job_id
        self._manager = manager
        self.details = initial_details

    @property
    def id(self) -> str:
        """返回当前任务的 Job ID (即 Batch Task ID)。"""
        return self._job_id

    def refresh(self) -> BatchJobDetails:
        """
        刷新并返回任务的最新状态。
        
        Returns:
            BatchJobDetails: 最新的任务详细状态。
        """
        self.details = self._manager._client.tasks.get_batch_task_details(self.id)
        return self.details

    def get_subtasks(self, status: Optional[JobStatus] = None, page: int = 1, limit: int = 20) -> "PaginatedSubTaskList":
        """
        获取此批量任务下的子任务列表（支持按状态筛选和分页）。
        
        Args:
            status: 按指定状态筛选子任务。
            page: 要获取的页码, 从 1 开始。
            limit: 每页返回的任务数量。
            
        Returns:
            一个包含子任务列表和分页信息的 PaginatedSubTaskList 对象。
        """
        return self._manager._client.tasks.list_subtasks(self.id, status=status, page=page, limit=limit)

    def cancel(self) -> dict:
        """
        请求取消整个批量任务。
        这是一个尽力而为的操作，不会立即停止所有正在运行的 Celery worker。
        """
        return self._manager.cancel_job(self.id)

    def stop(self, kbase_id: int, kbase_name: str, vector_store: str, graph_service: Optional[str] = None, vector_only: bool = False) -> dict:
        """
        请求停止当前这个批次任务。
        
        这是一个尽力而为的操作。需要提供任务关联的配置信息以满足后端接口要求。
        
        Args:
            kbase_id: 任务所属的知识库 ID。
            kbase_name: 任务所属的知识库名称。
            vector_store: 向量存储实例名称。
            graph_service: (可选) 图存储实例名称。
            vector_only: 是否只进行向量化处理。
            
        Returns:
            后端返回的成功信息字典。
        """
        return self._manager.stop_tasks(
            task_ids=[self.id],
            task_type=IngestTaskType.BATCH_TASKS,
            kbase_id=kbase_id,
            kbase_name=kbase_name,
            vector_store=vector_store,
            graph_service=graph_service,
            vector_only=vector_only
        )
    
    def restart(self, kbase_id: int, kbase_name: str, source_type: str, source_config: dict, vector_store: str, **kwargs) -> dict:
        """
        请求重新启动当前这个批次任务。
        
        需要提供最初发起任务时的完整数据源配置信息，以便后端重新获取文档。
        
        Args:
            kbase_id: 任务所属的知识库 ID。
            kbase_name: 任务所属的知识库名称。
            source_type: 原始数据源类型 (例如, 'sharepoint', 'box')。
            source_config: 原始数据源的完整配置。
            vector_store: 向量存储实例名称。
            **kwargs: 其他可选的摄取参数，如 graph_service, vector_only, chunk_size 等。
        
        Returns:
            后端返回的成功信息字典。
        """
        return self._manager.restart_tasks(
            task_ids=[self.id],
            task_type=IngestTaskType.BATCH_TASKS,
            kbase_id=kbase_id,
            kbase_name=kbase_name,
            source_type=source_type,
            source_config=source_config,
            vector_store=vector_store,
            **kwargs
        )

    def wait_for_completion(
        self,
        timeout: int = 3600,
        poll_interval: int = 10,
        on_progress: Optional[Callable[[BatchJobDetails], None]] = None
    ) -> "IngestionJob":
        """
        阻塞式等待任务完成，支持超时和进度回调。
        
        此方法会定期轮询任务状态，直到任务达到终结状态（如 COMPLETED, FAILED）或超时。
        
        Args:
            timeout: 最长等待时间（秒）。默认为 1 小时。
            poll_interval: 轮询状态的间隔时间（秒）。默认为 10 秒。
            on_progress: 一个可选的回调函数。每次获取到新状态时，该函数都会被调用，
                         并传入最新的 `BatchJobDetails` 对象作为参数。
        
        Returns:
            返回自身，以便于进行链式调用。
            
        Raises:
            TimeoutError: 如果在指定的超时时间内任务未能完成。
        """
        start_time = time.monotonic()
        
        latest_details = self.refresh()
        if on_progress:
            on_progress(latest_details)

        final_statuses = [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.PARTIAL_SUCCESS, JobStatus.STOPPED]
        while latest_details.status not in final_statuses:
            elapsed_time = time.monotonic() - start_time
            if elapsed_time > timeout:
                raise TimeoutError(f"等待任务 {self.id} 完成超时（超过 {timeout} 秒）。")
            
            # 确保等待时间不会超过总超时
            wait_time = min(poll_interval, timeout - elapsed_time)
            time.sleep(wait_time)
            
            latest_details = self.refresh()
            if on_progress:
                on_progress(latest_details)
        
        return self
