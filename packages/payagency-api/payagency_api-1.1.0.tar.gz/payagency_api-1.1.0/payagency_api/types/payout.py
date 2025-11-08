"""
Payout-related type definitions
"""

from typing import Optional, List, Literal
from typing_extensions import TypedDict

from .common import PaymentStatus, BasePaymentData


class PayoutInput(TypedDict):
    """Payout input"""
    wallet_id: str
    first_name: str
    last_name: str
    email: str
    address: str
    country: str
    city: str
    state: str
    zip: str
    ip_address: str
    phone_number: str
    amount: int
    currency: str
    card_number: str
    card_expiry_month: str
    card_expiry_year: str
    webhook_url: Optional[str]
    order_id: Optional[str]


class PayoutResponse(TypedDict):
    """Payout response"""
    status: PaymentStatus
    message: str
    data: BasePaymentData
    redirect_url: Optional[str]


class WalletInfo(TypedDict):
    """Wallet information"""
    wallet_id: str
    currency: str
    amount: int
    payment_method: str
    status: Literal["Active", "Inactive"]


class WalletsResponse(TypedDict):
    """Wallets response"""
    data: List[WalletInfo]


class EstimateFeeInput(TypedDict):
    """Estimate fee input"""
    wallet_id: str
    amount: int
    card_number: str


class EstimateFeeData(TypedDict):
    """Estimate fee response data"""
    amount_required: int
    wallet_balance: int
    total_fee: int


class EstimateFeeResponse(TypedDict):
    """Estimate fee response"""
    data: EstimateFeeData


class PayoutStatusResponse(TypedDict):
    """Payout status response"""
    status: PaymentStatus
    message: str
    data: BasePaymentData
