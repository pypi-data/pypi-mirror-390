"""Wallet service implementation"""

from typing import Dict, Any, List, Optional
from ..models.wallet import (
    UserWalletDto, FundWalletByNairaDto, DepositResponseDto,
    WithdrawWalletDto, PeerTransferDto, BankDto, BankAccountDto,
    VerifyBankAccountRequestDto
)
from ..exceptions import MoneiAPIError


class WalletService:
    """Service for wallet operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_wallet(self, chain_id: Optional[int] = None) -> UserWalletDto:
        """Get wallet information"""
        params = {}
        if chain_id:
            params['chainId'] = chain_id
            
        response = await self.client._request("GET", "/wallet/me", params=params)
        return UserWalletDto(**response['data'])
    
    async def fund_wallet(self, amount: float) -> DepositResponseDto:
        """Fund wallet with Naira"""
        request_data = FundWalletByNairaDto(amount=amount)
        response = await self.client._request(
            "POST", "/wallet/user/fund-wallet", data=request_data.dict()
        )
        return DepositResponseDto(**response['data'])
    
    async def withdraw_to_bank(self, request: WithdrawWalletDto) -> Dict[str, Any]:
        """Withdraw to bank account"""
        response = await self.client._request(
            "POST", "/wallet/withdrawals", data=request.dict()
        )
        return response
    
    async def peer_transfer(self, request: PeerTransferDto) -> Dict[str, Any]:
        """Transfer to another user"""
        response = await self.client._request(
            "POST", "/wallet/peer-transfer", data=request.dict()
        )
        return response
    
    async def get_banks(self) -> List[BankDto]:
        """Get available banks"""
        response = await self.client._request("GET", "/wallet/get-banks")
        return [BankDto(**bank) for bank in response['data']]
    
    async def verify_bank_account(self, account_number: str, bank: str) -> BankAccountDto:
        """Verify bank account"""
        request_data = VerifyBankAccountRequestDto(
            accountNumber=account_number, bank=bank
        )
        response = await self.client._request(
            "POST", "/wallet/verify-bank-account", data=request_data.dict()
        )
        return BankAccountDto(**response['data'])