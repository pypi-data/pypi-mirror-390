"""
Payment-related type definitions
"""

from typing import Optional
from typing_extensions import TypedDict

from .common import PaymentStatus, BasePaymentData, RefundInfo, ChargebackInfo


class S2SInput(TypedDict):
    """Server-to-Server payment input"""
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
    card_cvv: str
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class HostedInput(TypedDict):
    """Hosted payment input"""
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
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class APMInput(TypedDict):
    """Alternative Payment Method input"""
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
    redirect_url: str
    webhook_url: Optional[str]
    order_id: Optional[str]
    terminal_id: Optional[str]


class PaymentResponseData(BasePaymentData):
    """Payment response data with refund and chargeback info"""
    refund: RefundInfo
    chargeback: ChargebackInfo


class PaymentResponse(TypedDict):
    """Payment response"""
    status: PaymentStatus
    message: str
    data: PaymentResponseData
    redirect_url: Optional[str]  # Present for REDIRECT status
