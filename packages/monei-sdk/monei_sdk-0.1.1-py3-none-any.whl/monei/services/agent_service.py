"""AI Agent service"""

from typing import List, Optional
from ..models.agent import (
    AgentChatRequestDto, AgentStreamRequestDto, GuestAgentRequestDto,
    AgentChatResponseDto, ConversationListResponseDto,
    ConversationMessagesResponseDto, CreateConversationDto, PinConversationDto
)


class AgentService:
    """Service for AI agent operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_conversations(self) -> List[ConversationListResponseDto]:
        """Get all conversations"""
        response = await self.client._request("GET", "/agent/conversations")
        return [ConversationListResponseDto(**conv) for conv in response]
    
    async def chat(self, request: AgentChatRequestDto) -> AgentChatResponseDto:
        """Chat with AI agent"""
        response = await self.client._request(
            "POST", "/agent/conversations", data=request.dict()
        )
        return AgentChatResponseDto(**response)
    
    async def get_conversation_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[ConversationMessagesResponseDto]:
        """Get conversation messages"""
        params = {}
        if limit:
            params['limit'] = limit
            
        response = await self.client._request(
            "GET", f"/agent/conversations/{conversation_id}/messages", params=params
        )
        return [ConversationMessagesResponseDto(**msg) for msg in response]
    
    async def initialize_conversation(self, conversation_id: str) -> dict:
        """Initialize conversation"""
        request_data = CreateConversationDto(id=conversation_id)
        response = await self.client._request(
            "POST", "/agent/conversations/init-conversation", data=request_data.dict()
        )
        return response
    
    async def delete_conversation(self, conversation_id: str) -> None:
        """Delete conversation"""
        await self.client._request("DELETE", f"/agent/conversations/{conversation_id}")
    
    async def pin_conversation(self, conversation_id: str, pin: bool) -> None:
        """Pin/unpin conversation"""
        request_data = PinConversationDto(pin=pin)
        await self.client._request(
            "PATCH", f"/agent/conversations/{conversation_id}/pin", data=request_data.dict()
        )
    
    async def stream_chat(self, request: AgentStreamRequestDto) -> dict:
        """Stream chat with AI agent"""
        # Note: This would need special handling for SSE streams
        response = await self.client._request(
            "POST", "/agent/conversations/stream", data=request.dict()
        )
        return response
    
    async def guest_chat_stream(self, request: GuestAgentRequestDto) -> dict:
        """Guest chat stream"""
        # Note: This would need special handling for SSE streams
        response = await self.client._request(
            "POST", "/guest-agent/stream", data=request.dict()
        )
        return response