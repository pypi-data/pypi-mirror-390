"""
Cryptocurrency operations module
"""

from typing import TYPE_CHECKING

from ..types.crypto import (
    CryptoPaymentInput,
    CryptoPaymentResponse,
    CryptoPaymentLinkInput,
    CryptoOnRampInput,
    CryptoOffRampInput,
    CryptoPayinInput,
    CryptoPayinResponse,
    CryptoCurrenciesInput,
    CryptoCurrenciesResponse,
    CryptoOnRampLinkInput,
    CryptoOffRampLinkInput,
    CryptoPayinLinkInput,
)
from ..types.payment_link import PaymentLinkResponse

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class Crypto:
    """Cryptocurrency operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def payment(self, data: CryptoPaymentInput) -> CryptoPaymentResponse:
        """
        Full crypto payment method - handles both OnRamp and OffRamp based on transaction_type
        
        Args:
            data: Crypto payment data
            
        Returns:
            Crypto payment response
        """
        endpoints = {
            "test": "/api/v1/test/crypto",
            "live": "/api/v1/live/crypto",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
    
    def payment_link(self, data: CryptoPaymentLinkInput) -> PaymentLinkResponse:
        """
        Full crypto payment link method - handles OnRamp, OffRamp, and PayIn based on transaction_type
        
        Args:
            data: Crypto payment link data
            
        Returns:
            Payment link response
        """
        endpoints = {
            "test": "/api/v1/crypto/payment-link",
            "live": "/api/v1/crypto/payment-link",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data, skip_encryption=True)
    
    def on_ramp(self, data: CryptoOnRampInput) -> CryptoPaymentResponse:
        """
        OnRamp (Fiat to Crypto) transaction
        
        Args:
            data: OnRamp data
            
        Returns:
            Crypto payment response
        """
        # Add transaction_type to the data
        full_data = {**data, "transaction_type": "ONRAMP"}
        return self.payment(full_data)
    
    def off_ramp(self, data: CryptoOffRampInput) -> CryptoPaymentResponse:
        """
        OffRamp (Crypto to Fiat) transaction
        
        Args:
            data: OffRamp data
            
        Returns:
            Crypto payment response
        """
        # Add transaction_type to the data
        full_data = {**data, "transaction_type": "OFFRAMP"}
        return self.payment(full_data)
    
    def on_ramp_link(self, data: CryptoOnRampLinkInput) -> PaymentLinkResponse:
        """
        Create OnRamp payment link
        
        Args:
            data: OnRamp link data
            
        Returns:
            Payment link response
        """
        # Add transaction_type to the data
        full_data = {**data, "transaction_type": "ONRAMP"}
        return self.payment_link(full_data)
    
    def off_ramp_link(self, data: CryptoOffRampLinkInput) -> PaymentLinkResponse:
        """
        Create OffRamp payment link
        
        Args:
            data: OffRamp link data
            
        Returns:
            Payment link response
        """
        # Add transaction_type to the data
        full_data = {**data, "transaction_type": "OFFRAMP"}
        return self.payment_link(full_data)
    
    def payin(self, data: CryptoPayinInput) -> CryptoPayinResponse:
        """
        Direct crypto payin
        
        Args:
            data: PayIn data
            
        Returns:
            Crypto PayIn response
        """
        endpoints = {
            "test": "/api/v1/test/crypto/payin",
            "live": "/api/v1/live/crypto/payin",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
    
    def payin_link(self, data: CryptoPayinLinkInput) -> PaymentLinkResponse:
        """
        Create PayIn link
        
        Args:
            data: PayIn link data
            
        Returns:
            Payment link response
        """
        # Add transaction_type to the data
        full_data = {**data, "transaction_type": "PAYIN"}
        return self.payment_link(full_data)
    
    def get_currencies(self, data: CryptoCurrenciesInput) -> CryptoCurrenciesResponse:
        """
        Get supported currencies for crypto exchange
        
        Args:
            data: Currency query data
            
        Returns:
            Supported currencies response
        """
        endpoints = {
            "test": "/api/v1/test/crypto/currencies",
            "live": "/api/v1/live/crypto/currencies",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data, skip_encryption=True)
