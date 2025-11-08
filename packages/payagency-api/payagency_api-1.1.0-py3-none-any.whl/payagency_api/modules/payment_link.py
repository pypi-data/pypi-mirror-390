"""
Payment Link operations module
"""

from typing import TYPE_CHECKING

from ..types.payment_link import (
    PaymentLinkCreateInput,
    PaymentLinkResponse,
    PaymentTemplatesResponse,
)

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class PaymentLink:
    """Payment Link operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def create(self, data: PaymentLinkCreateInput) -> PaymentLinkResponse:
        """
        Create a payment link
        
        Args:
            data: Payment link creation data
            
        Returns:
            Payment link response
        """
        endpoints = {
            "test": "/api/v1/payment-link",
            "live": "/api/v1/payment-link",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data, skip_encryption=True)
    
    def get_templates(self) -> PaymentTemplatesResponse:
        """
        Get payment templates
        
        Returns:
            Payment templates response
        """
        # For test environment, return empty data array without making API call
        if self.client.environment == "test":
            return {"data": []}
            
        endpoints = {
            "test": "/api/v1/payment-templates",
            "live": "/api/v1/payment-templates",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("GET", endpoint, skip_encryption=True)
