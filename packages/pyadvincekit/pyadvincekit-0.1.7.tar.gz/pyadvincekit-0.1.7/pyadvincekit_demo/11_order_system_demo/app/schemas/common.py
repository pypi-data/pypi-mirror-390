"""
通用Pydantic模型

定义通用的请求和响应模型。
"""

from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field

DataType = TypeVar('DataType')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")


class PaginatedResponse(BaseModel, Generic[DataType]):
    """分页响应模型"""
    items: List[DataType] = Field(description="数据列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")
    
    @classmethod
    def create(
        cls,
        items: List[DataType],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[DataType]":
        """创建分页响应"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[str] = Field(description="要删除的ID列表")


class MessageResponse(BaseModel):
    """消息响应"""
    message: str = Field(description="响应消息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok", description="状态")
    timestamp: str = Field(description="时间戳")
    version: str = Field(description="版本号")
    database: str = Field(description="数据库状态")














