"""
Tests for PayAgency API client
"""

import pytest
from unittest.mock import patch, Mock

from payagency_api import PayAgencyApi, PayAgencyError, PayAgencyAPIError
from payagency_api.utils import validate_config, get_environment, normalize_base_url


class TestPayAgencyApi:
    """Test PayAgency API client"""
    
    def test_init_valid_config(self):
        """Test initialization with valid configuration"""
        client = PayAgencyApi(
            encryption_key="12345678901234567890123456789012",
            secret_key="PA_TEST_test_key"
        )
        
        assert client.encryption_key == "12345678901234567890123456789012"
        assert client.secret_key == "PA_TEST_test_key"
        assert client.environment == "test"
        assert client.base_url == "https://backend.pay.agency"
    
    def test_init_invalid_encryption_key(self):
        """Test initialization with invalid encryption key"""
        with pytest.raises(ValueError, match="Encryption key must be exactly 32 characters"):
            PayAgencyApi(
                encryption_key="short_key",
                secret_key="PA_TEST_test_key"
            )
    
    def test_init_invalid_secret_key(self):
        """Test initialization with invalid secret key"""
        with pytest.raises(ValueError, match="Secret key must start with"):
            PayAgencyApi(
                encryption_key="12345678901234567890123456789012",
                secret_key="INVALID_key"
            )
    
    def test_init_custom_base_url(self):
        """Test initialization with custom base URL"""
        client = PayAgencyApi(
            encryption_key="12345678901234567890123456789012",
            secret_key="PA_TEST_test_key",
            base_url="https://custom.pay.agency"
        )
        
        assert client.base_url == "https://custom.pay.agency"
    
    def test_environment_detection_test(self):
        """Test test environment detection"""
        client = PayAgencyApi(
            encryption_key="12345678901234567890123456789012",
            secret_key="PA_TEST_test_key"
        )
        
        assert client.environment == "test"
    
    def test_environment_detection_live(self):
        """Test live environment detection"""
        client = PayAgencyApi(
            encryption_key="12345678901234567890123456789012",
            secret_key="PA_LIVE_live_key"
        )
        
        assert client.environment == "live"
    
    @patch('payagency_api.client.requests.Session.request')
    def test_make_request_success(self, mock_request, mock_client):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "SUCCESS"}
        mock_request.return_value = mock_response
        
        result = mock_client.make_request("POST", "/test", {"test": "data"})
        
        assert result == {"status": "SUCCESS"}
        mock_request.assert_called_once()
    
    @patch('payagency_api.client.requests.Session.request')
    def test_make_request_api_error(self, mock_request, mock_client):
        """Test API error handling"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        mock_request.return_value = mock_response
        
        with pytest.raises(PayAgencyAPIError) as exc_info:
            mock_client.make_request("POST", "/test", {"test": "data"})
        
        assert exc_info.value.status_code == 400
        assert "Bad request" in str(exc_info.value)


class TestUtils:
    """Test utility functions"""
    
    def test_validate_config_valid(self):
        """Test valid configuration validation"""
        # Should not raise any exception
        validate_config("12345678901234567890123456789012", "PA_TEST_key")
    
    def test_validate_config_invalid_encryption_key(self):
        """Test invalid encryption key validation"""
        with pytest.raises(ValueError, match="Encryption key must be exactly 32 characters"):
            validate_config("short", "PA_TEST_key")
    
    def test_validate_config_invalid_secret_key(self):
        """Test invalid secret key validation"""
        with pytest.raises(ValueError, match="Secret key must start with"):
            validate_config("12345678901234567890123456789012", "INVALID_key")
    
    def test_get_environment_test(self):
        """Test test environment detection"""
        assert get_environment("PA_TEST_key") == "test"
    
    def test_get_environment_live(self):
        """Test live environment detection"""
        assert get_environment("PA_LIVE_key") == "live"
    
    def test_normalize_base_url(self):
        """Test base URL normalization"""
        assert normalize_base_url("pay.agency") == "https://pay.agency"
        assert normalize_base_url("http://pay.agency") == "https://pay.agency"
        assert normalize_base_url("https://pay.agency/") == "https://pay.agency"
        assert normalize_base_url("https://pay.agency") == "https://pay.agency"
