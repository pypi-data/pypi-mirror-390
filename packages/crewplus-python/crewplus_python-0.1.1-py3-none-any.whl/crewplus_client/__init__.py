# -*- coding: utf-8 -*-
# @create: 2025-10-20
# @update: 2025-10-20
# @desc  : 将核心的 CrewplusClient 类暴露到包的顶层，
#          这样用户就可以通过 from crewplus_client import CrewplusClient 来直接使用。

"""
Crewplus Client SDK

一个用于与 Crewplus API 交互的 Python 客户端库。
"""

__version__ = "0.1.0"

# 从 client 模块导入主客户端类
from .client import CrewPlusClient

# 从 exceptions 模块导入所有公共异常类
from .exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
)

# 定义对外暴露的接口
__all__ = ["CrewPlusClient"]
