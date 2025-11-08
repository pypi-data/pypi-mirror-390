"""Solana wallet service"""

from typing import Optional
from ..models.solana import (
    AddressDto, BalanceDto, PortfolioDto, TransferSolDto,
    TransferTokenDto, SignatureDto, SolanaNetwork
)


class SolanaService:
    """Service for Solana wallet operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_wallet_address(self) -> AddressDto:
        """Get Solana wallet address"""
        response = await self.client._request("GET", "/solana/address")
        return AddressDto(**response['data'])
    
    async def get_native_balance(self, network: Optional[SolanaNetwork] = None) -> BalanceDto:
        """Get SOL balance"""
        params = {}
        if network:
            params['network'] = network.value
            
        response = await self.client._request("GET", "/solana/balance", params=params)
        return BalanceDto(**response['data'])
    
    async def get_token_balance(self, token_mint_address: str, network: Optional[SolanaNetwork] = None) -> BalanceDto:
        """Get token balance"""
        params = {}
        if network:
            params['network'] = network.value
            
        response = await self.client._request(
            "GET", f"/solana/token-balance/{token_mint_address}", params=params
        )
        return BalanceDto(**response['data'])
    
    async def get_portfolio(self, network: Optional[SolanaNetwork] = None) -> PortfolioDto:
        """Get Solana portfolio"""
        params = {}
        if network:
            params['network'] = network.value
            
        response = await self.client._request("GET", "/solana/portfolio", params=params)
        return PortfolioDto(**response['data'])
    
    async def transfer_sol(self, request: TransferSolDto) -> SignatureDto:
        """Transfer SOL"""
        response = await self.client._request(
            "POST", "/solana/transfer", data=request.dict()
        )
        return SignatureDto(**response['data'])
    
    async def transfer_token(self, request: TransferTokenDto) -> SignatureDto:
        """Transfer SPL token"""
        response = await self.client._request(
            "POST", "/solana/transfer-token", data=request.dict()
        )
        return SignatureDto(**response['data'])