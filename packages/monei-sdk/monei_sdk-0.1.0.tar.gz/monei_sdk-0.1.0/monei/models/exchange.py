"""Exchange models"""

from typing import Optional
from .base import BaseModel

class SwapNativeToTokenDto(BaseModel):
    """Swap native to token request"""
    amount: str
    tokenOut: str
    chainId: int

class SwapTokenToTokenDto(BaseModel):
    """Swap token to token request"""
    inputMint: str
    outputMint: str
    amount: float
    slippageBps: Optional[int] = None

class SwapTokenToNativeDto(BaseModel):
    """Swap token to native request"""
    amount: str
    tokenIn: str
    chainId: int

class SwapSolToTokenDto(BaseModel):
    """Swap SOL to token request"""
    outputMint: str
    amount: float
    slippageBps: Optional[int] = None

class ZeroExQuoteDto(BaseModel):
    """0x quote response"""
    permit2: Optional[dict] = None
    transaction: dict

class SwapDto(BaseModel):
    """Swap response"""
    signature: str
    txUrl: str

class TxHashDto(BaseModel):
    """Transaction hash"""
    txHash: str