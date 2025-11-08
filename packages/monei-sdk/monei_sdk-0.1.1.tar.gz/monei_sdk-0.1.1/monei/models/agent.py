"""AI Agent models"""

from typing import Optional, List
from datetime import datetime
from .base import BaseModel

class ChatMessageDto(BaseModel):
    """Chat message"""
    role: str
    content: str

class AgentChatRequestDto(BaseModel):
    """Agent chat request"""
    message: str
    conversationId: str

class AgentStreamRequestDto(BaseModel):
    """Agent stream request"""
    message: str
    conversationId: str
    chainId: Optional[int] = 56

class GuestAgentRequestDto(BaseModel):
    """Guest agent request"""
    message: str
    chatHistory: Optional[List[ChatMessageDto]] = None

class AgentChatResponseDto(BaseModel):
    """Agent chat response"""
    response: str
    conversationId: str
    title: str

class ConversationListResponseDto(BaseModel):
    """Conversation list item"""
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime
    isPinned: bool
    messageCount: int

class ConversationMessagesResponseDto(BaseModel):
    """Conversation message"""
    id: str
    role: str
    content: str
    createdAt: datetime

class CreateConversationDto(BaseModel):
    """Create conversation request"""
    id: str

class PinConversationDto(BaseModel):
    """Pin conversation request"""
    pin: bool