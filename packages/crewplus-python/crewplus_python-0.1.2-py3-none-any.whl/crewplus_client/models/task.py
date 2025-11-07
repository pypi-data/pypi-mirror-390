# -*- coding: utf-8 -*-
# @create: 2025-10-22
# @update: 2025-10-22
# @desc  : 定义与任务状态查询相关的 Pydantic 数据模型。

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .ingestion import JobStatus, SubTaskDetails


class SingleSubTaskDetails(BaseModel):
    """
    代表一个独立的子任务的详细状态。
    该模型用于解析 GET /task_status/{task_id} 接口的响应。
    """
    id: str
    name: Optional[str] = None
    status: JobStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retries: Optional[int] = None
    is_final: Optional[bool] = None
    graph_retries: Optional[int] = None
    graph_is_final: Optional[bool] = None
    graph_start_time: Optional[datetime] = None
    graph_end_time: Optional[datetime] = None
    graph_status: Optional[JobStatus] = None
    batch_type: Optional[str] = None
    task_info: Optional[str] = None
    batch_task_id: Optional[str] = None
    created_at: datetime = Field(..., alias="create_datetime")
    updated_at: datetime = Field(..., alias="update_datetime")


class PaginatedSubTaskList(BaseModel):
    """
    代表子任务列表的分页响应。
    """
    items: List[SubTaskDetails]
    total: int
    page: int
    limit: int
    pages: int
