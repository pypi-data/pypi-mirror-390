"""
Payment operations module
"""

from typing import TYPE_CHECKING

from ..types.payment import S2SInput, HostedInput, APMInput, PaymentResponse

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class Payment:
    """Payment operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def s2s(self, data: S2SInput) -> PaymentResponse:
        """
        Server-to-Server card payment
        
        Args:
            data: S2S payment data
            
        Returns:
            Payment response
        """
        endpoints = {
            "test": "/api/v1/test/card",
            "live": "/api/v1/live/card",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
    
    def hosted(self, data: HostedInput) -> PaymentResponse:
        """
        Hosted payment
        
        Args:
            data: Hosted payment data
            
        Returns:
            Payment response
        """
        endpoints = {
            "test": "/api/v1/test/hosted/card",
            "live": "/api/v1/live/hosted/card",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
    
    def apm(self, data: APMInput) -> PaymentResponse:
        """
        Alternative Payment Method
        
        Args:
            data: APM payment data
            
        Returns:
            Payment response
        """
        endpoints = {
            "test": "/api/v1/test/apm",
            "live": "/api/v1/live/apm",  
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
