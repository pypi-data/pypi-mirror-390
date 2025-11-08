"""
Cryptocurrency-related type definitions
"""

from typing import Optional, List, Literal
from typing_extensions import TypedDict

from .common import PaymentStatus, CustomerInfo, BasePaymentData
from .payment_link import PaymentLinkResponse


TransactionType = Literal["ONRAMP", "OFFRAMP", "PAYIN"]


class CryptoPaymentInput(TypedDict):
    """Crypto payment input (unified for OnRamp/OffRamp)"""
    transaction_type: TransactionType
    first_name: str
    last_name: str
    email: str
    phone_number: str
    fiat_amount: Optional[int]  # Required for ONRAMP, omit for OFFRAMP
    crypto_amount: Optional[str]  # Required for OFFRAMP, omit for ONRAMP
    fiat_currency: str
    crypto_currency: str
    wallet_address: str
    ip_address: str
    country: str
    crypto_network: str
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class CryptoPaymentLinkInput(TypedDict):
    """Crypto payment link input (unified for OnRamp/OffRamp/PayIn)"""
    transaction_type: TransactionType
    fiat_amount: Optional[int]  # Required for ONRAMP and PAYIN
    crypto_amount: Optional[str]  # Required for OFFRAMP
    fiat_currency: str
    crypto_currency: str
    payment_template_id: str
    order_id: Optional[str]
    terminal_id: Optional[str]
    expiry_date: Optional[str]


class CryptoOnRampInput(TypedDict):
    """OnRamp (Fiat to Crypto) input"""
    first_name: str
    last_name: str
    email: str
    phone_number: str
    fiat_amount: int
    fiat_currency: str
    crypto_currency: str
    wallet_address: str
    ip_address: str
    country: str
    crypto_network: str
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class CryptoOffRampInput(TypedDict):
    """OffRamp (Crypto to Fiat) input"""
    first_name: str
    last_name: str
    email: str
    phone_number: str
    fiat_currency: str
    crypto_currency: str
    crypto_amount: str
    wallet_address: str
    ip_address: str
    country: str
    crypto_network: str
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class CryptoPayinInput(TypedDict):
    """Crypto PayIn input"""
    first_name: str
    last_name: str
    email: str
    address: str
    phone_number: str
    ip_address: str
    crypto_currency: str
    amount: int
    currency: str
    crypto_network: str
    country: str
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class CryptoOnRampLinkInput(TypedDict):
    """OnRamp link input"""
    fiat_amount: int
    fiat_currency: str
    crypto_currency: str
    payment_template_id: str
    order_id: Optional[str]
    terminal_id: Optional[str]
    expiry_date: Optional[str]


class CryptoOffRampLinkInput(TypedDict):
    """OffRamp link input"""
    fiat_currency: str
    crypto_currency: str
    crypto_amount: str
    payment_template_id: str
    order_id: Optional[str]
    terminal_id: Optional[str]
    expiry_date: Optional[str]


class CryptoPayinLinkInput(TypedDict):
    """PayIn link input"""
    fiat_amount: int
    fiat_currency: str
    crypto_currency: str
    payment_template_id: str
    order_id: Optional[str]
    terminal_id: Optional[str]
    expiry_date: Optional[str]


class CryptoCurrenciesInput(TypedDict):
    """Crypto currencies input"""
    country: str  # ISO 3166-1 alpha-2 country code
    amount: int


class CryptoCurrency(TypedDict):
    """Crypto currency information"""
    name: str
    code: str
    symbol: str


class CryptoCurrenciesResponse(TypedDict):
    """Crypto currencies response"""
    message: str
    data: List[CryptoCurrency]


class CryptoPaymentResponseData(TypedDict):
    """Crypto payment response data"""
    transaction_id: str
    fiat: str
    fiat_amount: int
    crypto: str
    crypto_amount: int
    customer: CustomerInfo


class CryptoPaymentResponse(TypedDict):
    """Crypto payment response (OnRamp/OffRamp)"""
    status: PaymentStatus
    message: str
    redirect_url: Optional[str]
    data: CryptoPaymentResponseData


class CryptoPayinResponseData(BasePaymentData):
    """Crypto PayIn response data"""
    crypto_currency: str


class CryptoPayinResponse(TypedDict):
    """Crypto PayIn response"""
    status: PaymentStatus
    message: str
    redirect_url: Optional[str]
    data: CryptoPayinResponseData
