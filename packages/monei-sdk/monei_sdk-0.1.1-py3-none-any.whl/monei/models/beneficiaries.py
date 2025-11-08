"""Beneficiary models"""

from typing import Optional, List
from enum import Enum
from .base import BaseDto, BaseModel

class BeneficiaryType(str, Enum):
    BANK = "bank"
    CRYPTO = "crypto"
    PEER = "peer"

class BeneficiaryDto(BaseDto):
    """Beneficiary model"""
    name: str
    type: BeneficiaryType
    accountNumber: Optional[str] = None
    bankCode: Optional[str] = None
    bankName: Optional[str] = None
    email: Optional[str] = None
    evmAddress: Optional[str] = None
    solAddress: Optional[str] = None
    currency: Optional[str] = "NGN"
    isVerified: bool = False

class CreateBeneficiaryDto(BaseModel):
    """Create beneficiary request"""
    name: str
    type: BeneficiaryType
    accountNumber: Optional[str] = None
    bankCode: Optional[str] = None
    bankName: Optional[str] = None
    email: Optional[str] = None
    evmAddress: Optional[str] = None
    solAddress: Optional[str] = None
    currency: Optional[str] = "NGN"

class UpdateBeneficiaryDto(BaseModel):
    """Update beneficiary request"""
    name: Optional[str] = None
    accountNumber: Optional[str] = None
    bankCode: Optional[str] = None
    bankName: Optional[str] = None
    email: Optional[str] = None
    evmAddress: Optional[str] = None
    solAddress: Optional[str] = None
    currency: Optional[str] = None
    type: Optional[BeneficiaryType] = None

class TransferToBeneficiaryDto(BaseModel):
    """Transfer to beneficiary request"""
    beneficiaryId: str
    amount: float
    transactionPin: str
    currency: Optional[str] = "NGN"
    narration: Optional[str] = None

# Bill Payment Beneficiaries
class CreateMobileBeneficiaryDto(BaseModel):
    """Create mobile bill beneficiary"""
    type: str  # "AIRTIME" or "MOBILEDATA"
    name: str
    isFavorite: bool = False
    mobileNumber: str
    mobileOperator: str  # "MTN", "AIRTEL", "GLO", "9MOBILE"

class CreateElectricityBeneficiaryDto(BaseModel):
    """Create electricity bill beneficiary"""
    type: str = "UTILITYBILLS"
    name: str
    isFavorite: bool = False
    meterNumber: str
    electricityProvider: str  # "IKEJA DISCO ELECTRICITY", etc.

class CreateCableTvBeneficiaryDto(BaseModel):
    """Create cable TV beneficiary"""
    type: str = "CABLEBILLS"
    name: str
    isFavorite: bool = False
    smartCardNumber: str
    cableProvider: str  # "DSTV", "GOTV", etc.

class UpdateBillBeneficiaryDto(BaseModel):
    """Update bill beneficiary request"""
    name: Optional[str] = None
    mobileNumber: Optional[str] = None
    mobileOperator: Optional[str] = None
    meterNumber: Optional[str] = None
    electricityProvider: Optional[str] = None
    smartCardNumber: Optional[str] = None
    cableProvider: Optional[str] = None
    isFavorite: Optional[bool] = None