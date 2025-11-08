"""User service implementation"""

from typing import Dict, Any
from ..models.user import UserDto, UpdateUserDto, UserKycInfoDto, VerifyBvnDto
from ..exceptions import MoneiAPIError


class UserService:
    """Service for user operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_me(self) -> UserDto:
        """Get current user information"""
        response = await self.client._request("GET", "/user/me")
        return UserDto(**response['data'])
    
    async def update(self, user_id: str, update_data: UpdateUserDto) -> UserDto:
        """Update user information"""
        response = await self.client._request(
            "PATCH", f"/user/update/{user_id}", data=update_data.dict(exclude_none=True)
        )
        return UserDto(**response['data'])
    
    async def kyc_verify_bvn(self, bvn: str) -> UserKycInfoDto:
        """Verify BVN for KYC"""
        request_data = VerifyBvnDto(bvn=bvn)
        response = await self.client._request(
            "POST", "/wallet/kyc/bvn", data=request_data.dict()
        )
        return UserKycInfoDto(**response['data'])