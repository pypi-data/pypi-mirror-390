"""Wallet-related models"""

from typing import Optional, List, Dict, Any

from pydantic import BaseModel
from .base import BaseDto

class SubWalletDto(BaseDto):
    """Sub-wallet model"""
    parentWalletId: str
    type: str  # "FIAT" or "CRYPTO"
    currency: str
    balance: float
    chain: Optional[str] = None
    publicAddress: Optional[str] = None
    evmPortfolio: Optional[Dict[str, Any]] = None
    solPortfolio: Optional[Dict[str, Any]] = None

class UserWalletDto(BaseModel):
    """User wallet model"""
    nairaBalance: float
    evmPortfolio: Optional[Dict[str, Any]] = None
    solPortfolio: Optional[Dict[str, Any]] = None
    subwallets: List[SubWalletDto]

class FundWalletByNairaDto(BaseModel):
    """Fund wallet request"""
    amount: float

class DepositResponseDto(BaseModel):
    """Deposit response"""
    link: str

class WithdrawWalletDto(BaseModel):
    """Withdraw to bank request"""
    amount: float
    bank: str
    accountNumber: str
    transactionPin: str
    currency: Optional[str] = "NGN"
    narration: Optional[str] = None

class PeerTransferDto(BaseModel):
    """Peer transfer request"""
    receiver: str
    amount: float
    transactionPin: str
    currency: Optional[str] = "NGN"

class BankDto(BaseModel):
    """Bank model"""
    swiftCode: Optional[str] = None
    bic: Optional[str] = None
    isMobileVerified: Optional[bool] = None
    isCashPickUp: bool
    nibssCode: str
    id: str
    code: str
    name: str
    branches: List[List[Any]]

class BankAccountDto(BaseModel):
    """Bank account model"""
    accountName: str
    accountNumber: str
    bankCode: str
    bankName: str

class VerifyBankAccountRequestDto(BaseModel):
    """Bank account verification request"""
    accountNumber: str
    bank: str