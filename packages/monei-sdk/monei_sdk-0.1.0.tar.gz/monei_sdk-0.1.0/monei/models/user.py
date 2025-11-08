"""User-related models"""

from typing import Optional
from datetime import datetime
from .base import BaseDto
from pydantic import BaseModel

class UserDto(BaseDto):
    """User model"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    name: Optional[str] = None
    email: str
    phone: str
    haveTransactionPin: bool
    verified: bool
    resetToken: Optional[str] = None
    resetTokenExpiry: Optional[int] = None
    dob: Optional[str] = None
    isAdmin: bool
    deviceId: Optional[str] = None
    deviceIp: Optional[str] = None
    deviceModel: Optional[str] = None
    platform: Optional[str] = None
    lastLoggedIn: Optional[str] = None

class UpdateUserDto(BaseModel):
    """Update user request model"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    deviceId: Optional[str] = None
    deviceIp: Optional[str] = None
    deviceModel: Optional[str] = None
    platform: Optional[str] = None

class UserKycInfoDto(BaseDto):
    """KYC information model"""
    verificationStatus: str
    firstName: str
    lastName: str
    gender: str
    dateOfBirth: str
    phoneNo: str
    pixBase64: Optional[str] = None
    kycStatus: str
    verifiedAt: Optional[datetime] = None

class VerifyBvnDto(BaseModel):
    """BVN verification request"""
    bvn: str