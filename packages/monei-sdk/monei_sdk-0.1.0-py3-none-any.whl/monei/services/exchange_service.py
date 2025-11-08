"""Exchange service"""

from ..models.exchange import (
    SwapNativeToTokenDto, SwapTokenToTokenDto, SwapTokenToNativeDto,
    SwapSolToTokenDto, ZeroExQuoteDto, SwapDto, TxHashDto
)


class ExchangeService:
    """Service for exchange operations"""
    
    def __init__(self, client):
        self.client = client
    
    # EVM Exchange
    async def get_swap_native_to_token_quote(self, request: SwapNativeToTokenDto) -> ZeroExQuoteDto:
        """Get quote for native to token swap"""
        response = await self.client._request(
            "POST", "/evm-exchange/quote/native-to-token", data=request.dict()
        )
        return ZeroExQuoteDto(**response['data'])
    
    async def swap_native_to_token(self, request: SwapNativeToTokenDto) -> TxHashDto:
        """Swap native to token"""
        response = await self.client._request(
            "POST", "/evm-exchange/native-to-token", data=request.dict()
        )
        return TxHashDto(**response['data'])
    
    async def get_swap_token_to_token_quote(self, request: SwapTokenToTokenDto) -> ZeroExQuoteDto:
        """Get quote for token to token swap"""
        response = await self.client._request(
            "POST", "/evm-exchange/quote/token-to-token", data=request.dict()
        )
        return ZeroExQuoteDto(**response['data'])
    
    async def swap_token_to_token(self, request: SwapTokenToTokenDto) -> TxHashDto:
        """Swap token to token"""
        response = await self.client._request(
            "POST", "/evm-exchange/token-to-token", data=request.dict()
        )
        return TxHashDto(**response['data'])
    
    # Solana Exchange
    async def get_swap_quote(self, input_mint: str, output_mint: str, amount: float) -> dict:
        """Get Solana swap quote"""
        params = {
            'inputMint': input_mint,
            'outputMint': output_mint,
            'amount': amount
        }
        response = await self.client._request("GET", "/solana-exchange/quote", params=params)
        return response
    
    async def swap_sol_to_token(self, request: SwapSolToTokenDto) -> SwapDto:
        """Swap SOL to token"""
        response = await self.client._request(
            "POST", "/solana-exchange/swap-sol-to-token", data=request.dict()
        )
        return SwapDto(**response['data'])
    
    async def swap_token_to_token_solana(self, request: SwapTokenToTokenDto) -> SwapDto:
        """Swap token to token on Solana"""
        response = await self.client._request(
            "POST", "/solana-exchange/swap-token-to-token", data=request.dict()
        )
        return SwapDto(**response['data'])
    
    async def swap_token_to_sol(self, request: SwapSolToTokenDto) -> SwapDto:
        """Swap token to SOL"""
        response = await self.client._request(
            "POST", "/solana-exchange/swap-token-to-sol", data=request.dict()
        )
        return SwapDto(**response['data'])