"""Solana wallet models"""

from typing import Optional, List
from enum import Enum
from .base import BaseModel

class SolanaNetwork(str, Enum):
    MAINNET_BETA = "mainnet-beta"
    DEVNET = "devnet"
    TESTNET = "testnet"

class BalanceDto(BaseModel):
    """Balance model"""
    balance: str

class AddressDto(BaseModel):
    """Wallet address"""
    address: str

class TokenInfoDto(BaseModel):
    """Token information"""
    mintAddress: str
    name: str
    symbol: str
    balance: str
    rawBalance: str
    decimals: int
    priceUsd: float
    valueUsd: float

class PortfolioDto(BaseModel):
    """Solana portfolio"""
    userId: str
    address: str
    nativeBalance: str
    nativeBalanceLamports: str
    nativeBalanceUsd: float
    tokens: List[TokenInfoDto]
    totalValueUsd: float

class TransferSolDto(BaseModel):
    """Transfer SOL request"""
    to: str
    amount: str
    network: Optional[SolanaNetwork] = SolanaNetwork.MAINNET_BETA

class TransferTokenDto(BaseModel):
    """Transfer SPL token request"""
    to: str
    tokenMintAddress: str
    amount: str
    network: Optional[SolanaNetwork] = SolanaNetwork.MAINNET_BETA

class SignatureDto(BaseModel):
    """Transaction signature"""
    signature: str