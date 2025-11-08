"""Beneficiary service"""

from typing import List, Optional
from ..models.beneficiaries import (
    BeneficiaryDto, CreateBeneficiaryDto, UpdateBeneficiaryDto,
    TransferToBeneficiaryDto
)



class BeneficiaryService:
    """Service for beneficiary operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_beneficiaries(self, beneficiary_type: Optional[str] = None) -> List[BeneficiaryDto]:
        """Get beneficiaries"""
        params = {}
        if beneficiary_type:
            params['type'] = beneficiary_type
            
        response = await self.client._request("GET", "/beneficiaries", params=params)
        return [BeneficiaryDto(**beneficiary) for beneficiary in response['data']]
    
    async def get_beneficiary(self, beneficiary_id: str) -> BeneficiaryDto:
        """Get beneficiary by ID"""
        response = await self.client._request("GET", f"/beneficiaries/{beneficiary_id}")
        return BeneficiaryDto(**response['data'])
    
    async def create_beneficiary(self, request: CreateBeneficiaryDto) -> BeneficiaryDto:
        """Create beneficiary"""
        response = await self.client._request(
            "POST", "/beneficiaries", data=request.dict()
        )
        return BeneficiaryDto(**response['data'])
    
    async def update_beneficiary(self, beneficiary_id: str, request: UpdateBeneficiaryDto) -> BeneficiaryDto:
        """Update beneficiary"""
        response = await self.client._request(
            "PUT", f"/beneficiaries/{beneficiary_id}", data=request.dict(exclude_none=True)
        )
        return BeneficiaryDto(**response['data'])
    
    async def delete_beneficiary(self, beneficiary_id: str) -> None:
        """Delete beneficiary"""
        await self.client._request("DELETE", f"/beneficiaries/{beneficiary_id}")
    
    async def transfer_to_beneficiary(self, request: TransferToBeneficiaryDto) -> dict:
        """Transfer to beneficiary"""
        response = await self.client._request(
            "POST", "/beneficiaries/transfer", data=request.dict()
        )
        return response