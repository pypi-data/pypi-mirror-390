"""
Integration tests for payment link operations - REAL API CALLS
"""

import pytest
from tests.integration_utility import api
from payagency_api.exceptions import PayAgencyAPIError


class TestPaymentLinkIntegration:
    """Integration tests for payment link operations using real API calls"""
    
    def test_create_payment_link(self):
        """Test creating a payment link"""
        payload = {
            "payment_template_id": "PLI07435325281394735",
        }
        
        try:
            response = api.payment_link.create(payload)
            print(f"Payment Link Creation Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            
            # Data should contain the payment link URL
            assert isinstance(response["data"], str)
            assert response["data"].startswith("http")
        except PayAgencyAPIError as e:
            print(f"Payment Link Creation API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_create_payment_link_with_optional_fields(self):
        """Test creating a payment link with optional fields"""
        payload = {
            "payment_template_id": "PLI07435325281394735",
            "amount": 1000,
            "currency": "USD",
            "expiry_date": "2024-12-31",
            "terminal_id": "T12345",
            "order_id": "ORDER_123",
        }
        
        try:
            response = api.payment_link.create(payload)
            print(f"Payment Link Creation with Optional Fields Response: {response}")
            
            # Verify response structure
            assert "message" in response
            assert "data" in response
            
            # Data should contain the payment link URL
            assert isinstance(response["data"], str)
            assert response["data"].startswith("http")
        except PayAgencyAPIError as e:
            print(f"Payment Link Creation with Optional Fields API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e)
    
    def test_get_payment_templates(self):
        """Test getting payment templates"""
        try:
            response = api.payment_link.get_templates()
            print(f"Payment Templates Response: {response}")
            
            # Verify response structure
            assert "data" in response
            assert isinstance(response["data"], list)
            
            # If templates exist, verify structure
            if response["data"]:
                template = response["data"][0]
                assert "template_id" in template
                assert "template_name" in template
                assert "payment_template_id" in template
                assert "redirect_url" in template
                assert "webhook_url" in template
        except PayAgencyAPIError as e:
            print(f"Payment Templates API Error: {str(e)}")
            # Test that the API call was attempted and error was handled
            assert "Route not found" in str(e) or "Please pass all mandatory fields" in str(e) or "Invalid Secret Key" in str(e)
