"""EVM wallet models"""

from typing import Optional, List
from .base import BaseModel

class BalanceDto(BaseModel):
    """Balance model"""
    balance: str

class UserTokenBalanceDto(BaseModel):
    """Token balance model"""
    contractAddress: str
    name: str
    symbol: str
    decimals: int
    logoUrl: Optional[str] = None
    type: str  # "native" or "token"
    balance: str
    balanceUSD: str
    priceUSD: str
    rawBalance: str
    network: str

class UserEvmPortfolioDto(BaseModel):
    """EVM portfolio model"""
    userId: str
    walletAddress: str
    network: str
    totalPortfolioValueUSD: str
    nativeToken: UserTokenBalanceDto
    tokens: List[UserTokenBalanceDto]
    updatedAt: str

class SendNativeTokenDto(BaseModel):
    """Send native token request"""
    to: str
    amount: str
    chainId: int

class SendTokenDto(BaseModel):
    """Send ERC20 token request"""
    to: str
    tokenAddress: str
    amount: str
    chainId: int

class Response(BaseModel):
    """Transaction response"""
    txHash: str