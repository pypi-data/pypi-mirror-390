"""
Main PayAgency API client
"""

import requests
from typing import Dict, Any, Optional

from .exceptions import PayAgencyAPIError, PayAgencyNetworkError
from .utils import validate_config, get_environment, normalize_base_url, prepare_request_data
from .modules.payment import Payment
from .modules.payout import Payout  
from .modules.payment_link import PaymentLink
from .modules.crypto import Crypto
from .modules.transaction import Transaction
from .modules.refund import Refund
from .types.refund import RefundInput, RefundResponse


class PayAgencyApi:
    """
    Main PayAgency API client
    
    Args:
        encryption_key: 32-character encryption key for payload encryption
        secret_key: Your API secret key (PA_TEST for test, PA_LIVE for live)
        base_url: PayAgency API base URL (optional, defaults to https://backend.pay.agency)
        timeout: Request timeout in seconds (default: 15)
    """
    
    def __init__(
        self,
        encryption_key: str,
        secret_key: str,
        base_url: Optional[str] = None,
        timeout: int = 15
    ):
        # Validate configuration
        validate_config(encryption_key, secret_key)
        
        self.encryption_key = encryption_key
        self.secret_key = secret_key
        self.environment = get_environment(secret_key)
        self.timeout = timeout
        
        # Set base URL
        if base_url is None:
            self.base_url = "https://backend.pay.agency"
        else:
            self.base_url = normalize_base_url(base_url)
        
        # Configure session
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {secret_key}",
        })
        self.session.timeout = timeout
        
        # Initialize API modules
        self._payment = Payment(self)
        self._payout = Payout(self)
        self._payment_link = PaymentLink(self)
        self._crypto = Crypto(self)
        self._txn = Transaction(self)
        self._refund = Refund(self)
    
    @property
    def payment(self) -> Payment:
        """Payment operations"""
        return self._payment
    
    @property
    def payout(self) -> Payout:
        """Payout operations"""
        return self._payout
    
    @property
    def payment_link(self) -> PaymentLink:
        """Payment link operations"""
        return self._payment_link
    
    @property
    def crypto(self) -> Crypto:
        """Cryptocurrency operations"""
        return self._crypto
    
    @property
    def txn(self) -> Transaction:
        """Transaction operations"""
        return self._txn
    
    def refund(self, data: RefundInput) -> RefundResponse:
        """
        Process a refund
        
        Args:
            data: Refund data
            
        Returns:
            Refund response
        """
        return self._refund.create(data)
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        skip_encryption: bool = False
    ) -> Dict[str, Any]:
        """
        Make a request to the PayAgency API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            skip_encryption: Whether to skip encryption
            
        Returns:
            Response data
            
        Raises:
            PayAgencyAPIError: For API errors
            PayAgencyNetworkError: For network errors
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request data
        if data is not None:
            request_data = prepare_request_data(data, self.encryption_key, skip_encryption)
        else:
            request_data = None
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=request_data,
                params=params
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text or "Unknown error"}
                
                raise PayAgencyAPIError(
                    message=error_data.get("message", f"HTTP {response.status_code} error"),
                    status_code=response.status_code,
                    response=error_data
                )
            
            # Parse response
            try:
                return response.json()
            except ValueError:
                raise PayAgencyAPIError(
                    message="Invalid JSON response from server",
                    status_code=response.status_code,
                    response={"raw_response": response.text}
                )
                
        except requests.RequestException as e:
            raise PayAgencyNetworkError(
                message=f"Network error: {str(e)}",
                status_code=None,
                response=None
            )
