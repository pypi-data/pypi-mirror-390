"""
Refund operations module
"""

from typing import TYPE_CHECKING

from ..types.refund import RefundInput, RefundResponse

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class Refund:
    """Refund operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def create(self, data: RefundInput) -> RefundResponse:
        """
        Process a refund
        
        Args:
            data: Refund data
            
        Returns:
            Refund response
        """
        endpoints = {
            "test": "/api/v1/test/refund",
            "live": "/api/v1/live/refund",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data, skip_encryption=True)
