"""EVM wallet service"""

from typing import Dict, Any
from ..models.evm import (
    BalanceDto, UserEvmPortfolioDto, SendNativeTokenDto,
    SendTokenDto, Response
)


class EvmService:
    """Service for EVM wallet operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_native_balance(self, chain_id: int) -> BalanceDto:
        """Get native token balance"""
        params = {'chainId': chain_id}
        response = await self.client._request("GET", "/evm/balance/native", params=params)
        return BalanceDto(**response['data'])
    
    async def get_token_balance(self, token_address: str, chain_id: int) -> BalanceDto:
        """Get ERC20 token balance"""
        params = {
            'tokenAddress': token_address,
            'chainId': chain_id
        }
        response = await self.client._request("GET", "/evm/balance/token", params=params)
        return BalanceDto(**response['data'])
    
    async def get_portfolio(self, chain_id: int) -> UserEvmPortfolioDto:
        """Get EVM portfolio"""
        response = await self.client._request("GET", f"/evm/portfolio/{chain_id}")
        return UserEvmPortfolioDto(**response['data'])
    
    async def send_native_token(self, request: SendNativeTokenDto) -> Response:
        """Send native token"""
        response = await self.client._request(
            "POST", "/evm/send/native", data=request.dict()
        )
        return Response(**response['data'])
    
    async def send_token(self, request: SendTokenDto) -> Response:
        """Send ERC20 token"""
        response = await self.client._request(
            "POST", "/evm/send/token", data=request.dict()
        )
        return Response(**response['data'])