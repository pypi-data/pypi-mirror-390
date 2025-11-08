# Monei Python SDK

The official Python SDK for Monei API - providing seamless integration with Monei's comprehensive financial services including wallets, crypto transactions, bill payments, and AI agent.

## Installation

```bash
pip install monei-sdk
```

## Quick Start

```python
import asyncio
import os
from monei import MoneiClient

async def main():
    # Initialize client with API key
    client = MoneiClient(api_key=os.getenv('MONEI_API_KEY'))
    
    try:
        # Get user info
        user = await client.user.get_me()
        print(f"Welcome {user.firstName} {user.lastName}!")
        
        # Get wallet balance
        wallet = await client.wallet.get_wallet()
        print(f"Naira Balance: ₦{wallet.nairaBalance:,.2f}")
        
    finally:
        await client.close()

asyncio.run(main())
```

## Features

- **User Management** - Profile, KYC verification
- **Wallet Operations** - Balance, funding, withdrawals, peer transfers
- **EVM Wallets** - Ethereum, BSC, Polygon support
- **Solana Wallets** - SOL and SPL token management
- **Bill Payments** - Airtime, data, electricity, cable TV
- **Crypto Exchange** - Token swaps on EVM and Solana
- **AI Agent** - Conversational banking assistant
- **Beneficiary Management** - Bank, crypto, and peer beneficiaries

## Basic Usage Examples

### 1. Wallet Operations

```python
from monei import MoneiClient
from monei.models.wallet import PeerTransferDto

async def wallet_operations():
    async with MoneiClient(api_key="your-api-key") as client:
        # Fund wallet
        fund_result = await client.wallet.fund_wallet(5000.0)
        print(f"Funding link: {fund_result.link}")
        
        # Peer transfer
        transfer = PeerTransferDto(
            receiver="user@example.com",
            amount=1000.0,
            transactionPin="1234"
        )
        result = await client.wallet.peer_transfer(transfer)
        print("Transfer successful!")
```

### 2. Crypto Operations

```python
from monei.models.evm import SendNativeTokenDto

async def crypto_operations():
    async with MoneiClient(api_key="your-api-key") as client:
        # Get EVM portfolio
        portfolio = await client.evm.get_portfolio(chain_id=56)  # BSC
        print(f"Portfolio value: ${portfolio.totalPortfolioValueUSD}")
        
        # Send crypto
        transfer = SendNativeTokenDto(
            to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            amount="0.01",
            chainId=1  # Ethereum
        )
        result = await client.evm.send_native_token(transfer)
        print(f"Transaction hash: {result.txHash}")
```

### 3. Bill Payments

```python
from monei.models.bills import AirtimePurchaseDto

async def bill_payments():
    async with MoneiClient(api_key="your-api-key") as client:
        # Buy airtime
        airtime = AirtimePurchaseDto(
            phoneNumber="08012345678",
            biller="MTN",
            amount=500.0
        )
        result = await client.bills.buy_airtime(airtime)
        print(f"Airtime purchase successful! Reference: {result.reference}")
```

### 4. AI Agent

```python
from monei.models.agent import AgentChatRequestDto

async def ai_agent():
    async with MoneiClient(api_key="your-api-key") as client:
        # Chat with AI agent
        chat_request = AgentChatRequestDto(
            message="What's my current account balance?",
            conversationId="conv_123"
        )
        response = await client.agent.chat(chat_request)
        print(f"Agent: {response.response}")
```

## Authentication

Get your API key from the [Monei Dashboard](https://monei.cc).

```python
# Use environment variable (recommended)
client = MoneiClient(api_key=os.getenv('MONEI_API_KEY'))

# Or pass directly
client = MoneiClient(api_key="your-api-key-here")
```

## Error Handling

```python
from monei import MoneiAPIError, AuthenticationError

try:
    async with MoneiClient(api_key="invalid-key") as client:
        await client.user.get_me()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except MoneiAPIError as e:
    print(f"API error: {e}")
```

## Getting Help

- **Documentation**: [https://goviral-ai-lab.gitbook.io/monei-api-gateway-docs/default](https://goviral-ai-lab.gitbook.io/monei-api-gateway-docs/)
- **API Reference**: [https://api.monei.cc/api-gateway-docs](https://api.monei.cc/api-gateway-docs)
- **Support**: tech@monei.cc

## License

MIT License - see LICENSE file for details.