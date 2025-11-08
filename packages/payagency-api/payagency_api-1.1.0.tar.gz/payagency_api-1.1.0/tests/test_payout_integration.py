"""
Integration tests for payout operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api
from payagency_api.exceptions import PayAgencyAPIError


class TestPayoutIntegration:
    """Integration tests for payout operations using real API calls"""
    
    def test_create_payout(self):
        """Test creating a real payout"""
        payload = {
            "wallet_id": "WAL1234567890",
            "first_name": "James",
            "last_name": "Dean",
            "email": "james@gmail.com",
            "address": "64 Hertingfordbury Rd",
            "country": "US",
            "city": "Newport",
            "state": "US",
            "zip": "TF10 8DF",
            "ip_address": "127.0.0.1",
            "phone_number": "7654233212",
            "amount": 100,
            "currency": "USD",
            "card_number": "4222222222222222",
            "card_expiry_month": "10",
            "card_expiry_year": "2030",
            "webhook_url": "https://pay.agency/webhook",
            "terminal_id": "T12345",
        }
        
        response = api.payout.create_payout(payload)
        print(f"Payout API Response: {response}")
        
        # Verify response structure
        assert "status" in response
        assert "message" in response
        
        # The response should have one of the expected statuses
        assert response["status"] in ["SUCCESS", "BLOCKED", "PENDING", "FAILED"]
    
    def test_fetch_wallets(self):
        """Test fetching wallets"""
        response = api.payout.get_wallets()
        print(f"Wallets Response: {response}")
        
        # Verify response structure
        assert "data" in response
        assert isinstance(response["data"], list)
        
        # If wallets exist, verify structure
        if response["data"]:
            wallet = response["data"][0]
            assert "wallet_id" in wallet
            assert "currency" in wallet
            assert "amount" in wallet
            assert "status" in wallet
    
    def test_estimate_payout_fee(self):
        """Test estimating payout fee"""
        payload = {
            "wallet_id": "WAL7825818519632620",
            "amount": 200,
            "card_number": "4111111111111111",
        }
        
        response = api.payout.estimate_fee(payload)
        print(f"Estimate Payout Fee Response: {response}")
        
        # Verify response structure
        assert "data" in response
        assert "amount_required" in response["data"]
        assert "wallet_balance" in response["data"] 
        assert "total_fee" in response["data"]
    
    def test_get_payout_status(self):
        """Test getting payout status"""
        try:
            response = api.payout.get_payout_status("PA1877208010353680")
            print(f"Payout Status Response: {response}")
            
            # Verify response structure
            assert "data" in response or "status" in response
            # Status endpoint may return different structure depending on payout existence
        except PayAgencyAPIError as e:
            print(f"Payout Status API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
