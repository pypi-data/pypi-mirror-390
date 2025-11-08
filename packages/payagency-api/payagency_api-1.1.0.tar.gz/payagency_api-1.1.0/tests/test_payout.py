"""
Unit tests for payout operations (mocked)
"""

import pytest
from unittest.mock import patch

from payagency_api.modules.payout import Payout


class TestPayoutMocked:
    """Test payout operations"""
    
    @patch('payagency_api.client.PayAgencyApi.make_request')
    def test_create_payout_test_env(self, mock_request, mock_client, sample_payout_data):
        """Test create payout in test environment"""
        mock_response = {
            "status": "SUCCESS",
            "message": "Payout successful",
            "data": {
                "transaction_id": "PAYOUT_123",
                "amount": 100,
                "currency": "USD"
            }
        }
        mock_request.return_value = mock_response
        
        payout = Payout(mock_client)
        result = payout.create_payout(sample_payout_data)
        
        assert result == mock_response
        mock_request.assert_called_once_with("POST", "/api/v1/test/payout", sample_payout_data)
    
    def test_get_wallets_test_env(self, mock_client):
        """Test get wallets in test environment (mock data)"""
        payout = Payout(mock_client)
        result = payout.get_wallets()
        
        assert "data" in result
        assert len(result["data"]) == 2
        assert result["data"][0]["wallet_id"] == "WAL7825818519632620"
        assert result["data"][0]["currency"] == "USD"
        assert result["data"][0]["status"] == "Active"
    
    def test_estimate_fee_test_env(self, mock_client):
        """Test estimate fee in test environment (mock data)"""
        fee_data = {
            "wallet_id": "WAL123456789",
            "amount": 200,
            "card_number": "4111111111111111"
        }
        
        payout = Payout(mock_client)
        result = payout.estimate_fee(fee_data)
        
        assert "data" in result
        assert result["data"]["amount_required"] == 200
        assert result["data"]["wallet_balance"] == 2000
        assert result["data"]["total_fee"] == 6  # 3% of 200
    
    @patch('payagency_api.client.PayAgencyApi.make_request')
    def test_get_payout_status(self, mock_request, mock_client):
        """Test get payout status"""
        mock_response = {
            "status": "SUCCESS",
            "message": "Payout completed",
            "data": {
                "transaction_id": "PAYOUT_123",
                "amount": 100,
                "currency": "USD"
            }
        }
        mock_request.return_value = mock_response
        
        payout = Payout(mock_client)
        result = payout.get_payout_status("PAYOUT_REF_123")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "GET", 
            "/api/v1/test/payout/status", 
            params={"payout_reference": "PAYOUT_REF_123"}
        )
    
    def test_create_payout_live_env(self, mock_client, sample_payout_data):
        """Test create payout endpoint selection for live environment"""
        # Change to live environment
        mock_client.environment = "live"
        
        with patch.object(mock_client, 'make_request') as mock_request:
            mock_request.return_value = {"status": "SUCCESS"}
            
            payout = Payout(mock_client)
            payout.create_payout(sample_payout_data)
            
            mock_request.assert_called_once_with("POST", "/api/v1/live/payout", sample_payout_data)
