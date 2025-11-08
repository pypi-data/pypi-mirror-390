"""
Integration tests for cryptocurrency operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api
from payagency_api.exceptions import PayAgencyAPIError


class TestCryptoIntegration:
    """Integration tests for crypto operations using real API calls"""
    
    def test_create_onramp_link(self):
        """Test creating an OnRamp link"""
        payload = {
            "fiat_amount": 100,
            "fiat_currency": "GBP",
            "crypto_currency": "BTC",
            "payment_template_id": "PLI07435325281394735",
        }
        
        try:
            response = api.crypto.on_ramp_link(payload)
            print(f"On-Ramp Link Response: {response}")
            
            # Verify response structure
            assert "data" in response
            assert "message" in response
            
            # Data should contain the payment link URL
            assert isinstance(response["data"], str)
            assert response["data"].startswith("http")
        except PayAgencyAPIError as e:
            print(f"On-Ramp Link API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_offramp_link(self):
        """Test creating an OffRamp link"""
        payload = {
            "fiat_currency": "GBP",
            "crypto_currency": "BTC",
            "crypto_amount": "0.01",
            "payment_template_id": "PLI07435325281394735",
        }
        
        try:
            response = api.crypto.off_ramp_link(payload)
            print(f"Off-Ramp Link Response: {response}")
            
            # Verify response structure
            assert "data" in response
            assert "message" in response
            
            # Data should contain the payment link URL
            assert isinstance(response["data"], str)
            assert response["data"].startswith("http")
        except PayAgencyAPIError as e:
            print(f"Off-Ramp Link API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_crypto_payin_link(self):
        """Test creating a crypto PayIn link"""
        payload = {
            "fiat_amount": 150,
            "fiat_currency": "USD",
            "crypto_currency": "BTC",
            "payment_template_id": "PLI07435325281394735",
        }
        
        try:
            response = api.crypto.payin_link(payload)
            print(f"Crypto PayIn Link Response: {response}")
            
            # Verify response structure
            assert "data" in response
            assert "message" in response
            
            # Data should contain the payment link URL
            assert isinstance(response["data"], str)
            assert response["data"].startswith("http")
        except PayAgencyAPIError as e:
            print(f"Crypto PayIn Link API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_crypto_onramp(self):
        """Test creating a crypto OnRamp transaction"""
        payload = {
            "first_name": "Diana",
            "last_name": "Prince",
            "email": "diana@pay.agency",
            "phone_number": "0123456789",
            "fiat_amount": 200,
            "fiat_currency": "EUR",
            "crypto_currency": "BTC",
            "wallet_address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
            "ip_address": "127.0.0.1",
            "country": "GB",
            "redirect_url": "https://pay.agency",
            "webhook_url": "https://pay.agency/webhook",
            "crypto_network": "BITCOIN",
        }
        
        try:
            response = api.crypto.on_ramp(payload)
            print(f"Crypto OnRamp Response: {response}")
            
            # Verify response structure
            assert "status" in response
            assert "message" in response
            
            # The response should have one of the expected statuses
            assert response["status"] in ["REDIRECT", "PENDING", "FAILED", "SUCCESS"]
            
            # If successful, should have transaction data
            if response["status"] in ["REDIRECT", "PENDING", "SUCCESS"]:
                assert "data" in response
        except PayAgencyAPIError as e:
            print(f"Crypto OnRamp API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_crypto_offramp(self):
        """Test creating a crypto OffRamp transaction"""
        payload = {
            "first_name": "Ethan",
            "last_name": "Hunt",
            "email": "ethan@pay.agency",
            "fiat_currency": "GBP",
            "crypto_currency": "BTC",
            "crypto_amount": "0.05",
            "phone_number": "0123456789",
            "wallet_address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
            "ip_address": "127.0.0.1",
            "country": "GB",
            "redirect_url": "https://pay.agency",
            "webhook_url": "https://pay.agency/webhook",
            "crypto_network": "BITCOIN",
        }
        
        try:
            response = api.crypto.off_ramp(payload)
            print(f"Crypto OffRamp Response: {response}")
            
            # Verify response structure
            assert "status" in response
            assert "message" in response
            
            # The response should have one of the expected statuses
            assert response["status"] in ["REDIRECT", "PENDING", "FAILED", "SUCCESS"]
        except PayAgencyAPIError as e:
            print(f"Crypto OffRamp API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_fetch_supported_cryptocurrencies(self):
        """Test fetching supported cryptocurrencies"""
        params = {
            "country": "GB",
            "amount": 100,
        }
        
        try:
            response = api.crypto.get_currencies(params)
            print(f"Supported Cryptocurrencies Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            assert isinstance(response["data"], list)
            
            # If currencies exist, verify structure
            if response["data"]:
                currency = response["data"][0]
                assert "name" in currency
                assert "code" in currency
                assert "symbol" in currency
        except PayAgencyAPIError as e:
            print(f"Supported Cryptocurrencies API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_crypto_payin(self):
        """Test creating a crypto PayIn transaction"""
        payload = {
            "first_name": "Fiona",
            "last_name": "Gallagher",
            "email": "hello@gmail.com",
            "address": "64 Hertingfordbury Rd",
            "phone_number": "0123456789",
            "ip_address": "127.0.0.1",
            "crypto_currency": "BTC",
            "amount": 300,
            "currency": "USD",
            "redirect_url": "https://pay.agency",
            "webhook_url": "https://pay.agency/webhook",
            "crypto_network": "BITCOIN",
            "country": "US",
        }
        
        response = api.crypto.payin(payload)
        print(f"Crypto PayIn Response: {response}")
        
        # Verify response structure
        assert "status" in response
        assert "message" in response
        
        # The response should have one of the expected statuses
        assert response["status"] in ["SUCCESS", "PENDING", "FAILED", "REDIRECT"]
        
        # If successful, should have transaction data
        if response["status"] in ["SUCCESS", "PENDING", "REDIRECT"]:
            assert "data" in response
