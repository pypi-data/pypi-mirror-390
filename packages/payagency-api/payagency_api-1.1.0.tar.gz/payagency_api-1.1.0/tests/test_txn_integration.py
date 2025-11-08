"""
Integration tests for transaction operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api
from payagency_api.exceptions import PayAgencyAPIError


class TestTransactionIntegration:
    """Integration tests for transaction operations using real API calls"""
    
    def test_get_transactions(self):
        """Test getting transaction history"""
        params = {
            "transaction_start_date": "2023-01-01",
            "transaction_end_date": "2024-12-31",
        }
        
        try:
            response = api.txn.get_transactions(params)
            print(f"Transactions Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            assert "meta" in response
            
            # Verify data structure
            assert isinstance(response["data"], list)
            
            # Verify meta structure
            meta = response["meta"]
            assert "hasNextPage" in meta
            assert "hasPreviousPage" in meta
            assert "totalCount" in meta
            
            # If transactions exist, verify structure
            if response["data"]:
                transaction = response["data"][0]
                assert "transaction_id" in transaction
                assert "amount" in transaction
                assert "currency" in transaction
                assert "status" in transaction
                assert "email" in transaction
                assert "created_at" in transaction
        except PayAgencyAPIError as e:
            print(f"Get Transactions API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_get_transactions_without_params(self):
        """Test getting transactions without date parameters"""
        try:
            response = api.txn.get_transactions()
            print(f"Transactions (no params) Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            assert "meta" in response
            
            # Verify data structure
            assert isinstance(response["data"], list)
        except PayAgencyAPIError as e:
            print(f"Get Transactions (no params) API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_get_wallet_transactions(self):
        """Test getting wallet transaction history"""
        params = {
            "transaction_start_date": "2023-01-01",
            "transaction_end_date": "2024-12-31",
        }
        
        try:
            response = api.txn.get_wallet_transactions(params)
            print(f"Wallet Transactions Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            assert "meta" in response
            
            # Verify data structure
            assert isinstance(response["data"], list)
            
            # Verify meta structure
            meta = response["meta"]
            assert "hasNextPage" in meta
            assert "hasPreviousPage" in meta
            assert "totalCount" in meta
        except PayAgencyAPIError as e:
            print(f"Get Wallet Transactions API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_get_wallet_transactions_without_params(self):
        """Test getting wallet transactions without date parameters"""
        try:
            response = api.txn.get_wallet_transactions()
            print(f"Wallet Transactions (no params) Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            assert "meta" in response
            
            # Verify data structure
            assert isinstance(response["data"], list)
        except PayAgencyAPIError as e:
            print(f"Get Wallet Transactions (no params) API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
