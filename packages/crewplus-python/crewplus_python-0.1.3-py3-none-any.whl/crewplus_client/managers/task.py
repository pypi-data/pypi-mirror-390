# -*- coding: utf-8 -*-
# @create: 2025-10-22
# @update: 2025-10-22
# @desc  : 封装所有与任务状态查询相关的 API 操作。

from typing import TYPE_CHECKING, Optional

from ..models.ingestion import BatchJobDetails, JobStatus
from ..models.task import PaginatedSubTaskList, SingleSubTaskDetails

if TYPE_CHECKING:
    from ..client import CrewPlusClient


class TaskManager:
    """
    管理任务状态查询的类。
    """
    def __init__(self, client: "CrewPlusClient"):
        self._client = client

    def get_batch_task_details(self, batch_id: str) -> BatchJobDetails:
        """
        获取指定批量任务的详细状态。

        Args:
            batch_id: 批量任务的 ID。

        Returns:
            一个包含批量任务详细信息的 BatchJobDetails 对象。
        """
        data = self._client._request("GET", f"/crewplus/v2/batch_task_status/{batch_id}")
        return BatchJobDetails.model_validate(data)

    def list_subtasks(self, batch_id: str, status: Optional[JobStatus] = None, page: int = 1, limit: int = 20) -> PaginatedSubTaskList:
        """
        获取指定批量任务下的子任务列表（支持分页和状态筛选）。

        Args:
            batch_id: 批量任务的 ID。
            status: (可选) 按指定状态筛选子任务。
            page: (可选) 要获取的页码, 从 1 开始。
            limit: (可选) 每页返回的任务数量。

        Returns:
            一个包含子任务列表和分页信息的 PaginatedSubTaskList 对象。
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status.value
            
        data = self._client._request("GET", f"/crewplus/v2/task_list_status/{batch_id}", params=params)
        return PaginatedSubTaskList.model_validate(data)

    def get_subtask_details(self, subtask_id: str) -> SingleSubTaskDetails:
        """
        获取单个子任务的详细状态。

        Args:
            subtask_id: 子任务的 ID。

        Returns:
            一个包含子任务详细信息的 SingleSubTaskDetails 对象。
        """
        data = self._client._request("GET", f"/crewplus/v2/task_status/{subtask_id}")
        return SingleSubTaskDetails.model_validate(data)
