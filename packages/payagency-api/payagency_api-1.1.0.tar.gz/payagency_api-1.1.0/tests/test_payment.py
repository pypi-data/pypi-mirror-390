"""
Unit tests for payment operations (mocked)
"""

import pytest
from unittest.mock import patch

from payagency_api.modules.payment import Payment


class TestPaymentMocked:
    """Test payment operations"""
    
    @patch('payagency_api.client.PayAgencyApi.make_request')
    def test_s2s_payment_test_env(self, mock_request, mock_client, sample_payment_data):
        """Test S2S payment in test environment"""
        mock_response = {
            "status": "SUCCESS",
            "message": "Payment successful",
            "data": {
                "transaction_id": "TXN_123",
                "amount": 100,
                "currency": "USD"
            }
        }
        mock_request.return_value = mock_response
        
        payment = Payment(mock_client)
        result = payment.s2s(sample_payment_data)
        
        assert result == mock_response
        mock_request.assert_called_once_with("POST", "/api/v1/test/card", sample_payment_data)
    
    @patch('payagency_api.client.PayAgencyApi.make_request')
    def test_hosted_payment_test_env(self, mock_request, mock_client, sample_payment_data):
        """Test hosted payment in test environment"""
        mock_response = {
            "status": "REDIRECT",
            "message": "Redirect to payment page",
            "redirect_url": "https://pay.agency/checkout/123"
        }
        mock_request.return_value = mock_response
        
        # Remove card fields for hosted payment
        hosted_data = {k: v for k, v in sample_payment_data.items() 
                      if k not in ["card_number", "card_expiry_month", "card_expiry_year", "card_cvv"]}
        
        payment = Payment(mock_client)
        result = payment.hosted(hosted_data)
        
        assert result == mock_response
        mock_request.assert_called_once_with("POST", "/api/v1/test/hosted/card", hosted_data)
    
    @patch('payagency_api.client.PayAgencyApi.make_request')
    def test_apm_payment_test_env(self, mock_request, mock_client, sample_payment_data):
        """Test APM payment in test environment"""
        mock_response = {
            "status": "REDIRECT", 
            "message": "Redirect to APM provider",
            "redirect_url": "https://apm-provider.com/pay/123"
        }
        mock_request.return_value = mock_response
        
        # Remove card fields for APM payment
        apm_data = {k: v for k, v in sample_payment_data.items() 
                   if k not in ["card_number", "card_expiry_month", "card_expiry_year", "card_cvv"]}
        
        payment = Payment(mock_client)
        result = payment.apm(apm_data)
        
        assert result == mock_response
        mock_request.assert_called_once_with("POST", "/api/v1/test/apm", apm_data)
    
    def test_s2s_payment_live_env(self, mock_client, sample_payment_data):
        """Test S2S payment endpoint selection for live environment"""
        # Change to live environment
        mock_client.environment = "live"
        
        with patch.object(mock_client, 'make_request') as mock_request:
            mock_request.return_value = {"status": "SUCCESS"}
            
            payment = Payment(mock_client)
            payment.s2s(sample_payment_data)
            
            mock_request.assert_called_once_with("POST", "/api/v1/live/card", sample_payment_data)
