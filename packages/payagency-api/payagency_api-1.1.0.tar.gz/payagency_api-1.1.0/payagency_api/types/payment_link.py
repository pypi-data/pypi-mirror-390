"""
Payment Link-related type definitions
"""

from typing import Optional, List
from typing_extensions import TypedDict


class PaymentLinkCreateInput(TypedDict):
    """Payment link creation input"""
    payment_template_id: str
    amount: Optional[int]
    currency: Optional[str]
    expiry_date: Optional[str]
    terminal_id: Optional[str]
    order_id: Optional[str]


class PaymentLinkResponse(TypedDict):
    """Payment link response"""
    message: str
    data: str  # The payment link URL


class PaymentTemplate(TypedDict):
    """Payment template information"""
    template_id: str
    template_name: str
    payment_template_id: str
    template_screenshot: str
    redirect_url: str
    webhook_url: str


class PaymentTemplatesResponse(TypedDict):
    """Payment templates response"""
    data: List[PaymentTemplate]
