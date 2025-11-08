"""
Transaction operations module
"""

from typing import TYPE_CHECKING

from ..types.transaction import TransactionsInput, TransactionsResponse

if TYPE_CHECKING:
    from ..client import PayAgencyApi


class Transaction:
    """Transaction operations"""
    
    def __init__(self, client: "PayAgencyApi"):
        self.client = client
    
    def get_transactions(self, data: TransactionsInput = None) -> TransactionsResponse:
        """
        Get transaction history
        
        Args:
            data: Transaction query parameters (optional)
            
        Returns:
            Transactions response
        """
        endpoints = {
            "test": "/api/v1/test-transactions",
            "live": "/api/v1/live-transactions",
        }
        
        endpoint = endpoints[self.client.environment]
        
        if data:
            # Convert to query parameters
            params = {k: v for k, v in data.items() if v is not None}
            return self.client.make_request("GET", endpoint, params=params)
        else:
            return self.client.make_request("GET", endpoint)
    
    def get_wallet_transactions(self, data: TransactionsInput = None) -> TransactionsResponse:
        """
        Get wallet transaction history
        
        Args:
            data: Transaction query parameters (optional)
            
        Returns:
            Transactions response
        """
        endpoints = {
            "test": "/api/v1/test-wallet-transactions",
            "live": "/api/v1/live-wallet-transactions",
        }
        
        endpoint = endpoints[self.client.environment]
        
        if data:
            # Convert to query parameters
            params = {k: v for k, v in data.items() if v is not None}
            return self.client.make_request("GET", endpoint, params=params)
        else:
            return self.client.make_request("GET", endpoint)
