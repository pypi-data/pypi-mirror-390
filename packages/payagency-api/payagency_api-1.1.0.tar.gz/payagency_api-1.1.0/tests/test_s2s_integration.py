"""
Integration tests for S2S payment operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api


class TestS2SPaymentIntegration:
    """Integration tests for S2S payments using real API calls"""
    
    def test_create_s2s_payment(self):
        """Test creating a real S2S payment"""
        payload = {
            "first_name": "James",
            "last_name": "Dean",
            "email": "james@gmail.com",
            "address": "64 Hertingfordbury Rd",
            "country": "GB",
            "city": "Newport",
            "state": "GB",
            "zip": "TF10 8DF",
            "ip_address": "127.0.0.1",
            "phone_number": "7654233212",
            "amount": 100,
            "currency": "GBP",
            "card_number": "4111111111111111",
            "card_expiry_month": "12",
            "card_expiry_year": "2027",
            "card_cvv": "029",
            "redirect_url": "https://pay.agency",
            "webhook_url": "https://pay.agency/webhook",
            "terminal_id": "T12345",
        }
        
        response = api.payment.s2s(payload)
        print(f"S2S Payment API Response: {response}")
        
        # Verify response structure
        assert "status" in response
        assert "message" in response
        
        # The response should have one of the expected statuses
        assert response["status"] in ["SUCCESS", "REDIRECT", "FAILED", "PENDING"]
        
        # If successful, should have transaction data
        if response["status"] in ["SUCCESS", "REDIRECT"]:
            assert "data" in response
            if "data" in response:
                assert "transaction_id" in response["data"]
