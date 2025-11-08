"""Base models for MrMonei SDK"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T')

class APIResponse(BaseModel):
    """Base response model for all API responses"""
    statusCode: int
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    """Base model for paginated responses"""
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool

class BaseDto(BaseModel):
    """Base DTO with common fields"""
    id: str
    createdAt: datetime
    updatedAt: datetime
    deletedDate: Optional[datetime] = None