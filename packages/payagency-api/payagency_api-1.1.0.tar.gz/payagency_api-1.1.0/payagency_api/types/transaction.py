"""
Transaction-related type definitions
"""

from typing import Optional, List
from typing_extensions import TypedDict


class TransactionsInput(TypedDict, total=False):
    """Transactions query input"""
    transaction_start_date: Optional[str]
    transaction_end_date: Optional[str]
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class MerchantConnector(TypedDict):
    """Merchant connector information"""
    name: str


class UserKyc(TypedDict):
    """User KYC information"""
    name: str


class User(TypedDict):
    """User information"""
    name: str
    user_kyc: UserKyc


class TransactionInfo(TypedDict):
    """Transaction information"""
    first_name: str
    last_name: str
    converted_amount: str
    converted_currency: str
    transaction_id: str
    amount: str
    currency: str
    status: str
    card_type: Optional[str]
    card_number: Optional[str]
    transaction_type: str
    order_id: Optional[str]
    country: str
    email: str
    created_at: str
    transaction_date: str
    chargeback_date: Optional[str]
    refund_date: Optional[str]
    suspicious_date: Optional[str]
    merchant_connector: MerchantConnector
    user: User


class TransactionMeta(TypedDict):
    """Transaction pagination metadata"""
    hasNextPage: bool
    hasPreviousPage: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]
    totatCount: int


class TransactionsResponse(TypedDict):
    """Transactions response"""
    message: str
    data: List[TransactionInfo]
    meta: TransactionMeta
