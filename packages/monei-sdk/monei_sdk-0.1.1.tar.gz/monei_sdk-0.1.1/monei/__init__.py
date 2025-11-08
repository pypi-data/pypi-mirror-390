"""
MrMonei Python SDK
"""

from .client import MoneiClient
from .exceptions import (
    MoneiAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    InsufficientBalanceError,
)

# Import models
from .models.user import UserDto, UpdateUserDto, UserKycInfoDto, VerifyBvnDto
from .models.wallet import (
    UserWalletDto, FundWalletByNairaDto, DepositResponseDto,
    WithdrawWalletDto, PeerTransferDto, BankDto, BankAccountDto
)
from .models.evm import (
    BalanceDto, UserEvmPortfolioDto, SendNativeTokenDto,
    SendTokenDto, Response
)
from .models.solana import (
    AddressDto, PortfolioDto, TransferSolDto, TransferTokenDto,
    SignatureDto, SolanaNetwork
)
from .models.transactions import TransactionResponseDto, TransactionDto
from .models.bills import (
    BillerDto, AirtimePurchaseDto, DataPurchaseDto,
    ElectricityPaymentDto, CableTvPaymentDto, BillPaymentDto, BillDto, BillCategory
)
from .models.exchange import (
    SwapNativeToTokenDto, SwapTokenToTokenDto, SwapTokenToNativeDto,
    SwapSolToTokenDto, ZeroExQuoteDto, SwapDto, TxHashDto
)
from .models.agent import (
    AgentChatRequestDto, AgentStreamRequestDto, GuestAgentRequestDto,
    AgentChatResponseDto, ConversationListResponseDto,
    ConversationMessagesResponseDto, CreateConversationDto, PinConversationDto
)

from .models.beneficiaries import (
    BeneficiaryDto, CreateBeneficiaryDto, UpdateBeneficiaryDto,
    TransferToBeneficiaryDto, BeneficiaryType,
    CreateMobileBeneficiaryDto, CreateElectricityBeneficiaryDto,
    CreateCableTvBeneficiaryDto, UpdateBillBeneficiaryDto
)

__version__ = "0.1.0"
__all__ = [
    "MoneiClient",
    "MoneiAPIError",
    "AuthenticationError", 
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "InsufficientBalanceError",
    # Models
    "UserDto", "UpdateUserDto", "UserKycInfoDto", "VerifyBvnDto",
    "UserWalletDto", "FundWalletByNairaDto", "DepositResponseDto",
    "WithdrawWalletDto", "PeerTransferDto", "BankDto", "BankAccountDto",
    "BalanceDto", "UserEvmPortfolioDto", "SendNativeTokenDto",
    "SendTokenDto", "Response",
    "AddressDto", "PortfolioDto", "TransferSolDto", "TransferTokenDto",
    "SignatureDto", "SolanaNetwork",
    "TransactionResponseDto", "TransactionDto",
    "BillerDto", "AirtimePurchaseDto", "DataPurchaseDto",
    "ElectricityPaymentDto", "CableTvPaymentDto", "BillPaymentDto", "BillDto", "BillCategory",
    "SwapNativeToTokenDto", "SwapTokenToTokenDto", "SwapTokenToNativeDto",
    "SwapSolToTokenDto", "ZeroExQuoteDto", "SwapDto", "TxHashDto",
    "AgentChatRequestDto", "AgentStreamRequestDto", "GuestAgentRequestDto",
    "AgentChatResponseDto", "ConversationListResponseDto",
    "ConversationMessagesResponseDto", "CreateConversationDto", "PinConversationDto"
    "BeneficiaryDto", "CreateBeneficiaryDto", "UpdateBeneficiaryDto",
    "TransferToBeneficiaryDto", "BeneficiaryType",
    "CreateMobileBeneficiaryDto", "CreateElectricityBeneficiaryDto", 
    "CreateCableTvBeneficiaryDto", "UpdateBillBeneficiaryDto"
]