"""
Integration tests for APM payment operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api


class TestAPMPaymentIntegration:
    """Integration tests for APM payments using real API calls"""
    
    def test_create_apm_payment(self):
        """Test creating a real APM payment"""
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
            "redirect_url": "https://pay.agency",
            "webhook_url": "https://pay.agency/webhook",
            "terminal_id": "T12345",
        }
        
        response = api.payment.apm(payload)
        print(f"APM Payment API Response: {response}")
        
        # Verify response structure
        assert "status" in response
        assert "message" in response
        
        # The response should have one of the expected statuses
        assert response["status"] in ["SUCCESS", "REDIRECT", "FAILED", "PENDING"]
        
        # For APM payments, usually expect REDIRECT status
        if response["status"] == "REDIRECT":
            assert "redirect_url" in response
            assert response["redirect_url"].startswith("http")
        
        # If successful, should have transaction data
        if response["status"] in ["SUCCESS", "REDIRECT"]:
            assert "data" in response
            if "data" in response:
                assert "transaction_id" in response["data"]
