"""
Common type definitions
"""

from typing import Literal, Optional, Dict, Any
from typing_extensions import TypedDict


Environment = Literal["test", "live"]
PaymentStatus = Literal["SUCCESS", "REDIRECT", "FAILED", "PENDING", "BLOCKED"]


class CustomerInfo(TypedDict):
    """Customer information"""
    first_name: str
    last_name: str  
    email: str


class RefundInfo(TypedDict):
    """Refund information"""
    status: bool
    refund_date: Optional[str]


class ChargebackInfo(TypedDict):
    """Chargeback information"""
    status: bool
    chargeback_date: Optional[str]


class BasePaymentData(TypedDict):
    """Base payment data structure"""
    amount: int
    currency: str
    order_id: Optional[str]
    transaction_id: str
    customer: CustomerInfo
