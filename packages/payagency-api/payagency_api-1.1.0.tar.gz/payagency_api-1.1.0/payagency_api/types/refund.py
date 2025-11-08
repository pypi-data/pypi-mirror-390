"""
Refund-related type definitions
"""

from typing_extensions import TypedDict

from .common import BasePaymentData, RefundInfo, ChargebackInfo


class RefundInput(TypedDict):
    """Refund input"""
    reason: str
    transaction_id: str


class RefundResponseData(BasePaymentData):
    """Refund response data"""
    refund: RefundInfo
    chargeback: ChargebackInfo


class RefundResponse(TypedDict):
    """Refund response"""
    status: str  # Always "SUCCESS" for successful refunds
    message: str
    data: RefundResponseData
