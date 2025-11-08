"""
Payout operations module
"""

from typing import TYPE_CHECKING

from ..types.payout import (
    PayoutInput,
    PayoutResponse,
    WalletsResponse,
    EstimateFeeInput,
    EstimateFeeResponse,
    PayoutStatusResponse,
)

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class Payout:
    """Payout operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def create_payout(self, data: PayoutInput) -> PayoutResponse:
        """
        Create a payout
        
        Args:
            data: Payout data
            
        Returns:
            Payout response
        """
        endpoints = {
            "test": "/api/v1/test/payout",
            "live": "/api/v1/live/payout",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data)
    
    def get_wallets(self) -> WalletsResponse:
        """
        Get all wallets
        
        Returns:
            Wallets response
        """
        if self.client.environment == "test":
            # Return mock data for test environment
            return {
                "data": [
                    {
                        "wallet_id": "WAL7825818519632620",
                        "currency": "USD",
                        "amount": 2000,
                        "payment_method": "Card",
                        "status": "Active",
                    },
                    {
                        "wallet_id": "WAL9876543210123456",  
                        "currency": "EUR",
                        "amount": 1500,
                        "payment_method": "Card",
                        "status": "Active",
                    },
                ]
            }
        
        endpoints = {
            "test": "/api/v1/wallet",
            "live": "/api/v1/wallet",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("GET", endpoint)
    
    def estimate_fee(self, data: EstimateFeeInput) -> EstimateFeeResponse:
        """
        Estimate payout fee
        
        Args:
            data: Fee estimation data
            
        Returns:
            Fee estimation response
        """
        if self.client.environment == "test":
            # Return mock data for test environment
            return {
                "data": {
                    "amount_required": data["amount"],
                    "wallet_balance": 2000,
                    "total_fee": int(data["amount"] * 0.03),  # 3% fee
                }
            }
        
        endpoints = {
            "test": "/api/v1/wallet/estimate-payout",
            "live": "/api/v1/wallet/estimate-payout",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("POST", endpoint, data,skip_encryption=True)
    
    def get_payout_status(self, payout_reference: str) -> PayoutStatusResponse:
        """
        Get payout status
        
        Args:
            payout_reference: Payout reference ID
            
        Returns:
            Payout status response
        """
        endpoints = {
            "test": f"/api/v1/test/payout/{payout_reference}/status",
            "live": f"/api/v1/live/payout/{payout_reference}/status",
        }
        
        endpoint = endpoints[self.client.environment]
        return self.client.make_request("GET", endpoint)
