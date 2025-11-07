# -*- coding: utf-8 -*-
# @create: 2025-10-20
# @update: 2025-10-21
# @desc  : 定义知识库（KnowledgeBase）相关的 Pydantic 数据模型。

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class KnowledgeBase(BaseModel):
    """
    知识库资源的 Pydantic 模型。
    
    用于验证和类型化从 API 返回的知识库数据。
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    coll_name: str
    coll_id: Optional[int] = None
    description: Optional[str] = ""
    is_active: bool
    create_user_id: Optional[int] = None
    create_datetime: datetime
    update_datetime: datetime
