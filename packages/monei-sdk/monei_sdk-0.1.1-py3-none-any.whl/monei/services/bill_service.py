"""Bill payment service"""

from typing import List, Optional
from ..models.bills import (
    BillerDto, ValidateBillDto, AirtimePurchaseDto, DataPurchaseDto,
    ElectricityPaymentDto, CableTvPaymentDto, BillPaymentDto, BillDto,
    BillCategory
)
from ..models.beneficiaries import (
    CreateMobileBeneficiaryDto, CreateElectricityBeneficiaryDto,
    CreateCableTvBeneficiaryDto, UpdateBillBeneficiaryDto
)


class BillService:
    """Service for bill payment operations"""
    
    def __init__(self, client):
        self.client = client
    
    async def get_biller_items(self, category: BillCategory, biller_name: str) -> List[BillerDto]:
        """Get biller items"""
        response = await self.client._request(
            "GET", f"/bills/get-biller-items/{category.value}/{biller_name}"
        )
        return [BillerDto(**item) for item in response['data']]
    
    async def validate_bill(self, item_code: str, customer: str) -> dict:
        """Validate bill information"""
        request_data = ValidateBillDto(itemCode=item_code, customer=customer)
        response = await self.client._request(
            "POST", "/bills/validate", data=request_data.dict()
        )
        return response
    
    async def buy_airtime(self, request: AirtimePurchaseDto) -> BillPaymentDto:
        """Buy airtime"""
        response = await self.client._request(
            "POST", "/bills/buy-airtime", data=request.dict()
        )
        return BillPaymentDto(**response['data'])
    
    async def buy_data(self, request: DataPurchaseDto) -> BillPaymentDto:
        """Buy mobile data"""
        response = await self.client._request(
            "POST", "/bills/buy-mobile-data", data=request.dict()
        )
        return BillPaymentDto(**response['data'])
    
    async def buy_electricity(self, request: ElectricityPaymentDto) -> BillPaymentDto:
        """Pay electricity bill"""
        response = await self.client._request(
            "POST", "/bills/buy-electricity", data=request.dict()
        )
        return BillPaymentDto(**response['data'])
    
    async def subscribe_cable_tv(self, request: CableTvPaymentDto) -> BillPaymentDto:
        """Subscribe to cable TV"""
        response = await self.client._request(
            "POST", "/bills/subscribe-cable-tv", data=request.dict()
        )
        return BillPaymentDto(**response['data'])
    
    async def get_bill_history(self) -> List[BillDto]:
        """Get bill payment history"""
        response = await self.client._request("GET", "/bills/history")
        return [BillDto(**bill) for bill in response['data']]
    
    async def get_bill_beneficiaries(self, category: Optional[str] = None) -> List[dict]:
        """Get bill beneficiaries"""
        params = {}
        if category:
            params['category'] = category
            
        response = await self.client._request("GET", "/bill-beneficiaries", params=params)
        return response['data']
    
    async def get_favourite_bill_beneficiaries(self) -> List[dict]:
        """Get favourite bill beneficiaries"""
        response = await self.client._request("GET", "/bill-beneficiaries/favorites")
        return response['data']
    
    async def create_mobile_beneficiary(self, request: CreateMobileBeneficiaryDto) -> dict:
        """Create mobile bill beneficiary"""
        response = await self.client._request(
            "POST", "/bill-beneficiaries/mobile", data=request.dict()
        )
        return response['data']
    
    async def create_electricity_beneficiary(self, request: CreateElectricityBeneficiaryDto) -> dict:
        """Create electricity bill beneficiary"""
        response = await self.client._request(
            "POST", "/bill-beneficiaries/electricity", data=request.dict()
        )
        return response['data']
    
    async def create_cabletv_beneficiary(self, request: CreateCableTvBeneficiaryDto) -> dict:
        """Create cable TV beneficiary"""
        response = await self.client._request(
            "POST", "/bill-beneficiaries/cable-tv", data=request.dict()
        )
        return response['data']
    
    async def delete_bill_beneficiary(self, beneficiary_id: str) -> None:
        """Delete bill beneficiary"""
        await self.client._request("DELETE", f"/bill-beneficiaries/{beneficiary_id}")